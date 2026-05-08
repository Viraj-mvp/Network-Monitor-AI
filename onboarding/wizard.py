"""
Setup Wizard - Main container for onboarding
"""

from PySide6.QtWidgets import (
    QWizard, QApplication, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QWidget, QStyle
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap

from onboarding.pages import (
    WelcomePage, MonitoringPage, EmailPage, 
    AppearancePage, CompletePage
)
from config import get_config_manager, get_credential_manager


class SetupWizard(QWizard):
    """
    Setup wizard for first-run configuration.
    Collects user preferences and saves to config.
    """
    
    setup_completed = Signal(dict)  # Emits all settings on completion
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Network AI Monitor - Setup")
        self.setMinimumSize(700, 600)
        self.setWizardStyle(QWizard.ModernStyle)
        
        # Set app icon if available
        try:
            from utils.resources import resource_path
            icon_path = resource_path('assets/icon.ico')
            self.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass
        
        # Style the wizard
        self.setup_styles()
        
        # Add pages
        self.addPage(WelcomePage())      # 0
        self.addPage(MonitoringPage())   # 1
        self.addPage(EmailPage())        # 2
        self.addPage(AppearancePage())  # 3
        self.addPage(CompletePage())     # 4
        
        # Connect signals
        self.finished.connect(self.on_finished)
        
        # Store collected settings
        self.collected_settings = {}
    
    def setup_styles(self):
        """Apply modern styling to the wizard"""
        self.setStyleSheet("""
            QWizard {
                background-color: #f5f5f5;
            }
            QWizardPage {
                background-color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton#saveButton {
                background-color: #2196F3;
                color: white;
                border: none;
            }
            QPushButton#saveButton:hover {
                background-color: #1976D2;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QSpinBox, QDoubleSpinBox {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
    
    def on_finished(self, result):
        """Handle wizard completion"""
        if result == QWizard.Accepted:
            # Collect settings from all pages
            self.collected_settings = self.collect_settings()
            
            # Save to config
            self.save_settings()
            
            # Emit completion signal
            self.setup_completed.emit(self.collected_settings)
    
    def collect_settings(self) -> dict:
        """Collect settings from all wizard pages"""
        settings = {}
        
        # Monitoring settings (page 1)
        monitoring_page = self.page(1)
        if isinstance(monitoring_page, MonitoringPage):
            settings['monitoring'] = monitoring_page.get_settings()
        
        # Email settings (page 2)
        email_page = self.page(2)
        if isinstance(email_page, EmailPage):
            settings['email'] = email_page.get_settings()
            # Also get credentials separately
            creds = email_page.get_credentials()
            if creds and creds[0]:  # sender email present
                settings['credentials'] = {
                    'sender_email': creds[0],
                    'app_password': creds[1],
                    'receiver_email': creds[2]
                }
        
        # Appearance settings (page 3)
        appearance_page = self.page(3)
        if isinstance(appearance_page, AppearancePage):
            settings['appearance'] = appearance_page.get_settings()
        
        # Complete page options (page 4)
        complete_page = self.page(4)
        if isinstance(complete_page, CompletePage):
            settings['start_monitoring'] = complete_page.get_start_monitoring()
        
        return settings
    
    def save_settings(self):
        """Save collected settings to config and credentials"""
        config_mgr = get_config_manager()
        cred_mgr = get_credential_manager()
        
        try:
            # Disable auto-save temporarily
            config_mgr._auto_save = False
            
            # Save monitoring settings
            if 'monitoring' in self.collected_settings:
                m = self.collected_settings['monitoring']
                config_mgr.update_monitoring(
                    interface=m.get('interface', 'auto'),
                    interval=m.get('interval', 5),
                    ai_sensitivity=m.get('ai_sensitivity', 'medium'),
                    wifi_threshold_in=m.get('wifi_threshold_in', 1.0),
                    wifi_threshold_out=m.get('wifi_threshold_out', 0.5),
                    ethernet_threshold_in=m.get('ethernet_threshold_in', 5.0),
                    ethernet_threshold_out=m.get('ethernet_threshold_out', 2.0)
                )
            
            # Save email settings
            if 'email' in self.collected_settings:
                e = self.collected_settings['email']
                config_mgr.update_email(
                    enabled=e.get('enabled', False),
                    sender_email=e.get('sender_email', ''),
                    receiver_email=e.get('receiver_email', '')
                )
            
            # Save credentials securely
            if 'credentials' in self.collected_settings:
                c = self.collected_settings['credentials']
                if c.get('sender_email') and c.get('app_password'):
                    cred_mgr.save_email_credentials(
                        c['sender_email'],
                        c['app_password'],
                        c['receiver_email']
                    )
            
            # Save appearance settings
            if 'appearance' in self.collected_settings:
                a = self.collected_settings['appearance']
                config_mgr.update_appearance(
                    theme=a.get('theme', 'auto'),
                    start_minimized=a.get('start_minimized', False),
                    minimize_to_tray=a.get('minimize_to_tray', True),
                    startup_with_system=a.get('startup_with_system', False)
                )
            
            # Mark first run complete
            config_mgr.mark_first_run_complete()
            
            # Enable auto-save and save once
            config_mgr._auto_save = True
            config_mgr.save()
            
            print("✅ Setup settings saved successfully")
            
        except Exception as e:
            print(f"❌ Error saving settings: {e}")
            import traceback
            traceback.print_exc()
    
    def get_start_monitoring(self) -> bool:
        """Get whether to start monitoring after setup"""
        return self.collected_settings.get('start_monitoring', True)
    
    def get_theme(self) -> str:
        """Get selected theme"""
        appearance = self.collected_settings.get('appearance', {})
        return appearance.get('theme', 'auto')


def run_setup_wizard(parent=None) -> tuple[bool, dict]:
    """
    Run the setup wizard and return results.
    
    Returns:
        tuple: (accepted, settings)
            accepted: True if user completed setup, False if cancelled
            settings: dict of collected settings
    """
    wizard = SetupWizard(parent)
    result = wizard.exec()
    
    accepted = (result == QWizard.Accepted)
    settings = wizard.collected_settings if accepted else {}
    
    return accepted, settings
