"""
Splash Screen - Shown during application startup
"""

from PySide6.QtWidgets import QSplashScreen, QLabel, QVBoxLayout, QWidget, QProgressBar, QGraphicsDropShadowEffect, QApplication
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QLinearGradient, QBrush, QColor

from utils.resources import resource_path


class SplashScreen(QSplashScreen):
    """Custom splash screen with progress indicator"""
    
    def __init__(self, parent=None):
        # Create pixmap for splash
        self.splash_pixmap = self._create_splash_pixmap()
        super().__init__(pixmap=self.splash_pixmap)
        
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint |
            Qt.SplashScreen
        )
        
        # Setup UI elements on top of pixmap
        self._setup_ui()
        
        # Progress animation
        self._progress = 0
        self._loading_messages = [
            "Initializing...",
            "Loading configuration...",
            "Setting up network monitor...",
            "Preparing dashboard...",
            "Ready!"
        ]
        self._current_message = 0
    
    def _create_splash_pixmap(self) -> QPixmap:
        """Create the splash screen background"""
        # Create a 500x300 pixmap with gradient background
        pixmap = QPixmap(500, 300)
        
        # Paint gradient background
        painter = QPainter(pixmap)
        gradient = QLinearGradient(0, 0, 0, 300)
        gradient.setColorAt(0, QColor("#2196F3"))  # Blue
        gradient.setColorAt(1, QColor("#1976D2"))  # Darker blue
        painter.fillRect(pixmap.rect(), QBrush(gradient))
        
        # Add app icon/logo
        try:
            icon_path = resource_path('assets/icon.ico')
            icon = QPixmap(icon_path)
            if not icon.isNull():
                icon = icon.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                x = (500 - icon.width()) // 2
                painter.drawPixmap(x, 40, icon)
        except Exception:
            pass  # Draw without icon if not available
        
        # Draw app name
        font = QFont("Segoe UI", 24, QFont.Bold)
        painter.setFont(font)
        painter.setPen(Qt.white)
        painter.drawText(pixmap.rect().adjusted(0, 130, 0, 0), Qt.AlignHCenter | Qt.AlignTop, 
                        "Network AI Monitor")
        
        # Draw subtitle
        font = QFont("Segoe UI", 12)
        painter.setFont(font)
        painter.drawText(pixmap.rect().adjusted(0, 170, 0, 0), Qt.AlignHCenter | Qt.AlignTop,
                        "AI-Powered Network Security & Monitoring")
        
        # Draw version
        font = QFont("Segoe UI", 10)
        painter.setFont(font)
        painter.drawText(pixmap.rect().adjusted(0, 0, -20, -15), Qt.AlignRight | Qt.AlignBottom,
                        "v1.0.0")
        
        painter.end()
        return pixmap
    
    def _setup_ui(self):
        """Setup UI elements overlay"""
        # Create container widget for overlay elements
        self._container = QWidget(self)
        self._container.setGeometry(0, 220, 500, 80)
        
        layout = QVBoxLayout(self._container)
        layout.setContentsMargins(30, 10, 30, 20)
        layout.setSpacing(8)
        
        # Loading message label
        self._message_label = QLabel("Initializing...")
        self._message_label.setAlignment(Qt.AlignCenter)
        self._message_label.setStyleSheet("""
            color: white;
            font-size: 13px;
            font-family: 'Segoe UI';
        """)
        layout.addWidget(self._message_label)
        
        # Progress bar
        self._progress_bar = QProgressBar(self._container)
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setFixedHeight(4)
        self._progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(255, 255, 255, 0.3);
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: white;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self._progress_bar)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
    
    def show_progress(self, value: int, message: str = None):
        """Update progress bar and message"""
        self._progress = min(value, 100)
        self._progress_bar.setValue(self._progress)
        
        if message:
            self._message_label.setText(message)
        
        self.repaint()
        QApplication.processEvents()
    
    def animate_progress(self, duration_ms: int = 2000):
        """Animate progress from 0 to 100 over duration"""
        self._progress = 0
        self._current_message = 0
        
        steps = len(self._loading_messages)
        interval = duration_ms // steps
        
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_animation)
        self._timer.start(interval)
        
        # Stop timer after full duration
        QTimer.singleShot(duration_ms, self._finish_animation)
    
    def _update_animation(self):
        """Update animation step"""
        if self._current_message < len(self._loading_messages):
            progress = ((self._current_message + 1) / len(self._loading_messages)) * 100
            message = self._loading_messages[self._current_message]
            self.show_progress(int(progress), message)
            self._current_message += 1
    
    def _finish_animation(self):
        """Finish the animation"""
        if hasattr(self, '_timer'):
            self._timer.stop()
        self.show_progress(100, "Ready!")
    
    def finish(self, main_window):
        """Close splash and show main window"""
        super().finish(main_window)


class QProgressBar:
    """Import fix - this should be imported from QtWidgets"""
    pass


# Fix import
from PySide6.QtWidgets import QProgressBar as RealQProgressBar
QProgressBar = RealQProgressBar
