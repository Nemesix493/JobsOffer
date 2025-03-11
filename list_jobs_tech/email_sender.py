import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date

from .report import Report
from .settings import (
    SMTP_SERVER,
    SMTP_PORT,
    EMAIL_SENDER,
    EMAIL_PASSWORD,
    EMAIL_RECEIVER,
    EMAIL_ENABLE
)


class EmailSender:
    @property
    def smtp_server(self):
        return self._smtp_server

    @property
    def smtp_port(self):
        return self._smtp_port

    @property
    def email_sender(self):
        return self._email_sender

    @property
    def email_password(self):
        return self._email_password

    @property
    def email_receiver(self):
        return self._email_receiver

    def __init__(self, email_receiver: str | None = None):
        if not EMAIL_ENABLE:
            raise ValueError(
                "Email is disable !\n"
                "To enable email sepcify minimum email settings in your settings file\n"
                "- SMTP_SERVER\n"
                "- EMAIL_SENDER\n"
                "- EMAIL_PASSWORD\n"
                "- SMTP_PORT Default -> 587"
            )
        self._smtp_server = SMTP_SERVER
        self._smtp_port = SMTP_PORT
        self._email_sender = EMAIL_SENDER
        self._email_password = EMAIL_PASSWORD
        self._email_receiver = EMAIL_RECEIVER
        if email_receiver is not None:
            self._email_receiver = email_receiver
        elif self._email_receiver is None:
            raise ValueError(
                "No receiver adresse !\n"
                "Please specify one or configure a default one in your settings file"
            )

    def get_virgin_message(self) -> MIMEMultipart:
        message = MIMEMultipart()
        message["From"] = self.email_sender
        message["To"] = self.email_receiver
        return message

    def send_report(self, report: Report):
        message = self.get_virgin_message()
        message["Subject"] = f"Job searcher report from {date.today().strftime('%d/%m/%Y')}"
        body = report.html()
        message.attach(MIMEText(body, "html"))
        self.send(message)

    def send(self, message: MIMEMultipart):
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_sender, self.email_password)
            server.sendmail(
                self.email_sender,
                self.email_receiver,
                message.as_string()
            )
            server.quit()
            print("✅ E-mail successfully sent !")
        except Exception as e:
            print(f"❌ Failed email not sent due to this error : {e}")
