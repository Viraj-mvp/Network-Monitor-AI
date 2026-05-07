# dashboard/settings_panel.py
import json
import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class SettingsPanel(QWidget):
    settings_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.settings_file = "settings.json"
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
        
        self.wifi_out = QDoubleSpinBox()
        self.wifi_out.setRange(0, 1000)
        self.wifi_out.setSuffix(" Mbps")

        self.eth_in = QDoubleSpinBox()
        self.eth_in.setRange(0, 1000)
        self.eth_in.setSuffix(" Mbps")
        
        self.eth_out = QDoubleSpinBox()
        self.eth_out.setRange(0, 1000)
        self.eth_out.setSuffix(" Mbps")
        
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
        self.receiver_email = QLineEdit()
        self.receiver_email.setPlaceholderText("example@gmail.com")
        
        email_layout.addRow(self.enable_email)
        email_layout.addRow("Receiver Email:", self.receiver_email)
        
        email_group.setLayout(email_layout)
        layout.addWidget(email_group)
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setObjectName("saveButton")
        layout.addWidget(save_btn)
        
        layout.addStretch()
        self.setLayout(layout)

    def save_settings(self):
        # Input Validation
        email = self.receiver_email.text().strip()
        if self.enable_email.isChecked() and not email:
            QMessageBox.warning(self, "Validation Error", "Receiver email is required when alerts are enabled.")
            return
            
        import re
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            QMessageBox.warning(self, "Validation Error", "Please enter a valid email address.")
            return

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
        
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            self.settings_changed.emit(settings)
            QMessageBox.information(self, "Success", "Settings saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")

    def load_settings(self):
        # Default settings
        settings = {
            "thresholds": {
                "WiFi": {"in": 1.0, "out": 0.5},
                "Ethernet": {"in": 5.0, "out": 2.0}
            },
            "email": {
                "enabled": False,
                "receiver": ""
            }
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    # Merge loaded settings with defaults to handle missing keys
                    if "thresholds" in loaded:
                        settings["thresholds"].update(loaded["thresholds"])
                    if "email" in loaded:
                        settings["email"].update(loaded["email"])
            except Exception:
                pass # Use defaults on error
        
        # Apply to UI
        self.wifi_in.setValue(settings["thresholds"]["WiFi"]["in"])
        self.wifi_out.setValue(settings["thresholds"]["WiFi"]["out"])
        self.eth_in.setValue(settings["thresholds"]["Ethernet"]["in"])
        self.eth_out.setValue(settings["thresholds"]["Ethernet"]["out"])
        self.enable_email.setChecked(settings["email"]["enabled"])
        self.receiver_email.setText(settings["email"]["receiver"])
        
        # Emit initial settings
        self.settings_changed.emit(settings)