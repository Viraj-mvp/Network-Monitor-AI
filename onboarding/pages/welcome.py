"""
Welcome Page - First page of setup wizard
"""

from PySide6.QtWidgets import (
    QWizardPage, QVBoxLayout, QLabel, QPushButton, 
    QHBoxLayout, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class WelcomePage(QWizardPage):
    """Welcome page introducing the app"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("")
        self.setSubTitle("")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # App icon/logo placeholder
        icon_label = QLabel("🔒")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_font = QFont()
        icon_font.setPointSize(48)
        icon_label.setFont(icon_font)
        layout.addWidget(icon_label)
        
        # Welcome title
        title = QLabel("Welcome to Network AI Monitor")
        title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("AI-Powered Network Security & Monitoring")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)
        subtitle.setFont(subtitle_font)
        layout.addWidget(subtitle)
        
        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Description
        desc = QLabel(
            "Let's get you set up in just a few steps.\n\n"
            "Network AI Monitor will:\n"
            "  • Monitor your network interfaces in real-time\n"
            "  • Detect suspicious traffic patterns using AI\n" 
            "  • Send email alerts for anomalies\n"
            "  • Log network activity for analysis"
        )
        desc.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        desc_font = QFont()
        desc_font.setPointSize(12)
        desc.setFont(desc_font)
        layout.addWidget(desc)
        
        # Spacer
        layout.addStretch()
        
        # Get started button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.get_started_btn = QPushButton("Get Started →")
        self.get_started_btn.setMinimumSize(200, 50)
        btn_font = QFont()
        btn_font.setPointSize(14)
        btn_font.setBold(True)
        self.get_started_btn.setFont(btn_font)
        self.get_started_btn.clicked.connect(self.go_to_next_page)
        button_layout.addWidget(self.get_started_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        self.setLayout(layout)
    
    def go_to_next_page(self):
        """Proceed to next page"""
        self.wizard().next()
    
    def isComplete(self):
        """Always complete (no validation needed)"""
        return True
    
    def nextId(self):
        """Go to monitoring settings page"""
        return 1  # Index of MonitoringPage
