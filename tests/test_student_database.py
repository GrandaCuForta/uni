import os
import unittest
import uuid

import mysql.connector
from dotenv import load_dotenv


load_dotenv()


@unittest.skipUnless(
    os.getenv("RUN_DB_TESTS") == "1",
    "Set RUN_DB_TESTS=1 to run the MySQL integration test.",
)
class StudentDatabaseFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.database = os.getenv("TEST_DB_NAME", "student_manager_test")
        cls.connection = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=cls.database,
        )
        cls.cursor = cls.connection.cursor()
        cls.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                age INT NOT NULL
            )
            """
        )
        cls.connection.commit()

    @classmethod
    def tearDownClass(cls):
        cls.cursor.close()
        cls.connection.close()

    def setUp(self):
        suffix = uuid.uuid4().hex[:8]
        self.email = f"student_{suffix}@example.com"
        self.updated_email = f"updated_{suffix}@example.com"
        self.cursor.execute("DELETE FROM students WHERE email IN (%s, %s)", (self.email, self.updated_email))
        self.connection.commit()

    def tearDown(self):
        self.cursor.execute("DELETE FROM students WHERE email IN (%s, %s)", (self.email, self.updated_email))
        self.connection.commit()

    def test_student_create_read_update_duplicate_email_delete_flow(self):
        self.cursor.execute(
            "INSERT INTO students (name, email, age) VALUES (%s, %s, %s)",
            ("Test Student", self.email, 20),
        )
        self.connection.commit()
        student_id = self.cursor.lastrowid

        self.cursor.execute(
            "SELECT name, email, age FROM students WHERE id = %s",
            (student_id,),
        )
        self.assertEqual(
            self.cursor.fetchone(),
            ("Test Student", self.email, 20),
        )

        self.cursor.execute(
            "UPDATE students SET name = %s, email = %s, age = %s WHERE id = %s",
            ("Updated Student", self.updated_email, 21, student_id),
        )
        self.connection.commit()

        self.cursor.execute(
            "SELECT name, email, age FROM students WHERE id = %s",
            (student_id,),
        )
        self.assertEqual(
            self.cursor.fetchone(),
            ("Updated Student", self.updated_email, 21),
        )

        with self.assertRaises(mysql.connector.IntegrityError):
            self.cursor.execute(
                "INSERT INTO students (name, email, age) VALUES (%s, %s, %s)",
                ("Duplicate Student", self.updated_email, 22),
            )
        self.connection.rollback()

        self.cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
        self.connection.commit()

        self.cursor.execute("SELECT 1 FROM students WHERE id = %s", (student_id,))
        self.assertIsNone(self.cursor.fetchone())


if __name__ == "__main__":
    unittest.main()
