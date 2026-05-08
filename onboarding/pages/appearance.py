"""
Appearance Settings Page - Configure theme and behavior
"""

from PySide6.QtWidgets import (
    QWizardPage, QVBoxLayout, QLabel, QComboBox, 
    QCheckBox, QGroupBox, QFormLayout, QHBoxLayout,
    QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import darkdetect


class AppearancePage(QWizardPage):
    """Page for configuring appearance and behavior settings"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Appearance & Behavior")
        self.setSubTitle("Customize how Network AI Monitor looks and behaves")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Theme Selection
        theme_group = QGroupBox("Theme")
        theme_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("🌓 Auto (follow system)", "auto")
        self.theme_combo.addItem("🌙 Dark Mode", "dark")
        self.theme_combo.addItem("☀️ Light Mode", "light")
        
        # Set default based on system
        if darkdetect.isDark():
            self.theme_combo.setCurrentIndex(0)  # Auto will pick dark
        else:
            self.theme_combo.setCurrentIndex(0)  # Auto will pick light
        
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        theme_layout.addRow("Application theme:", self.theme_combo)
        
        # Preview note
        preview_label = QLabel("Theme preview will be applied after setup")
        preview_label.setStyleSheet("color: gray; font-size: 11px;")
        theme_layout.addRow("", preview_label)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Startup Behavior
        startup_group = QGroupBox("Startup Behavior")
        startup_layout = QVBoxLayout()
        startup_layout.setSpacing(10)
        
        # Start minimized
        self.start_minimized = QCheckBox("Start minimized to system tray")
        self.start_minimized.setChecked(False)
        self.start_minimized.setToolTip(
            "When checked, the app will start minimized in the system tray"
        )
        startup_layout.addWidget(self.start_minimized)
        
        # Minimize to tray
        self.minimize_to_tray = QCheckBox("Minimize to tray instead of taskbar")
        self.minimize_to_tray.setChecked(True)
        self.minimize_to_tray.setToolTip(
            "When checked, minimizing the window will hide it to the system tray"
        )
        startup_layout.addWidget(self.minimize_to_tray)
        
        # Close to tray
        self.close_to_tray = QCheckBox("Keep running in tray when closing window")
        self.close_to_tray.setChecked(True)
        self.close_to_tray.setToolTip(
            "When checked, closing the window will keep the app running in the system tray"
        )
        startup_layout.addWidget(self.close_to_tray)
        
        # Auto-start monitoring
        self.auto_start_monitoring = QCheckBox("Automatically start monitoring on launch")
        self.auto_start_monitoring.setChecked(True)
        self.auto_start_monitoring.setToolTip(
            "When checked, network monitoring will start automatically when the app opens"
        )
        startup_layout.addWidget(self.auto_start_monitoring)
        
        # Windows-only: Start with system
        if sys.platform == 'win32':
            self.startup_with_system = QCheckBox("Start with Windows")
            self.startup_with_system.setChecked(False)
            self.startup_with_system.setToolTip(
                "Launch Network AI Monitor automatically when you log in to Windows"
            )
            startup_layout.addWidget(self.startup_with_system)
        else:
            self.startup_with_system = None
        
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)
        
        # Info box
        info_group = QGroupBox("System Tray")
        info_layout = QVBoxLayout()
        
        info_text = QLabel(
            "Network AI Monitor runs in your system tray for continuous monitoring:\n\n"
            "• 📊 View network status at a glance\n"
            "• 🔔 Get notified of alerts\n"
            "• ⚡ Quick access to start/stop monitoring\n"
            "• 🚪 Right-click tray icon for more options"
        )
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def on_theme_changed(self, index):
        """Handle theme selection change"""
        theme = self.theme_combo.currentData()
        # Could emit signal to preview theme
        self.completeChanged.emit()
    
    def isComplete(self):
        """Always complete (no required validation)"""
        return True
    
    def validatePage(self):
        """Validate before proceeding"""
        return True
    
    def get_settings(self) -> dict:
        """Get appearance settings from page"""
        settings = {
            'theme': self.theme_combo.currentData(),
            'start_minimized': self.start_minimized.isChecked(),
            'minimize_to_tray': self.minimize_to_tray.isChecked(),
            'close_to_tray': self.close_to_tray.isChecked(),
            'startup_with_system': self.startup_with_system.isChecked() if hasattr(self, 'startup_with_system') else False
        }
        
        return settings
    
    def nextId(self):
        """Go to complete page"""
        return 4  # Index of CompletePage


# Need sys import at top
import sys
