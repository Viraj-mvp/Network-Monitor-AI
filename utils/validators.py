"""
Validation utilities for Network AI Monitor
Email, SMTP, and network validation functions
"""

import re
import smtplib
import socket
from typing import Tuple, List
import psutil


class ValidationError(Exception):
    """Custom validation error with user-friendly message"""
    pass


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format.
    Returns (is_valid, error_message)
    """
    if not email or not email.strip():
        return False, "Email address is required"
    
    email = email.strip()
    
    # Basic format check
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format. Example: user@gmail.com"
    
    # Gmail-specific check (for this simplified setup)
    if not email.endswith('@gmail.com'):
        return True, "Note: Only Gmail addresses are fully supported in this version"
    
    return True, ""


def validate_app_password(password: str) -> Tuple[bool, str]:
    """
    Validate Gmail app password format.
    Gmail app passwords are 16 characters, no spaces.
    Returns (is_valid, error_message)
    """
    if not password or not password.strip():
        return False, "App password is required"
    
    password = password.strip().replace(' ', '')
    
    # App passwords are typically 16 characters
    if len(password) != 16:
        return False, "Gmail app password should be 16 characters (remove spaces if any)"
    
    # Should be alphanumeric
    if not password.isalnum():
        return False, "App password should only contain letters and numbers"
    
    return True, ""


def test_smtp_connection(sender_email: str, app_password: str, 
                         receiver_email: str = None,
                         timeout: int = 10) -> Tuple[bool, str]:
    """
    Test SMTP connection with Gmail.
    Returns (success, message)
    """
    try:
        # Try to connect to Gmail SMTP
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=timeout)
        server.starttls()
        server.login(sender_email, app_password)
        
        # If receiver provided, try to verify it's valid
        if receiver_email:
            # Note: We can't actually verify if email exists without sending
            # But we can validate format
            valid, msg = validate_email(receiver_email)
            if not valid:
                server.quit()
                return False, f"Receiver email: {msg}"
        
        server.quit()
        return True, "SMTP connection successful! Email alerts are ready."
        
    except smtplib.SMTPAuthenticationError:
        return False, "Authentication failed. Please check your Gmail app password."
    except smtplib.SMTPConnectError:
        return False, "Could not connect to Gmail SMTP server. Check your internet connection."
    except socket.timeout:
        return False, "Connection timed out. Please check your internet connection."
    except socket.gaierror:
        return False, "Network error. Could not resolve SMTP server address."
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def get_network_interfaces() -> List[dict]:
    """
    Get list of available network interfaces.
    Returns list of dicts with name, type, and status.
    """
    interfaces = []
    
    try:
        stats = psutil.net_if_stats()
        io_counters = psutil.net_io_counters(pernic=True)
        
        for name, stat in stats.items():
            # Skip loopback
            if name.lower() in ('lo', 'loopback', 'localhost'):
                continue
            
            # Determine interface type
            name_lower = name.lower()
            if any(x in name_lower for x in ('wi-fi', 'wifi', 'wlan', 'wlp')):
                iface_type = 'WiFi'
            elif any(x in name_lower for x in ('eth', 'enp', 'ens', 'ethernet')):
                iface_type = 'Ethernet'
            elif any(x in name_lower for x in ('bluetooth', 'bt')):
                iface_type = 'Bluetooth'
            elif any(x in name_lower for x in ('tun', 'vpn', 'ppp')):
                iface_type = 'VPN'
            else:
                iface_type = 'Other'
            
            # Check if interface is active (has traffic)
            is_active = stat.isup
            has_traffic = name in io_counters
            
            interfaces.append({
                'name': name,
                'type': iface_type,
                'is_up': is_active,
                'has_traffic': has_traffic,
                'speed': stat.speed if stat.speed else 0,  # Mbps
                'display_name': f"{name} ({iface_type})"
            })
    except Exception as e:
        print(f"Error getting network interfaces: {e}")
    
    # Sort: active first, then by type
    interfaces.sort(key=lambda x: (not x['is_up'], x['type'], x['name']))
    
    return interfaces


def validate_monitoring_interval(interval: int) -> Tuple[bool, str]:
    """
    Validate monitoring interval.
    Returns (is_valid, error_message)
    """
    if interval < 1:
        return False, "Interval must be at least 1 second"
    if interval > 300:
        return False, "Interval should not exceed 300 seconds (5 minutes)"
    return True, ""


def validate_threshold(value: float, direction: str = "in/out") -> Tuple[bool, str]:
    """
    Validate bandwidth threshold value.
    Returns (is_valid, error_message)
    """
    if value < 0:
        return False, f"Threshold cannot be negative"
    if value > 10000:
        return False, f"Threshold seems too high (>10000 Mbps)"
    return True, ""


class ConfigValidator:
    """Validator for complete configuration"""
    
    @staticmethod
    def validate_monitoring_settings(settings: dict) -> Tuple[bool, List[str]]:
        """Validate monitoring settings section"""
        errors = []
        
        # Interval
        interval = settings.get('interval', 5)
        valid, msg = validate_monitoring_interval(interval)
        if not valid:
            errors.append(f"Monitoring interval: {msg}")
        
        # Thresholds
        wifi_in = settings.get('wifi_threshold_in', 1.0)
        valid, msg = validate_threshold(wifi_in, "WiFi inbound")
        if not valid:
            errors.append(msg)
        
        wifi_out = settings.get('wifi_threshold_out', 0.5)
        valid, msg = validate_threshold(wifi_out, "WiFi outbound")
        if not valid:
            errors.append(msg)
        
        eth_in = settings.get('ethernet_threshold_in', 5.0)
        valid, msg = validate_threshold(eth_in, "Ethernet inbound")
        if not valid:
            errors.append(msg)
        
        eth_out = settings.get('ethernet_threshold_out', 2.0)
        valid, msg = validate_threshold(eth_out, "Ethernet outbound")
        if not valid:
            errors.append(msg)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_email_settings(settings: dict, check_credentials: bool = False) -> Tuple[bool, List[str]]:
        """Validate email settings section"""
        errors = []
        
        if not settings.get('enabled', False):
            return True, []  # Email disabled, no validation needed
        
        # Sender email
        sender = settings.get('sender_email', '')
        valid, msg = validate_email(sender)
        if not valid:
            errors.append(f"Sender email: {msg}")
        elif not sender.endswith('@gmail.com'):
            errors.append("Only Gmail addresses are supported for sender email")
        
        # Receiver email
        receiver = settings.get('receiver_email', '')
        valid, msg = validate_email(receiver)
        if not valid:
            errors.append(f"Receiver email: {msg}")
        
        if check_credentials:
            # This would require the app password, which isn't in settings
            # It's stored separately in credential manager
            pass
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_appearance_settings(settings: dict) -> Tuple[bool, List[str]]:
        """Validate appearance settings section"""
        errors = []
        
        theme = settings.get('theme', 'auto')
        if theme not in ('auto', 'dark', 'light'):
            errors.append("Theme must be 'auto', 'dark', or 'light'")
        
        return len(errors) == 0, errors
