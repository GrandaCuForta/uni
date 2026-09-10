def validate_name(name):
	return bool(name.strip())


def validate_email(email):
	return "@" in email.strip()


def validate_age(age):
	try:
		return 0 <= int(age) <= 120
	except (TypeError, ValueError):
		return False
