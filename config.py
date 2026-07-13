"""
Application configuration.

Loads all environment variables from the .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ---------------------------
# Bright Data
# ---------------------------

BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY")
BRIGHTDATA_ENDPOINT = os.getenv("BRIGHTDATA_ENDPOINT")
BRIGHTDATA_ZONE = os.getenv("BRIGHTDATA_ZONE")
TARGET_COUNTRY = os.getenv("TARGET_COUNTRY", "India")


# ---------------------------
# Database
# ---------------------------

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ---------------------------
# Defaults
# ---------------------------

DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "India")
DEFAULT_LIMIT = int(os.getenv("DEFAULT_LIMIT", 20))


def validate_config():
    """
    Ensure required configuration is present.
    """

    missing = []

    required = {
        "BRIGHTDATA_API_KEY": BRIGHTDATA_API_KEY,
        "BRIGHTDATA_ENDPOINT": BRIGHTDATA_ENDPOINT,
        "DB_HOST": DB_HOST,
        "DB_NAME": DB_NAME,
        "DB_USER": DB_USER,
        "DB_PASSWORD": DB_PASSWORD,
    }

    for key, value in required.items():
        if not value:
            missing.append(key)

    if missing:
        raise ValueError(
            f"Missing environment variables: {', '.join(missing)}"
        )