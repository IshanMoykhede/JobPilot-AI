import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)

def send_otp_email(to_email: str, otp: str):
    """
    Sends a 6-digit OTP to the user's email via SMTP.
    If SMTP details are missing from settings, logs the OTP to the console instead (fallback).
    """
    subject = "JobPilot AI - Your Password Reset OTP"
    body = f"""Hello,

You requested a password reset. Here is your One-Time Password (OTP) code:

{otp}

This OTP is valid for 10 minutes. If you did not make this request, please ignore this email.

Best regards,
The JobPilot AI Team"""

    # Check for SMTP settings
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.info(f"====== DEV MODE OTP LOG ======")
        logger.info(f"Email: {to_email}")
        logger.info(f"OTP: {otp}")
        logger.info(f"==============================")
        print(f"\n[DEV MODE] OTP for {to_email}: {otp}\n")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())
        server.quit()
        logger.info(f"OTP email sent successfully to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send SMTP email to {to_email}: {e}")
        # Log to console so it's not totally lost in dev even if SMTP fails
        print(f"\n[SMTP FAILURE FALLBACK] OTP for {to_email}: {otp}\n")
