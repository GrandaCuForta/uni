import unittest
from datetime import date
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.validators import (
    parse_date,
    validate_date,
    validate_email,
    validate_enrollment_date,
    validate_name,
    validate_phone,
    validate_study_program,
)


class ValidationTests(unittest.TestCase):
    def test_name_accepts_letters_and_spaces(self):
        self.assertTrue(validate_name("Anna Ozola"))

    def test_name_rejects_numbers(self):
        self.assertFalse(validate_name("Anna2"))

    def test_name_rejects_empty_value(self):
        self.assertFalse(validate_name("   "))

    def test_email_accepts_valid_address(self):
        self.assertTrue(validate_email(" student@example.com "))

    def test_email_rejects_missing_domain(self):
        self.assertFalse(validate_email("student@"))

    def test_date_accepts_dd_mm_yyyy(self):
        self.assertTrue(validate_date("15/01/2000"))
        self.assertEqual(parse_date("15/01/2000"), date(2000, 1, 15))

    def test_date_rejects_impossible_date(self):
        self.assertFalse(validate_date("31/02/2000"))

    def test_phone_accepts_common_formats(self):
        self.assertTrue(validate_phone("+371 2000 0000"))
        self.assertTrue(validate_phone("20000000"))

    def test_phone_rejects_letters(self):
        self.assertFalse(validate_phone("phone-number"))

    def test_study_program_is_required(self):
        self.assertTrue(validate_study_program("Computer Science"))
        self.assertFalse(validate_study_program(""))

    def test_enrollment_date_cannot_be_in_the_future(self):
        self.assertTrue(validate_enrollment_date("01/09/2020"))
        self.assertFalse(validate_enrollment_date("01/01/2999"))


if __name__ == "__main__":
    unittest.main()
