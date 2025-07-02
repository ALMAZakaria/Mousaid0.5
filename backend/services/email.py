from backend.config import settings
import logging
import smtplib
from email.mime.text import MIMEText

def send_email_confirmation(user_profile):
    sender_email = settings.SENDER_EMAIL
    sender_email_app_password = settings.SENDER_EMAIL_APP_PASSWORD
    smtp_host = settings.SMTP_HOST
    smtp_port = int(settings.SMTP_PORT)
    receiver_email = user_profile.get("email")
    if not all([sender_email, sender_email_app_password, smtp_host, receiver_email]):
        logging.error(f"Missing environment variables for email sending or receiver email is missing. (session_id={user_profile.get('session_id')})")
        return
    subject = "Your Test Drive Schedule Confirmation"
    body = f"""Dear {user_profile.get('name', 'User')},\n\nThank you for your interest in a test drive! We have received your request and will contact you shortly to schedule your test drive.\n\nHere's a summary of your contact information:\nName: {user_profile.get('name', 'N/A')}\nLocation: {user_profile.get('location', 'N/A')}\nPhone: {user_profile.get('phone_number', 'N/A')}\nEmail: {user_profile.get('email', 'N/A')}\nTest drive date: {user_profile.get('test_drive_date', 'N/A')}\n\nBest regards,\nYour Car Recommendation Assistant\n"""
    try:
        import email.utils
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Date'] = email.utils.formatdate(localtime=True)
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(sender_email, sender_email_app_password)
            server.sendmail(sender_email, [receiver_email], msg.as_string())
        logging.info(f"Confirmation email sent successfully to {receiver_email} (session_id={user_profile.get('session_id')})")
    except Exception as e:
        logging.error(f"Failed to send confirmation email to {receiver_email} (session_id={user_profile.get('session_id')}): {e}") 