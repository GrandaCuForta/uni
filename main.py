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
    print("\n1. Add Student")
    print("2. View Students")
    print("3. Delete Student")
    print("4. Exit Program")

    choice = input("Choose: ")

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
    
        for student in cursor.fetchall():
            print (student)

    elif choice == "3":
        student_id = input("Enter student ID: ")
        delete_student(student_id)

    elif choice == "4":
        break