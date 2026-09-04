import mysql.connector
from sqlalchemy import true
from config import *

connection = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

cursor = connection.cursor()


def delete_student(student_id):
    cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
    connection.commit()

    if cursor.rowcount == 0:
        print("Student not found.")
    else:
        print("Student deleted successfully!")


while true:
    print("\n" + "=" * 32)
    print("       STUDENT MANAGER")
    print("=" * 32)
    print("1. Add Student")
    print("2. View Students")
    print("3. Delete Student")
    print("4. Exit Program")
    print("=" * 32)

    choice = input("Choose an option: ")

    if choice == "1":
        name = input("Enter student name: ")
        email = input("Enter student email: ")
        age = input("Enter student age: ")

        sql = """
        INSERT INTO students (name, email, age) VALUES (%s, %s, %s) """

        cursor.execute(sql, (name, email, age))
        connection.commit()
        print("Student added successfully!")

    elif choice == "2":
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()

        print("\n" + "-" * 72)
        print("STUDENTS")
        print("-" * 72)

        if students:
            headers = [column[0].upper() for column in cursor.description]
            print(" | ".join(f"{header:<15}" for header in headers))
            print("-" * 72)
            for student in students:
                print(" | ".join(f"{str(value):<15}" for value in student))
        else:
            print("No students found.")

        print("-" * 72)

    elif choice == "3":
        student_id = input("Enter student ID: ")
        delete_student(student_id)

    elif choice == "4":
        print("Goodbye!")
        break