import os

from dotenv import load_dotenv


load_dotenv()


def _required_setting(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Configure the database settings before starting the application."
        )
    return value


DB_HOST = _required_setting("DB_HOST")
DB_USER = _required_setting("DB_USER")
DB_PASSWORD = _required_setting("DB_PASSWORD")
DB_NAME = _required_setting("DB_NAME")
