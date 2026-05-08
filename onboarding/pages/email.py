"""
Email Settings Page - Configure Gmail alerts
"""

from PySide6.QtWidgets import (
    QWizardPage, QVBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QPushButton, QGroupBox, QFormLayout,
    QMessageBox, QHBoxLayout, QWidget, QSpacerItem,
    QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from utils.validators import validate_email, validate_app_password, test_smtp_connection
from config import get_credential_manager


class EmailPage(QWizardPage):
    """Page for configuring email alert settings"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Email Alerts")
        self.setSubTitle("Configure Gmail notifications for network anomalies")
        self._smtp_tested = False
        self._test_success = False
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Enable/Disable email
        self.enable_checkbox = QCheckBox("Enable Email Alerts")
        self.enable_checkbox.setChecked(False)
        self.enable_checkbox.stateChanged.connect(self.on_enable_changed)
        enable_font = QFont()
        enable_font.setPointSize(14)
        enable_font.setBold(True)
        self.enable_checkbox.setFont(enable_font)
        layout.addWidget(self.enable_checkbox)
        
        # Email settings group
        self.email_group = QGroupBox("Gmail Configuration")
        email_layout = QFormLayout()
        email_layout.setSpacing(15)
        
        # Sender email (Gmail)
        self.sender_email = QLineEdit()
        self.sender_email.setPlaceholderText("your.email@gmail.com")
        self.sender_email.textChanged.connect(self.on_email_changed)
        email_layout.addRow("Your Gmail address:", self.sender_email)
        
        # App password
        self.app_password = QLineEdit()
        self.app_password.setEchoMode(QLineEdit.Password)
        self.app_password.setPlaceholderText("16-character app password")
        self.app_password.textChanged.connect(self.on_password_changed)
        email_layout.addRow("Gmail App Password:", self.app_password)
        
        # Show password checkbox
        self.show_password = QCheckBox("Show password")
        self.show_password.stateChanged.connect(self.toggle_password_visibility)
        email_layout.addRow("", self.show_password)
        
        # App password help
        help_label = QLabel(
            "<a href='https://support.google.com/accounts/answer/185833'>"
            "How to create a Gmail App Password →</a>"
        )
        help_label.setOpenExternalLinks(True)
        help_label.setStyleSheet("color: #2196F3; font-size: 11px;")
        email_layout.addRow("", help_label)
        
        # Receiver email
        self.receiver_email = QLineEdit()
        self.receiver_email.setPlaceholderText("alerts@example.com (can be same as sender)")
        self.receiver_email.textChanged.connect(self.on_email_changed)
        email_layout.addRow("Send alerts to:", self.receiver_email)
        
        self.email_group.setLayout(email_layout)
        layout.addWidget(self.email_group)
        
        # Test button
        test_widget = QWidget()
        test_layout = QHBoxLayout(test_widget)
        test_layout.setContentsMargins(0, 0, 0, 0)
        
        self.test_btn = QPushButton("Test Email Connection")
        self.test_btn.setMinimumWidth(180)
        self.test_btn.clicked.connect(self.test_connection)
        self.test_btn.setEnabled(False)
        test_layout.addWidget(self.test_btn)
        
        self.test_result = QLabel("")
        self.test_result.setStyleSheet("font-size: 12px;")
        test_layout.addWidget(self.test_result, 1)
        test_layout.addStretch()
        
        layout.addWidget(test_widget)
        
        # Info box
        info_box = QGroupBox("About Email Alerts")
        info_layout = QVBoxLayout()
        
        info_text = QLabel(
            "• An email is sent when network traffic exceeds your thresholds\n"
            "• Alerts are rate-limited to prevent spam\n"
            "• You can disable/enable alerts anytime in Settings\n"
            "• Only Gmail is supported in this version"
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        info_box.setLayout(info_layout)
        layout.addWidget(info_box)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Initial state
        self.update_field_states()
    
    def on_enable_changed(self, state):
        """Enable/disable email fields based on checkbox"""
        enabled = state == Qt.Checked
        self.email_group.setEnabled(enabled)
        self.test_btn.setEnabled(enabled and self.has_required_fields())
        self._smtp_tested = False
        self._test_success = False
        self.test_result.setText("")
        self.completeChanged.emit()
    
    def update_field_states(self):
        """Update field enabled states"""
        enabled = self.enable_checkbox.isChecked()
        self.email_group.setEnabled(enabled)
        self.test_btn.setEnabled(enabled and self.has_required_fields())
    
    def has_required_fields(self) -> bool:
        """Check if required fields are filled"""
        return (
            self.sender_email.text().strip() and 
            self.app_password.text().strip() and
            self.receiver_email.text().strip()
        )
    
    def on_email_changed(self):
        """Handle email field changes"""
        self._smtp_tested = False
        self._test_success = False
        self.test_result.setText("")
        self.test_btn.setEnabled(
            self.enable_checkbox.isChecked() and self.has_required_fields()
        )
        self.completeChanged.emit()
    
    def on_password_changed(self):
        """Handle password field changes"""
        self._smtp_tested = False
        self._test_success = False
        self.test_result.setText("")
        self.test_btn.setEnabled(
            self.enable_checkbox.isChecked() and self.has_required_fields()
        )
        self.completeChanged.emit()
    
    def toggle_password_visibility(self, state):
        """Toggle password visibility"""
        if state == Qt.Checked:
            self.app_password.setEchoMode(QLineEdit.Normal)
        else:
            self.app_password.setEchoMode(QLineEdit.Password)
    
    def test_connection(self):
        """Test SMTP connection"""
        sender = self.sender_email.text().strip()
        password = self.app_password.text().strip()
        receiver = self.receiver_email.text().strip()
        
        # Validate inputs first
        valid, msg = validate_email(sender)
        if not valid:
            self.test_result.setText(f"❌ {msg}")
            self.test_result.setStyleSheet("color: #f44336; font-size: 12px;")
            return
        
        if not sender.endswith('@gmail.com'):
            self.test_result.setText("❌ Only Gmail addresses are supported")
            self.test_result.setStyleSheet("color: #f44336; font-size: 12px;")
            return
        
        valid, msg = validate_app_password(password)
        if not valid:
            self.test_result.setText(f"❌ {msg}")
            self.test_result.setStyleSheet("color: #f44336; font-size: 12px;")
            return
        
        valid, msg = validate_email(receiver)
        if not valid:
            self.test_result.setText(f"❌ Receiver: {msg}")
            self.test_result.setStyleSheet("color: #f44336; font-size: 12px;")
            return
        
        # Test connection
        self.test_result.setText("⏳ Testing connection...")
        self.test_result.setStyleSheet("color: #ff9800; font-size: 12px;")
        self.test_btn.setEnabled(False)
        
        # Run test (in real app, this should be threaded)
        success, msg = test_smtp_connection(sender, password, receiver)
        
        self._smtp_tested = True
        self._test_success = success
        
        if success:
            self.test_result.setText(f"✅ {msg}")
            self.test_result.setStyleSheet("color: #4caf50; font-size: 12px;")
        else:
            self.test_result.setText(f"❌ {msg}")
            self.test_result.setStyleSheet("color: #f44336; font-size: 12px;")
        
        self.test_btn.setEnabled(True)
        self.completeChanged.emit()
    
    def isComplete(self):
        """Validate email settings"""
        if not self.enable_checkbox.isChecked():
            return True  # Email disabled is valid
        
        # If enabled, check required fields
        if not self.has_required_fields():
            return False
        
        # Basic validation
        sender = self.sender_email.text().strip()
        valid, _ = validate_email(sender)
        if not valid:
            return False
        
        receiver = self.receiver_email.text().strip()
        valid, _ = validate_email(receiver)
        if not valid:
            return False
        
        # We don't require SMTP test to pass to proceed
        # User can configure email and test later
        return True
    
    def validatePage(self):
        """Validate before proceeding"""
        return self.isComplete()
    
    def get_settings(self) -> dict:
        """Get email settings from page"""
        if not self.enable_checkbox.isChecked():
            return {
                'enabled': False,
                'sender_email': '',
                'receiver_email': ''
            }
        
        return {
            'enabled': True,
            'sender_email': self.sender_email.text().strip(),
            'receiver_email': self.receiver_email.text().strip()
        }
    
    def get_credentials(self) -> tuple:
        """Get credentials (sender_email, app_password, receiver_email)"""
        if not self.enable_checkbox.isChecked():
            return None, None, None
        
        return (
            self.sender_email.text().strip(),
            self.app_password.text().strip(),
            self.receiver_email.text().strip()
        )
    
    def nextId(self):
        """Go to appearance settings page"""
        return 3  # Index of AppearancePage
