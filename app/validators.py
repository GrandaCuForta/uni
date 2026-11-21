import re
from datetime import date, datetime


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_PATTERN = re.compile(r"^\+?[0-9 ()-]{7,20}$")


def validate_name(name):
    words = name.strip().split()
    return bool(words) and all(word.isalpha() for word in words)


def validate_email(email):
    return bool(EMAIL_PATTERN.fullmatch(email.strip()))


def validate_age(age):
    try:
        return 0 <= int(age) <= 120
    except (TypeError, ValueError):
        return False


def validate_date(value):
    try:
        datetime.strptime(value.strip(), "%d/%m/%Y")
        return True
    except (TypeError, ValueError):
        return False


def parse_date(value):
    return datetime.strptime(value.strip(), "%d/%m/%Y").date()


def validate_phone(phone):
    return bool(PHONE_PATTERN.fullmatch(phone.strip()))


def validate_study_program(program):
    return bool(program.strip()) and len(program.strip()) <= 100


def validate_enrollment_date(value):
    if not validate_date(value):
        return False
    return parse_date(value) <= date.today()


__all__ = [
    "parse_date",
    "validate_date",
    "validate_age",
    "validate_email",
    "validate_enrollment_date",
    "validate_name",
    "validate_phone",
    "validate_study_program",
]
