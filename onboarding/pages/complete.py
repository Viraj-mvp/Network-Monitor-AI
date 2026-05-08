"""
Complete Page - Final step of setup wizard
"""

from PySide6.QtWidgets import (
    QWizardPage, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QSpacerItem, QSizePolicy, QCheckBox,
    QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class CompletePage(QWizardPage):
    """Final page showing setup completion"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("")
        self.setSubTitle("")
        self._can_finish = False
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Success icon
        icon_label = QLabel("✅")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_font = QFont()
        icon_font.setPointSize(64)
        icon_label.setFont(icon_font)
        layout.addWidget(icon_label)
        
        # Success title
        title = QLabel("You're All Set!")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Network AI Monitor is configured and ready to use")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle.setFont(subtitle_font)
        layout.addWidget(subtitle)
        
        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # What's next
        next_group = QGroupBox("What's Next?")
        next_layout = QVBoxLayout()
        
        next_text = QLabel(
            "After clicking 'Finish':\n\n"
            "1. The main dashboard will open\n"
            "2. Monitoring will begin automatically (if enabled)\n"
            "3. The app will minimize to your system tray\n"
            "4. You'll receive alerts when anomalies are detected"
        )
        next_text.setWordWrap(True)
        next_layout.addWidget(next_text)
        
        # Start on finish checkbox
        self.start_on_finish = QCheckBox("Start monitoring immediately")
        self.start_on_finish.setChecked(True)
        next_layout.addWidget(self.start_on_finish)
        
        next_group.setLayout(next_layout)
        layout.addWidget(next_group)
        
        # Quick tips
        tips_group = QGroupBox("Quick Tips")
        tips_layout = QVBoxLayout()
        
        tips_text = QLabel(
            "• 📊 View real-time traffic in the dashboard\n"
            "• ⚙️ Change settings anytime from the Settings tab\n"
            "• 🔔 Configure which alerts you want to receive\n"
            "• 📁 Find logs and data in the Logs tab\n"
            "• 🚪 Right-click the tray icon for quick actions"
        )
        tips_text.setWordWrap(True)
        tips_layout.addWidget(tips_text)
        
        tips_group.setLayout(tips_layout)
        layout.addWidget(tips_group)
        
        layout.addStretch()
        
        # Finish button area (custom since wizard has its own)
        self.setLayout(layout)
    
    def initializePage(self):
        """Called when page is shown"""
        self._can_finish = True
        self.completeChanged.emit()
    
    def isComplete(self):
        """Allow finish when page is shown"""
        return self._can_finish
    
    def get_start_monitoring(self) -> bool:
        """Get whether to start monitoring on finish"""
        return self.start_on_finish.isChecked()
    
    def nextId(self):
        """No next page - this is the last one"""
        return -1
