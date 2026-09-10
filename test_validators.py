import unittest

from validators import validate_age, validate_email, validate_name


class ValidationTests(unittest.TestCase):
    def test_valid_name(self):
        self.assertTrue(validate_name("Aleks"))

    def test_empty_name_is_invalid(self):
        self.assertFalse(validate_name("   "))

    def test_valid_email(self):
        self.assertTrue(validate_email("aleks@example.com"))

    def test_email_without_at_symbol_is_invalid(self):
        self.assertFalse(validate_email("aleks.example.com"))

    def test_email_with_spaces_is_trimmed(self):
        self.assertTrue(validate_email(" aleks@example.com "))

    def test_valid_age(self):
        self.assertTrue(validate_age("20"))

    def test_zero_is_valid_age(self):
        self.assertTrue(validate_age(0))

    def test_120_is_valid_age(self):
        self.assertTrue(validate_age(120))

    def test_negative_age_is_invalid(self):
        self.assertFalse(validate_age(-1))

    def test_non_numeric_age_is_invalid(self):
        self.assertFalse(validate_age("twenty"))


if __name__ == "__main__":
    unittest.main()
