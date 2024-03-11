# Databases and SQLite
# Create a program that allows a user to easily be able to make certain queries in the database.

# Examples in Database:

# Students:
# ('LM00100200306', 'Luffy', 'Monkey', 'pking@linegrand.com', 12),
# ('PA00100200307', 'Paul', 'Atreides', 'paul@melange.com', 13),

# Teachers
# ('MP001', 'Monty', 'Python', 'montypython@tim.com', 1),
# ('FG002', 'Frank', 'Google', 'frank@google.com', 2),

import sqlite3
import xml.etree.ElementTree as ET
import json

try:
    conn = sqlite3.connect("HyperionDev.db")
except sqlite3.Error:
    print("Please store your database as HyperionDev.db")
    quit()

cur = conn.cursor()

# - Functions -

# Checking if user inputs the correct argument with the menu
def usage_is_incorrect(input, num_args):
    if len(input) != num_args + 1:
        print(f"The {input[0]} command requires {num_args} arguments.")
        return True
    return False

# Function to save data as .json
def store_data_as_json(data, filename):
    with open(filename, 'w') as outfile:
        outfile = json.dump(data, outfile, sort_keys=True, indent=4)

# Function to save data as .XML
def store_data_as_xml(data, filename):
    root = ET.Element("data")

    for item in data:
        element = ET.SubElement(root, "item")
        for key, value in item.items():
            child_element = ET.SubElement(element, key)
            child_element.text = str(value)

    tree = ET.ElementTree(root)
    tree.write(filename, encoding="utf-8", xml_declaration=True)

# Asking user to store data in XML or json
def offer_to_store(data):
    while True:
        print("Would you like to store this result?")
        choice = input("Y/[N]? : ").strip().lower()

        if choice == "y":
            filename = input("Specify filename. Must end in .xml or .json: ")
            ext = filename.split(".")[-1]
            if ext == 'xml':
                store_data_as_xml(data, filename)
            elif ext == 'json':
                store_data_as_json(data, filename)
            else:
                print("Invalid file extension. Please use .xml or .json")

        elif choice == 'n':
            break

        else:
            print("Invalid choice")


# - Menu -

usage = '''
What would you like to do?

d - demo
vs <student_id>            - view subjects taken by a student
la <firstname> <surname>   - lookup address for a given firstname and surname
lr <student_id>            - list reviews for a given student_id
lc <teacher_id>            - list all courses taken by teacher_id
lnc                        - list all students who haven't completed their course
lf                         - list all students who have completed their course and achieved 30 or below
e                          - exit this program

Type your option here: '''

print("Welcome to the data querying app!")

