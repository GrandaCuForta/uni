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

while true:
    print("\n1. Add Student")
    print("2. View Students")
    print("3. Exit")

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
        break