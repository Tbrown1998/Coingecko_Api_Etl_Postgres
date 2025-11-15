import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from configs import settings
from etl.utils import get_logger

logger = get_logger(__name__)


def send_mail(subject: str, body: str, filename_content: str, today: str):
    """
    Sends an email with the CSV content attached (file stored in memory).
    `filename_content` is a string containing CSV text (not a file path).
    """

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    sender_mail = settings.EMAIL_SENDER
    email_password = settings.EMAIL_PASSWORD
    receiver_mails = settings.EMAIL_RECEIVERS

    if not sender_mail or not email_password or not receiver_mails:
        logger.error("=== Email credentials or receivers are missing in settings. ===")
        return

    message = MIMEMultipart()
    message["From"] = sender_mail
    message["To"] = ", ".join(receiver_mails)
    message["Subject"] = subject

    # Attach HTML body (kept exactly as requested)
    message.attach(MIMEText(body, "html"))

    # Attach CSV in memory
    csv_part = MIMEApplication(filename_content, Name=f"crypto_data_{today}.csv")
    csv_part["Content-Disposition"] = f'attachment; filename="crypto_data_{today}.csv"'
    message.attach(csv_part)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_mail, email_password)
            server.sendmail(sender_mail, receiver_mails, message.as_string())
            logger.info(f"=== Email sent successfully to: {', '.join(receiver_mails)} ===")
    except Exception as e:
        logger.error(f"=== Unable to send mail {e} ===")
        raise
