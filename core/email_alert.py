import os
import smtplib
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

LOG_FILE = "email_error.log"

def send_email_alert(subject, message):
    if not SENDER_EMAIL or not APP_PASSWORD or not RECEIVER_EMAIL:
        error_msg = f"Email alert failed: Missing environment variables (SENDER: {SENDER_EMAIL}, RECEIVER: {RECEIVER_EMAIL})"
        with open(LOG_FILE, "a") as f:
            f.write(f"\n[{os.getpid()}] {error_msg}")
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "plain"))

        print(f"DEBUG: Attempting to send email to {RECEIVER_EMAIL} via {SMTP_SERVER}...")
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print("DEBUG: Email sent successfully.")

    except smtplib.SMTPAuthenticationError:
        error_log = "SMTP Authentication Error: Check your App Password."
        with open(LOG_FILE, "a") as f:
            f.write(f"\n{error_log}\n{traceback.format_exc()}")
        print(f"ERROR: {error_log}")
    except smtplib.SMTPException as e:
        error_log = f"SMTP Error occurred: {e}"
        with open(LOG_FILE, "a") as f:
            f.write(f"\n{error_log}\n{traceback.format_exc()}")
        print(f"ERROR: {error_log}")
    except Exception as e:
        error_log = f"Unexpected error in email system: {e}"
        with open(LOG_FILE, "a") as f:
            f.write(f"\n{error_log}\n{traceback.format_exc()}")
        print(f"ERROR: {error_log}")
