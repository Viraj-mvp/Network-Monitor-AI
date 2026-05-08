"""
System Tray Manager - Handle tray icon and menu
"""

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QWidget, QApplication
from PySide6.QtGui import QAction
from PySide6.QtCore import Signal, QObject
from PySide6.QtGui import QIcon, QPixmap

from utils.resources import resource_path


class SystemTray(QObject):
    """System tray icon with context menu"""
    
    # Signals
    show_requested = Signal()
    hide_requested = Signal()
    start_monitoring_requested = Signal()
    stop_monitoring_requested = Signal()
    settings_requested = Signal()
    exit_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._tray_icon = None
        self._menu = None
        self._is_monitoring = False
        self._has_alerts = False
        
        self._create_tray_icon()
    
    def _create_tray_icon(self):
        """Create and configure the system tray icon"""
        self._tray_icon = QSystemTrayIcon(self.parent())
        
        # Set icon
        self._update_icon()
        
        # Create context menu
        self._create_menu()
        self._tray_icon.setContextMenu(self._menu)
        
        # Connect signals
        self._tray_icon.activated.connect(self._on_activated)
        self._tray_icon.messageClicked.connect(self._on_message_clicked)
    
    def _create_menu(self):
        """Create the context menu"""
        self._menu = QMenu()
        self._menu.setStyleSheet("""
            QMenu {
                padding: 8px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #e3f2fd;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e0e0e0;
                margin: 8px 0px;
            }
        """)
        
        # App name (disabled)
        self._app_action = QAction("Network AI Monitor", self)
        self._app_action.setEnabled(False)
        font = self._app_action.font()
        font.setBold(True)
        self._app_action.setFont(font)
        self._menu.addAction(self._app_action)
        
        self._menu.addSeparator()
        
        # Show/Hide
        self._show_action = QAction("Show Dashboard", self)
        self._show_action.triggered.connect(self.show_requested.emit)
        self._menu.addAction(self._show_action)
        
        self._hide_action = QAction("Hide to Tray", self)
        self._hide_action.triggered.connect(self.hide_requested.emit)
        self._menu.addAction(self._hide_action)
        
        self._menu.addSeparator()
        
        # Monitoring controls
        self._start_action = QAction("▶ Start Monitoring", self)
        self._start_action.triggered.connect(self.start_monitoring_requested.emit)
        self._menu.addAction(self._start_action)
        
        self._stop_action = QAction("⏹ Stop Monitoring", self)
        self._stop_action.triggered.connect(self.stop_monitoring_requested.emit)
        self._stop_action.setVisible(False)
        self._menu.addAction(self._stop_action)
        
        self._menu.addSeparator()
        
        # Settings
        self._settings_action = QAction("⚙️ Settings", self)
        self._settings_action.triggered.connect(self.settings_requested.emit)
        self._menu.addAction(self._settings_action)
        
        self._menu.addSeparator()
        
        # Exit
        self._exit_action = QAction("Exit", self)
        self._exit_action.triggered.connect(self.exit_requested.emit)
        self._menu.addAction(self._exit_action)
    
    def _update_icon(self):
        """Update tray icon based on state"""
        try:
            icon_path = resource_path('assets/icon.ico')
            icon = QIcon(icon_path)
            
            # TODO: Create different icon states (normal, monitoring, alert)
            # For now, use same icon
            
            self._tray_icon.setIcon(icon)
            self._tray_icon.setToolTip(self._get_tooltip())
        except Exception as e:
            print(f"Error setting tray icon: {e}")
    
    def _get_tooltip(self) -> str:
        """Get tooltip text based on current state"""
        lines = ["Network AI Monitor"]
        
        if self._is_monitoring:
            lines.append("Status: Monitoring")
        else:
            lines.append("Status: Stopped")
        
        if self._has_alerts:
            lines.append("⚠️ Alerts pending")
        
        return "\n".join(lines)
    
    def _on_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            # Double-click shows/hides the window
            self.show_requested.emit()
        elif reason == QSystemTrayIcon.Trigger:
            # Single click - could show status tooltip or menu
            pass
    
    def _on_message_clicked(self):
        """Handle click on notification message"""
        self.show_requested.emit()
    
    def show(self):
        """Show the tray icon"""
        if self._tray_icon:
            self._tray_icon.show()
    
    def hide(self):
        """Hide the tray icon"""
        if self._tray_icon:
            self._tray_icon.hide()
    
    def set_monitoring_state(self, is_monitoring: bool):
        """Update tray to reflect monitoring state"""
        self._is_monitoring = is_monitoring
        
        # Update menu actions
        self._start_action.setVisible(not is_monitoring)
        self._stop_action.setVisible(is_monitoring)
        
        # Update icon and tooltip
        self._update_icon()
    
    def set_alert_state(self, has_alerts: bool):
        """Update tray to reflect alert state"""
        self._has_alerts = has_alerts
        self._update_icon()
    
    def show_notification(self, title: str, message: str, 
                         icon=QSystemTrayIcon.Information, 
                         duration_ms=5000):
        """
        Show a system notification
        
        Args:
            title: Notification title
            message: Notification body
            icon: Icon type (Information, Warning, Critical)
            duration_ms: How long to show (0 = system default)
        """
        if self._tray_icon and self._tray_icon.supportsMessages():
            self._tray_icon.showMessage(title, message, icon, duration_ms)
    
    def show_alert_notification(self, iface: str, status: str):
        """Show notification for network alert"""
        title = f"⚠️ Network Alert: {iface}"
        message = f"Anomaly detected: {status}"
        self.show_notification(title, message, QSystemTrayIcon.Warning, 10000)
    
    def is_visible(self) -> bool:
        """Check if tray icon is visible"""
        return self._tray_icon.isVisible() if self._tray_icon else False
    
    def is_system_tray_available(self) -> bool:
        """Check if system tray is available on this system"""
        return QSystemTrayIcon.isSystemTrayAvailable()
