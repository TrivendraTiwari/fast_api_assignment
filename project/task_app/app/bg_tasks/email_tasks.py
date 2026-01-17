# task_app/app/tasks/email_tasks.py
from ..celery_app import celery
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from task_app.app.services_config.config import *

@celery.task
def send_email_notification(subject: str, body: str, to_email: str):
    message = MIMEMultipart()
    message["From"] = GMAIL_USER
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, message.as_string())