while True:
    print()
    # Get input from user
    user_input = input(usage).strip().split(" ")

    print()

    # Parse user input into command and args
    command = user_input[0]
    if len(user_input) > 1:
        args = user_input[1:]


    # - Menu Options -

    # demo - a nice bit of code from me to you - this prints all student names and surnames :)
    if command == 'd': 
        data = cur.execute("SELECT * FROM Student")
        for _, firstname, surname, _, _ in data:
            print(f"{firstname} {surname}")


    # view subjects by student_id   
    elif command == 'vs': 
        if usage_is_incorrect(user_input, 1):
            continue
        student_id = args[0].strip()

        # Checking to see if the student Id exists in the database
        cur.execute("SELECT COUNT(*) FROM Student WHERE student_id = ?", (student_id,))
        if cur.fetchone()[0] == 0:
            print("Student ID does not exist in the database.")
        else:
            cur.execute(
                "SELECT Course.course_name "
                "FROM StudentCourse "
                "INNER JOIN Course "
                "ON StudentCourse.course_code = Course.course_code "
                "WHERE StudentCourse.student_id = ?", (student_id,)
            )

            data = []
            for row in cur.fetchall():
                data.append({"course_name": row[0]})

            if data: # check to see if the data is empty or not
                print("You are currently enrolled in the following subjects:\n")
                for subject in data:
                    print(subject["course_name"])
            else:
                print("You are not enrolled in any subjects")

            offer_to_store(data)


    # list address by name and surname
    elif command == 'la':
        if usage_is_incorrect(user_input, 2):
            continue
        firstname, surname = args[0], args[1]

        cur.execute(
            "SELECT street, city "
            "FROM Address "
            "INNER JOIN Student "
            "ON Student.address_id = Address.address_id "
            "WHERE Student.first_name = ? AND Student.last_name = ?", (firstname, surname)
        )

        data = []
        for row in cur.fetchall():
            data.append({"Street": row[0], "City": row[1]})

        if data:
            print(f"Student {firstname} {surname} lives at the address below:\n")
            for address in data:
                print(f"Street: {address['Street']}, City: {address['City']}")
        else:
            print("There is no address allocated to the student.")

        offer_to_store(data)

    
    # list reviews by student_id
    elif command == 'lr':
        if usage_is_incorrect(user_input, 1):
            continue
        student_id = args[0]

        cur.execute(
            "SELECT review_text, completeness, efficiency, style, documentation "
            "FROM Review "
            "WHERE student_id = ?", (student_id,)
        )

        data = []
        for row in cur.fetchall():
            data.append({
                "review_text": row[0],
                "completeness": row[1],
                "efficiency": row[2],
                "style": row[3],
                "documentation": row[4]
            })

        if data:
            print(f"Reviews for student {student_id}:")
            for review in data:
                print(f"""
Review Text:     {review["review_text"]}
Completeness:    {review["completeness"]}
Efficiency:      {review["efficiency"]}
Style:           {review["style"]}
Documentation:   {review["documentation"]}""")
        else:
            print("There are no reviews for the student.")

        offer_to_store(data)


    # List all courses being given by a specific teacher
    elif command == 'lc':
        if usage_is_incorrect(user_input, 1):
            continue
        teacher_id = args[0]

        cur.execute(
            "SELECT course_name "
            "FROM Course "
            "INNER JOIN Teacher "
            "ON Teacher.teacher_id = Course.teacher_id "
            "WHERE Course.teacher_id = ?", (teacher_id,)
        )

        data = []

        for row in cur.fetchall():
            data.append({"Course name": row[0]})

        if data:
            print(f"Teacher ID: {teacher_id} is teaching the below courses:\n")
            for course in data:
                print(f"Course: {course['Course name']}")
        else:
            print("There are no courses being taught by the teacher.")

        offer_to_store(data)


    # list all students who haven't completed their course
    elif command == 'lnc':

        cur.execute(
            "SELECT Student.student_id, Student.first_name, Student.last_name, Student.email, Course.course_name "
            "FROM Student "
            "INNER JOIN StudentCourse ON Student.student_id = StudentCourse.student_id "
            "INNER JOIN Course ON StudentCourse.course_code = Course.course_code "
            "WHERE StudentCourse.is_complete = 0"
        )

        data = []

        for row in cur.fetchall():
            data.append({"student_id": row[0], "first_name": row[1], "last_name": row[2], "email": row[3], "course_name": row[4]})

        
        for student_info in data:
            print(f"""
Student ID:  {student_info["student_id"]}
Name:        {student_info['first_name']} {student_info['last_name']}
Email:       {student_info["email"]}
Course Name: {student_info["course_name"]}""")

        offer_to_store(data)


    # list all students who have completed their course and got a mark <= 30
    elif command == 'lf':

        cur.execute(
            "SELECT Student.student_id, Student.first_name, Student.last_name, Student.email, Course.course_name, StudentCourse.mark "
            "FROM Student "
            "INNER JOIN StudentCourse ON Student.student_id = StudentCourse.student_id "
            "INNER JOIN Course ON StudentCourse.course_code = Course.course_code "
            "WHERE StudentCourse.is_complete = 1 AND StudentCourse.mark <= 30"
        )

        data = []
        
        for row in cur.fetchall():
            data.append({"student_id": row[0], "first_name": row[1], "last_name": row[2], "email": row[3], "course_name": row[4], "mark": row[5]})

        for student_info in data:
            print(f"""
Student ID:  {student_info["student_id"]}
Name:        {student_info['first_name']} {student_info['last_name']}
Email:       {student_info["email"]}
Course Name: {student_info["course_name"]}
Mark:        {student_info["mark"]}""")

        offer_to_store(data)

    # Exit 
    elif command == 'e':
        print("Programme exited successfully!")
        break
    
    else:
        print(f"Incorrect command: '{command}'")