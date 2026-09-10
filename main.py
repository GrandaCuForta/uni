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


def update_student(student_id, name, email, age):
    cursor.execute("SELECT 1 FROM students WHERE id = %s", (student_id,))
    if cursor.fetchone() is None:
        print("Student not found.")
        return

    cursor.execute(
        "SELECT 1 FROM students WHERE email = %s AND id != %s LIMIT 1",
        (email, student_id),
    )
    if cursor.fetchone() is not None:
        print("This email is already registered.")
        return

    cursor.execute(
        "UPDATE students SET name = %s, email = %s, age = %s WHERE id = %s",
        (name, email, age, student_id),
    )
    connection.commit()
    print("Student updated successfully!")


while true:
    print("\n" + "=" * 32)
    print("       STUDENT MANAGER")
    print("=" * 32)
    print("1. Add Student")
    print("2. View Students")
    print("3. Delete Student")
    print("4. Update Student")
    print("5. Exit Program")
    print("=" * 32)

    choice = input("Choose an option: ")

    if choice == "1":
        while True:
            name = input("Enter student name: ").strip()
            if name:
                break
            print("Name cannot be empty. Please try again.")

        while True:
            email = input("Enter student email: ").strip()
            if "@" not in email:
                print("Email must contain @. Please try again.")
                continue

            cursor.execute("SELECT 1 FROM students WHERE email = %s LIMIT 1", (email,))
            if cursor.fetchone() is not None:
                print("This email is already registered. Please try again.")
                continue
            break

        while True:
            age = input("Enter student age: ")
            try:
                age = int(age)
                if 0 <= age <= 120:
                    break
                print("Age must be between 0 and 120. Please try again.")
            except ValueError:
                print("Age must contain numbers only. Please try again.")

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
        confirmation = input("Are you sure you want to delete this student? (y/n): ")
        if confirmation.lower() in ("y", "yes"):
            delete_student(student_id)
        else:
            print("Deletion cancelled.")

    elif choice == "4":
        student_id = input("Enter student ID: ")

        while True:
            name = input("Enter new student name: ").strip()
            if name:
                break
            print("Name cannot be empty. Please try again.")

        while True:
            email = input("Enter new student email: ").strip()
            if "@" not in email:
                print("Email must contain @. Please try again.")
                continue

            cursor.execute(
                "SELECT 1 FROM students WHERE email = %s AND id != %s LIMIT 1",
                (email, student_id),
            )
            if cursor.fetchone() is not None:
                print("This email is already registered. Please try again.")
                continue
            break

        while True:
            age = input("Enter new student age: ")
            try:
                age = int(age)
                if 0 <= age <= 120:
                    break
                print("Age must be between 0 and 120. Please try again.")
            except ValueError:
                print("Age must contain numbers only. Please try again.")

        update_student(student_id, name, email, age)

    elif choice == "5":
        print("Goodbye!")
        break