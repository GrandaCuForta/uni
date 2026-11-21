import sys
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.gui import StudentManagerApp


class FakeVariable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class FakeRepository:
    def __init__(self):
        self.created = []
        self.updated = []

    def create(self, *values):
        self.created.append(values)
        return 1

    def update(self, student_id, *values):
        self.updated.append((student_id, values))


class GuiSaveTests(unittest.TestCase):
    def setUp(self):
        self.app = StudentManagerApp.__new__(StudentManagerApp)
        self.app.repository = FakeRepository()
        self.app.status_var = FakeVariable("")
        self.variables = {
            "name": FakeVariable("Anna Ozola"),
            "email": FakeVariable("anna@example.com"),
            "date_of_birth": FakeVariable("15/01/2000"),
            "study_program": FakeVariable("Computer Science"),
            "phone": FakeVariable("+371 2000 0000"),
            "enrollment_date": FakeVariable("01/09/2020"),
        }

    def test_create_student_from_form(self):
        with patch.object(self.app, "_show_list_section"), patch.object(
            self.app, "load_students"
        ):
            self.app._save_form(self.variables, None)

        self.assertEqual(
            self.app.repository.created,
            [
                (
                    "Anna Ozola",
                    "anna@example.com",
                    date(2000, 1, 15),
                    "Computer Science",
                    "+371 2000 0000",
                    date(2020, 9, 1),
                )
            ],
        )
        self.assertEqual(self.app.repository.updated, [])

    def test_edit_student_from_form(self):
        with patch.object(self.app, "_show_list_section"), patch.object(
            self.app, "load_students"
        ):
            self.app._save_form(self.variables, 42)

        self.assertEqual(self.app.repository.created, [])
        self.assertEqual(
            self.app.repository.updated,
            [
                (
                    42,
                    (
                        "Anna Ozola",
                        "anna@example.com",
                        date(2000, 1, 15),
                        "Computer Science",
                        "+371 2000 0000",
                        date(2020, 9, 1),
                    ),
                )
            ],
        )


if __name__ == "__main__":
    unittest.main()
