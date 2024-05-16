import smtplib
import ssl
from email.message import Message
from app import config
import logging


class MailManagerNotConfigured(Exception):
    pass


class MailManager:
    context_key = "_mail_manager"

    def __init__(self):
        self.host = config.MAIL_HOST
        self.port = config.MAIL_PORT
        self.password = config.MAIL_PASSWORD
        self.username = config.MAIL_USERNAME
        self._from = config.MAIL_FROM

    def send(self, to, subject, body):
        if "" in (self._from, self.host, self.port, self.password, self.username):
            raise MailManagerNotConfigured(
                "Ensure you have configured all the required MAIL_* environment variables."
            )

        logging.info(f"Sending email via {self.host} - {self.username}")

        message = Message()
        message.add_header("from", self._from)
        message.add_header("to", to)
        message.add_header("subject", subject)
        # Always send html emails.
        message.add_header("Content-Type", "text/html")
        message.set_payload(body)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.host, self.port, context=context) as server:
            server.login(self.username, self.password)
            server.sendmail(self._from, to, message.as_string().encode("utf-8"))
