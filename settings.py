from os import getenv

# Email settings

SMTP_SERVER = getenv("SMTP_SERVER", None)
EMAIL_SENDER = getenv("EMAIL_SENDER", None)
EMAIL_PASSWORD = getenv("EMAIL_PASSWORD", None)
EMAIL_RECEIVER = getenv("EMAIL_RECEIVER", None)
