import os
import sys
import unittest
import uuid
from datetime import date
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import StudentRepository


load_dotenv(".env")


@unittest.skipUnless(
    os.getenv("RUN_DB_TESTS") == "1",
    "Set RUN_DB_TESTS=1 to run MySQL integration tests.",
)
class StudentRepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repository = StudentRepository()
        cursor = cls.repository.connection.cursor()
        try:
            cursor.execute("SHOW COLUMNS FROM students")
            columns = {row[0] for row in cursor.fetchall()}
        finally:
            cursor.close()

        expected_columns = {
            "id",
            "name",
            "email",
            "date_of_birth",
            "study_program",
            "phone",
            "enrollment_date",
        }
        missing_columns = expected_columns - columns
        if missing_columns:
            cls.repository.close()
            raise AssertionError(
                "The test database is not migrated. Missing columns: "
                + ", ".join(sorted(missing_columns))
            )

    @classmethod
    def tearDownClass(cls):
        cls.repository.close()

    def setUp(self):
        suffix = uuid.uuid4().hex[:8]
        self.email = f"test_{suffix}@example.com"
        self.updated_email = f"updated_{suffix}@example.com"
        self.student_data = {
            "name": "Test Student",
            "email": self.email,
            "date_of_birth": date(2000, 1, 15),
            "study_program": "Computer Science",
            "phone": "+37120000000",
            "enrollment_date": date(2026, 9, 1),
        }

    def tearDown(self):
        cursor = self.repository.connection.cursor()
        try:
            cursor.execute(
                "DELETE FROM students WHERE email IN (%s, %s)",
                (self.email, self.updated_email),
            )
            self.repository.connection.commit()
        finally:
            cursor.close()

    def _create_student(self):
        return self.repository.create(**self.student_data)

    def test_create_and_read_student(self):
        student_id = self._create_student()

        student = self.repository.get(student_id)

        self.assertIsNotNone(student)
        self.assertEqual(student.name, "Test Student")
        self.assertEqual(student.email, self.email)
        self.assertEqual(student.date_of_birth, date(2000, 1, 15))
        self.assertEqual(student.study_program, "Computer Science")
        self.assertEqual(student.phone, "+37120000000")
        self.assertEqual(student.enrollment_date, date(2026, 9, 1))

    def test_update_student(self):
        student_id = self._create_student()

        self.repository.update(
            student_id,
            "Updated Student",
            self.updated_email,
            date(2001, 2, 16),
            "Software Engineering",
            "+37121111111",
            date(2026, 9, 2),
        )
        student = self.repository.get(student_id)

        self.assertEqual(student.name, "Updated Student")
        self.assertEqual(student.email, self.updated_email)
        self.assertEqual(student.study_program, "Software Engineering")
        self.assertEqual(student.phone, "+37121111111")

    def test_duplicate_email_is_rejected(self):
        self._create_student()

        with self.assertRaises(mysql.connector.IntegrityError):
            self.repository.create(
                "Duplicate Student",
                self.email,
                self.student_data["date_of_birth"],
                self.student_data["study_program"],
                self.student_data["phone"],
                self.student_data["enrollment_date"],
            )

    def test_required_fields_reject_missing_values(self):
        fields = (
            "name",
            "email",
            "date_of_birth",
            "study_program",
            "phone",
            "enrollment_date",
        )

        for field in fields:
            with self.subTest(field=field):
                values = self.student_data.copy()
                values["email"] = f"missing_{field}_{uuid.uuid4().hex[:8]}@example.com"
                values[field] = None

                with self.assertRaises(mysql.connector.IntegrityError):
                    self.repository.create(**values)

    def test_delete_student_and_confirm_absence(self):
        student_id = self._create_student()

        self.repository.delete(student_id)

        self.assertIsNone(self.repository.get(student_id))

    def test_search_sort_and_pagination(self):
        first_id = self._create_student()
        second_email = f"second_{uuid.uuid4().hex[:8]}@example.com"
        self.repository.create(
            "Another Student",
            second_email,
            date(1999, 5, 20),
            "Design",
            "+37122222222",
            date(2026, 9, 3),
        )
        self.updated_email = second_email

        results = self.repository.list_students(
            search="Computer",
            sort_column="name",
            offset=0,
            limit=1,
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, first_id)
        self.assertEqual(self.repository.count("Computer"), 1)
