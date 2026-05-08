"""
Settings Panel - Updated to use ConfigManager
"""

import json
import os
import re
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from config import get_config_manager, get_credential_manager
from utils.validators import validate_email, validate_app_password
from core.email_alert import test_email_configuration


class SettingsPanel(QWidget):
    settings_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.config_mgr = get_config_manager()
        self.cred_mgr = get_credential_manager()
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Threshold settings
        group = QGroupBox("Threshold Settings")
        form_layout = QFormLayout()
        
        self.wifi_in = QDoubleSpinBox()
        self.wifi_in.setRange(0, 1000)
        self.wifi_in.setSuffix(" Mbps")
        self.wifi_in.setDecimals(1)
        
        self.wifi_out = QDoubleSpinBox()
        self.wifi_out.setRange(0, 1000)
        self.wifi_out.setSuffix(" Mbps")
        self.wifi_out.setDecimals(1)

        self.eth_in = QDoubleSpinBox()
        self.eth_in.setRange(0, 1000)
        self.eth_in.setSuffix(" Mbps")
        self.eth_in.setDecimals(1)
        
        self.eth_out = QDoubleSpinBox()
        self.eth_out.setRange(0, 1000)
        self.eth_out.setSuffix(" Mbps")
        self.eth_out.setDecimals(1)
        
        form_layout.addRow("WiFi Inbound:", self.wifi_in)
        form_layout.addRow("WiFi Outbound:", self.wifi_out)
        form_layout.addRow("Ethernet Inbound:", self.eth_in)
        form_layout.addRow("Ethernet Outbound:", self.eth_out)
        
        group.setLayout(form_layout)
        layout.addWidget(group)

        # Email Settings
        email_group = QGroupBox("Email Notification Settings")
        email_layout = QFormLayout()
        
        self.enable_email = QCheckBox("Enable Email Alerts")
        self.enable_email.stateChanged.connect(self.on_email_toggled)
        
        # Gmail configuration
        self.sender_email = QLineEdit()
        self.sender_email.setPlaceholderText("your.email@gmail.com")
        
        self.app_password = QLineEdit()
        self.app_password.setEchoMode(QLineEdit.Password)
        self.app_password.setPlaceholderText("16-character Gmail app password")
        
        self.show_password = QCheckBox("Show password")
        self.show_password.stateChanged.connect(self.toggle_password_visibility)
        
        self.receiver_email = QLineEdit()
        self.receiver_email.setPlaceholderText("alerts@example.com")
        
        # Test button
        self.test_email_btn = QPushButton("Test Email")
        self.test_email_btn.clicked.connect(self.test_email)
        
        email_layout.addRow(self.enable_email)
        email_layout.addRow("Gmail Address:", self.sender_email)
        email_layout.addRow("App Password:", self.app_password)
        email_layout.addRow("", self.show_password)
        email_layout.addRow("Send Alerts To:", self.receiver_email)
        email_layout.addRow("", self.test_email_btn)
        
        email_group.setLayout(email_layout)
        layout.addWidget(email_group)
        
        # Actions
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setObjectName("saveButton")
        button_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_btn)
        
        layout.addLayout(button_layout)
        
        # Config location info
        config_path = self.config_mgr.get_config_path()
        info_label = QLabel(f"Config: {config_path}")
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addStretch()
        self.setLayout(layout)

    def on_email_toggled(self, state):
        """Enable/disable email fields"""
        enabled = (state == Qt.Checked)
        self.sender_email.setEnabled(enabled)
        self.app_password.setEnabled(enabled)
        self.receiver_email.setEnabled(enabled)
        self.test_email_btn.setEnabled(enabled)
    
    def toggle_password_visibility(self, state):
        """Toggle password visibility"""
        if state == Qt.Checked:
            self.app_password.setEchoMode(QLineEdit.Normal)
        else:
            self.app_password.setEchoMode(QLineEdit.Password)
    
    def test_email(self):
        """Test email configuration"""
        sender = self.sender_email.text().strip()
        password = self.app_password.text().strip()
        receiver = self.receiver_email.text().strip()
        
        if not sender or not password:
            QMessageBox.warning(self, "Missing Credentials", 
                              "Please enter both Gmail address and app password.")
            return
        
        self.test_email_btn.setEnabled(False)
        self.test_email_btn.setText("Testing...")
        
        success, msg = test_email_configuration(sender, password, receiver)
        
        self.test_email_btn.setEnabled(True)
        self.test_email_btn.setText("Test Email")
        
        if success:
            QMessageBox.information(self, "Test Successful", msg)
        else:
            QMessageBox.warning(self, "Test Failed", msg)

    def save_settings(self):
        """Save settings using ConfigManager"""
        # Validate email if enabled
        if self.enable_email.isChecked():
            sender = self.sender_email.text().strip()
            valid, msg = validate_email(sender)
            if not valid:
                QMessageBox.warning(self, "Invalid Email", f"Sender: {msg}")
                return
            
            if not sender.endswith('@gmail.com'):
                QMessageBox.warning(self, "Unsupported Email", 
                                  "Only Gmail addresses are supported.")
                return
            
            password = self.app_password.text().strip()
            valid, msg = validate_app_password(password)
            if not valid:
                QMessageBox.warning(self, "Invalid Password", msg)
                return
            
            receiver = self.receiver_email.text().strip()
            valid, msg = validate_email(receiver)
            if not valid:
                QMessageBox.warning(self, "Invalid Email", f"Receiver: {msg}")
                return
            
            # Save credentials securely
            self.cred_mgr.save_email_credentials(sender, password, receiver)
        
        # Update config
        self.config_mgr.update_monitoring(
            wifi_threshold_in=self.wifi_in.value(),
            wifi_threshold_out=self.wifi_out.value(),
            ethernet_threshold_in=self.eth_in.value(),
            ethernet_threshold_out=self.eth_out.value()
        )
        
        self.config_mgr.update_email(
            enabled=self.enable_email.isChecked(),
            sender_email=self.sender_email.text().strip() if self.enable_email.isChecked() else "",
            receiver_email=self.receiver_email.text().strip() if self.enable_email.isChecked() else ""
        )
        
        # Emit settings changed
        settings = {
            "thresholds": {
                "WiFi": {"in": self.wifi_in.value(), "out": self.wifi_out.value()},
                "Ethernet": {"in": self.eth_in.value(), "out": self.eth_out.value()}
            },
            "email": {
                "enabled": self.enable_email.isChecked(),
                "receiver": self.receiver_email.text()
            }
        }
        
        self.settings_changed.emit(settings)
        QMessageBox.information(self, "Success", "Settings saved successfully!")

    def load_settings(self):
        """Load settings from ConfigManager"""
        # Load from config manager
        monitoring = self.config_mgr.monitoring
        email = self.config_mgr.email
        
        # Apply to UI
        self.wifi_in.setValue(monitoring.wifi_threshold_in)
        self.wifi_out.setValue(monitoring.wifi_threshold_out)
        self.eth_in.setValue(monitoring.ethernet_threshold_in)
        self.eth_out.setValue(monitoring.ethernet_threshold_out)
        
        self.enable_email.setChecked(email.enabled)
        self.receiver_email.setText(email.receiver_email)
        
        # Load credentials
        credentials = self.cred_mgr.load_email_credentials()
        if credentials:
            self.sender_email.setText(credentials.get('sender_email', ''))
            # Don't show password in UI (empty field means unchanged)
            self.app_password.setPlaceholderText("Enter to change password")
        
        # Enable/disable email fields
        self.on_email_toggled(Qt.Checked if email.enabled else Qt.Unchecked)
        
        # Emit initial settings
        settings = {
            "thresholds": {
                "WiFi": {"in": monitoring.wifi_threshold_in, "out": monitoring.wifi_threshold_out},
                "Ethernet": {"in": monitoring.ethernet_threshold_in, "out": monitoring.ethernet_threshold_out}
            },
            "email": {
                "enabled": email.enabled,
                "receiver": email.receiver_email
            }
        }
        self.settings_changed.emit(settings)
    
    def reset_settings(self):
        """Reset settings to defaults"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Are you sure you want to reset all settings to defaults?\n\n"
            "Email credentials will be preserved.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Reset thresholds to defaults
            self.wifi_in.setValue(1.0)
            self.wifi_out.setValue(0.5)
            self.eth_in.setValue(5.0)
            self.eth_out.setValue(2.0)
            
            # Reset email
            self.enable_email.setChecked(False)
            self.sender_email.clear()
            self.app_password.clear()
            self.receiver_email.clear()
            
            # Save
            self.save_settings()