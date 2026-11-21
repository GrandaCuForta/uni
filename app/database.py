from dataclasses import dataclass
from datetime import date

import mysql.connector

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER


@dataclass(frozen=True)
class Student:
    id: int
    name: str
    email: str
    date_of_birth: date
    study_program: str
    phone: str
    enrollment_date: date


class StudentRepository:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
        )

    def close(self):
        if self.connection.is_connected():
            self.connection.close()

    def count(self, search=""):
        cursor = self.connection.cursor()
        try:
            pattern = f"%{search.strip()}%"
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM students
                WHERE name LIKE %s
                   OR email LIKE %s
                   OR study_program LIKE %s
                   OR phone LIKE %s
                """,
                (pattern, pattern, pattern, pattern),
            )
            return cursor.fetchone()[0]
        finally:
            cursor.close()

    def list_students(self, search="", sort_column="name", descending=False, offset=0, limit=10):
        allowed_sort_columns = {
            "id": "id",
            "name": "name",
            "email": "email",
            "date_of_birth": "date_of_birth",
            "study_program": "study_program",
            "phone": "phone",
            "enrollment_date": "enrollment_date",
        }
        order_by = allowed_sort_columns.get(sort_column, "name")
        direction = "DESC" if descending else "ASC"
        pattern = f"%{search.strip()}%"
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                f"""
                SELECT id, name, email, date_of_birth, study_program, phone, enrollment_date
                FROM students
                WHERE name LIKE %s
                   OR email LIKE %s
                   OR study_program LIKE %s
                   OR phone LIKE %s
                ORDER BY {order_by} {direction}
                LIMIT %s OFFSET %s
                """,
                (pattern, pattern, pattern, pattern, limit, offset),
            )
            return [Student(*row) for row in cursor.fetchall()]
        finally:
            cursor.close()

    def get(self, student_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                SELECT id, name, email, date_of_birth, study_program, phone, enrollment_date
                FROM students
                WHERE id = %s
                """,
                (student_id,),
            )
            row = cursor.fetchone()
            return Student(*row) if row else None
        finally:
            cursor.close()

    def create(self, name, email, date_of_birth, study_program, phone, enrollment_date):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO students
                    (name, email, date_of_birth, study_program, phone, enrollment_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (name, email, date_of_birth, study_program, phone, enrollment_date),
            )
            self.connection.commit()
            return cursor.lastrowid
        except mysql.connector.Error:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def update(self, student_id, name, email, date_of_birth, study_program, phone, enrollment_date):
        cursor = self.connection.cursor()
        try:
            cursor.execute(
                """
                UPDATE students
                SET name = %s, email = %s, date_of_birth = %s,
                    study_program = %s, phone = %s, enrollment_date = %s
                WHERE id = %s
                """,
                (
                    name,
                    email,
                    date_of_birth,
                    study_program,
                    phone,
                    enrollment_date,
                    student_id,
                ),
            )
            self.connection.commit()
        except mysql.connector.Error:
            self.connection.rollback()
            raise
        finally:
            cursor.close()

    def delete(self, student_id):
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
            self.connection.commit()
        except mysql.connector.Error:
            self.connection.rollback()
            raise
        finally:
            cursor.close()
