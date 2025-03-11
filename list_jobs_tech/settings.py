import sys
import os
from pathlib import Path

# define default settings value

BASE_DIR = Path(__file__).resolve().parent

# Database settings

DB_PATH = BASE_DIR.parent / "my_db.db"
INITIAL_DATA = BASE_DIR.parent / "initial_data.sql"

# Email settings

SMTP_SERVER = None
SMTP_PORT = 587
EMAIL_SENDER = None
EMAIL_PASSWORD = None
EMAIL_RECEIVER = None
EMAIL_ENABLE = False

# Jinja settings

TEMPLATES_DIR = BASE_DIR / 'templates'

# remove pattern for offer description analyse

REMOVE_PATTERN = [
    ",",
    "/",
    "\n",
    "?",
    "..",
    ". ",
    ".\n",
    "\\"
]

# Settings initialisation

settings_keys = [
    "REMOVE_PATTERN",
    "DB_PATH",
    "INITIAL_DATA",
    "SMTP_SERVER",
    "SMTP_PORT",
    "EMAIL_SENDER",
    "EMAIL_PASSWORD",
    "EMAIL_RECEIVER",
    "TEMPLATES_DIR"
]


def settings_path():
    module_name = os.environ.get('SETTINGS_MODULE', None)
    if module_name is None:
        return None
    externe_settings_module = __import__(module_name)
    current_module = sys.modules[__name__]
    for key in settings_keys:
        if hasattr(externe_settings_module, key):
            print(f"{key} set in {current_module.__name__}")
            setattr(
                current_module,
                key,
                getattr(
                    externe_settings_module,
                    key
                )
            )


settings_path()

# Check email enabling
EMAIL_ENABLE = None not in (
    SMTP_SERVER,
    EMAIL_SENDER,
    EMAIL_PASSWORD
)
