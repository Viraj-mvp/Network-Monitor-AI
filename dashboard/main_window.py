# dashboard/main_window.py (simplified version)
import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import darkdetect

# Import our panels
from dashboard.interface_panel import InterfacePanel
from dashboard.alert_panel import AlertPanel
from dashboard.log_viewer import LogViewer
from dashboard.settings_panel import SettingsPanel
from dashboard.theme import ThemeManager

# Import core modules
from core.network_monitor import get_interfaces_bandwidth_mbps
from core.ai_engine import InterfaceThresholdDetector
from core.email_alert import send_email_alert

class MonitoringWorker(QObject):
    data_ready = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, detector, thresholds):
        super().__init__()
        self.detector = detector
        self.thresholds = thresholds
        self.email_enabled = False
        self.receiver_email = ""

    @Slot()
    def fetch_data(self):
        try:
            data = get_interfaces_bandwidth_mbps()
            
            # Process anomalies
            for iface, traffic in data.items():
                th_key = 'WiFi' if 'wlan' in iface.lower() or 'wi-fi' in iface.lower() else \
                         'Ethernet' if 'eth' in iface.lower() or 'ethernet' in iface.lower() else 'Default'
                
                if iface not in self.detector.thresholds:
                    self.detector.thresholds[iface] = self.thresholds.get(th_key, self.thresholds.get('Default'))
                
                status = self.detector.predict(iface, traffic['in'], traffic['out'])
                data[iface]['status'] = status
                
                if status != "NORMAL" and self.email_enabled and self.receiver_email:
                    # In a real app, we'd throttle these emails
                    try:
                        alert_msg = f"Anomaly detected on {iface}: {status} (In: {traffic['in']:.2f} Mbps, Out: {traffic['out']:.2f} Mbps)"
                        send_email_alert(f"Network Anomaly: {iface}", alert_msg)
                    except Exception:
                        pass # Silently fail for background emails
            
            self.data_ready.emit(data)
        except Exception as e:
            self.error_occurred.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Network Monitor - Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize monitoring state
        self.monitoring_active = False
        self.thresholds = {
            'WiFi': {'in': 1.0, 'out': 0.5},
            'Ethernet': {'in': 5.0, 'out': 2.0},
            'Default': {'in': 2.0, 'out': 1.0}
        }
        self.detector = InterfaceThresholdDetector(self.thresholds)
        
        # Setup worker thread
        self.worker_thread = QThread()
        self.worker = MonitoringWorker(self.detector, self.thresholds)
        self.worker.moveToThread(self.worker_thread)
        self.worker.data_ready.connect(self.handle_monitoring_data)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker_thread.start()
        
        # Create a timer for data updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.worker.fetch_data)
        
        # Setup UI
        self.setup_ui()
        
        # Apply initial theme
        self.theme_manager = ThemeManager()
        self.theme_manager.set_theme('dark' if darkdetect.isDark() else 'light')
    
    def setup_ui(self):
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        self.setup_central_widget()

    def setup_menu(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        file_menu.addAction("Export Logs...")
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)
        
        # View menu
        view_menu = menubar.addMenu("View")
        view_menu.addAction("Dark Theme", lambda: self.theme_manager.set_theme('dark'))
        view_menu.addAction("Light Theme", lambda: self.theme_manager.set_theme('light'))
    
    def setup_toolbar(self):
        toolbar = self.addToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        
        # Start/Stop buttons
        self.start_btn = QAction("▶ Start Monitoring", self)
        self.start_btn.triggered.connect(self.start_monitoring)
        toolbar.addAction(self.start_btn)
        
        self.stop_btn = QAction("⏹ Stop Monitoring", self)
        self.stop_btn.triggered.connect(self.stop_monitoring)
        self.stop_btn.setEnabled(False)
        toolbar.addAction(self.stop_btn)
        
        toolbar.addSeparator()
        toolbar.addAction("Refresh", self.refresh_data)
    
    def setup_statusbar(self):
        self.status_bar = self.statusBar()
        
        # Status indicators
        self.status_label = QLabel("Stopped")
        self.status_label.setStyleSheet("padding: 5px; background-color: #dc3545; color: white; border-radius: 3px;")
        self.status_bar.addWidget(self.status_label)
        
        # Interface count
        self.interface_label = QLabel("Interfaces: 0")
        self.status_bar.addPermanentWidget(self.interface_label)
        
        # Alert count
        self.alert_label = QLabel("Alerts: 0")
        self.status_bar.addPermanentWidget(self.alert_label)
    
    def setup_central_widget(self):
        # Create main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel: Interface monitoring
        self.interface_panel = InterfacePanel()
        main_splitter.addWidget(self.interface_panel)
        
        # Right panel: Tab widget
        right_tabs = QTabWidget()
        
        # Alert panel
        self.alert_panel = AlertPanel()
        right_tabs.addTab(self.alert_panel, "Alerts")
        
        # Log viewer
        self.log_viewer = LogViewer()
        right_tabs.addTab(self.log_viewer, "Logs")
        
        # Settings panel
        self.settings_panel = SettingsPanel()
        self.settings_panel.settings_changed.connect(self.update_settings)
        right_tabs.addTab(self.settings_panel, "Settings")
        
        main_splitter.addWidget(right_tabs)
        
        # Set initial sizes
        main_splitter.setSizes([700, 700])
        
        self.setCentralWidget(main_splitter)

    def update_settings(self, settings):
        """Handle settings changes from the settings panel"""
        self.thresholds = settings.get("thresholds", self.thresholds)
        email_settings = settings.get("email", {})
        self.email_enabled = email_settings.get("enabled", False)
        self.receiver_email = email_settings.get("receiver", "")
        
        # Update worker and detector
        if hasattr(self, 'worker'):
            self.worker.thresholds = self.thresholds
            self.worker.email_enabled = self.email_enabled
            self.worker.receiver_email = self.receiver_email
            self.detector.thresholds.update(self.thresholds)
            
        self.log_viewer.log_message("Application settings updated.")

    def handle_monitoring_data(self, data):
        """Update UI with data from worker thread with basic memoization"""
        if not hasattr(self, '_prev_data_hash'):
            self._prev_data_hash = None
            
        import hashlib
        import json
        current_hash = hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
        
        if current_hash == self._prev_data_hash:
            return
            
        self._prev_data_hash = current_hash
        
        for iface, traffic in data.items():
            status = traffic.get('status', 'NORMAL')
            if status != "NORMAL":
                alert_msg = f"Anomaly detected on {iface}: {status} (In: {traffic['in']:.2f} Mbps, Out: {traffic['out']:.2f} Mbps)"
                print(f"⚠️  ALERT: {alert_msg}")  # Restore terminal alert
                self.alert_panel.add_alert(iface, status, alert_msg)
                self.log_viewer.log_message(alert_msg, "WARNING")
        
        self.interface_panel.update_data(data)
        self.interface_label.setText(f"Interfaces: {len(data)}")

    def handle_error(self, error_msg):
        self.log_viewer.log_message(f"Monitoring error: {error_msg}", "ERROR")
    
    def start_monitoring(self):
        self.monitoring_active = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("Monitoring")
        self.status_label.setStyleSheet("padding: 5px; background-color: #28a745; color: white; border-radius: 3px;")
        self.timer.start(1000)
        self.log_viewer.log_message("Network monitoring started.")
        print("Monitoring started")
    
    def stop_monitoring(self):
        self.monitoring_active = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Stopped")
        self.status_label.setStyleSheet("padding: 5px; background-color: #dc3545; color: white; border-radius: 3px;")
        self.timer.stop()
        self.log_viewer.log_message("Network monitoring stopped.")
        print("Monitoring stopped")
    
    def closeEvent(self, event):
        """Clean up threads on close"""
        self.worker_thread.quit()
        self.worker_thread.wait()
        super().closeEvent(event)

    def refresh_data(self):
        if self.monitoring_active:
            self.worker.fetch_data()
    
    def update_monitoring_data(self):
        """Replaced by worker thread logic"""
        pass