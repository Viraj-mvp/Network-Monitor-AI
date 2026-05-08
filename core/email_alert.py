"""
Email Alert System - Uses config manager for credentials
Sends email notifications for network anomalies
"""

import os
import sys
import smtplib
import traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from config import get_credential_manager, get_config_manager

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

LOG_FILE = "email_error.log"

def send_email_alert(subject, message, custom_receiver=None):
    """
    Send email alert using configured credentials.
    
    Args:
        subject: Email subject
        message: Email body
        custom_receiver: Optional override for receiver email
    """
    # Get credentials from secure storage
    cred_mgr = get_credential_manager()
    credentials = cred_mgr.load_email_credentials()
    
    if not credentials:
        error_msg = "Email alert failed: No credentials configured"
        _log_error(error_msg)
        return False
    
    sender_email = credentials.get('sender_email')
    app_password = credentials.get('app_password')
    receiver_email = custom_receiver or credentials.get('receiver_email')
    
    if not sender_email or not app_password:
        error_msg = f"Email alert failed: Incomplete credentials (sender: {bool(sender_email)}, password: {bool(app_password)})"
        _log_error(error_msg)
        return False
    
    # Get receiver from config if not in credentials
    if not receiver_email:
        config_mgr = get_config_manager()
        receiver_email = config_mgr.email.receiver_email
    
    if not receiver_email:
        error_msg = "Email alert failed: No receiver email configured"
        _log_error(error_msg)
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "plain"))

        print(f"[Email] Sending alert to {receiver_email}...")
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)
        server.quit()
        
        print("[Email] Alert sent successfully.")
        return True

    except smtplib.SMTPAuthenticationError:
        error_log = "SMTP Authentication Error: Check your Gmail App Password."
        _log_error(error_log)
        return False
    except smtplib.SMTPException as e:
        error_log = f"SMTP Error occurred: {e}"
        _log_error(error_log)
        return False
    except Exception as e:
        error_log = f"Unexpected error in email system: {e}"
        _log_error(error_log)
        return False


def _log_error(message):
    """Log error to file"""
    try:
        # Use app data directory for logs
        config_mgr = get_config_manager()
        logs_dir = config_mgr.get_logs_dir()
        log_path = Path(logs_dir) / "email_errors.log"
        
        with open(log_path, "a") as f:
            f.write(f"\n[{os.getpid()}] {message}\n{traceback.format_exc()}")
    except Exception:
        pass
    
    print(f"[Email Error] {message}")


def test_email_configuration(sender_email=None, app_password=None, 
                             receiver_email=None, timeout=10):
    """
    Test email configuration without sending actual alert.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Use provided credentials or load from storage
    if not sender_email or not app_password:
        cred_mgr = get_credential_manager()
        credentials = cred_mgr.load_email_credentials()
        if credentials:
            sender_email = sender_email or credentials.get('sender_email')
            app_password = app_password or credentials.get('app_password')
            receiver_email = receiver_email or credentials.get('receiver_email')
    
    if not sender_email or not app_password:
        return False, "Email credentials not configured"
    
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=timeout)
        server.starttls()
        server.login(sender_email, app_password)
        server.quit()
        return True, "Email configuration is valid"
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication failed - check your Gmail App Password"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"


def is_email_configured() -> bool:
    """Check if email is properly configured"""
    cred_mgr = get_credential_manager()
    return cred_mgr.has_credentials()
