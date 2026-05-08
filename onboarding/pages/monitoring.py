"""
Monitoring Settings Page - Configure network monitoring
"""

from PySide6.QtWidgets import (
    QWizardPage, QVBoxLayout, QLabel, QComboBox, 
    QSpinBox, QDoubleSpinBox, QFormLayout, QGroupBox,
    QHBoxLayout, QSlider, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from utils.validators import get_network_interfaces, validate_monitoring_interval, validate_threshold


class MonitoringPage(QWizardPage):
    """Page for configuring monitoring settings"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Monitoring Settings")
        self.setSubTitle("Configure how Network AI Monitor watches your network traffic")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Network Interface Selection
        interface_group = QGroupBox("Network Interface")
        interface_layout = QFormLayout()
        
        self.interface_combo = QComboBox()
        self.interface_combo.setMinimumWidth(300)
        self.load_interfaces()
        interface_layout.addRow("Interface to monitor:", self.interface_combo)
        
        # Info label
        self.interface_info = QLabel("Auto-detect will monitor all active interfaces")
        self.interface_info.setWordWrap(True)
        self.interface_info.setStyleSheet("color: gray; font-size: 11px;")
        interface_layout.addRow("", self.interface_info)
        
        interface_group.setLayout(interface_layout)
        layout.addWidget(interface_group)
        
        # Monitoring Interval
        interval_group = QGroupBox("Monitoring Interval")
        interval_layout = QFormLayout()
        
        interval_widget = QWidget()
        interval_hbox = QHBoxLayout(interval_widget)
        interval_hbox.setContentsMargins(0, 0, 0, 0)
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 300)
        self.interval_spin.setValue(5)
        self.interval_spin.setSuffix(" seconds")
        self.interval_spin.setMinimumWidth(150)
        self.interval_spin.valueChanged.connect(self.on_interval_changed)
        interval_hbox.addWidget(self.interval_spin)
        
        self.interval_slider = QSlider(Qt.Horizontal)
        self.interval_slider.setRange(1, 60)
        self.interval_slider.setValue(5)
        self.interval_slider.valueChanged.connect(self.on_slider_changed)
        interval_hbox.addWidget(self.interval_slider, 1)
        
        interval_layout.addRow("Check interval:", interval_widget)
        
        self.interval_desc = QLabel("Lower = more responsive but higher CPU usage")
        self.interval_desc.setStyleSheet("color: gray; font-size: 11px;")
        interval_layout.addRow("", self.interval_desc)
        
        interval_group.setLayout(interval_layout)
        layout.addWidget(interval_group)
        
        # AI Sensitivity
        sensitivity_group = QGroupBox("AI Sensitivity")
        sensitivity_layout = QVBoxLayout()
        
        self.sensitivity_combo = QComboBox()
        self.sensitivity_combo.addItem("Low - Fewer alerts, higher thresholds", "low")
        self.sensitivity_combo.addItem("Medium - Balanced detection", "medium")
        self.sensitivity_combo.addItem("High - More alerts, lower thresholds", "high")
        self.sensitivity_combo.setCurrentIndex(1)  # Default medium
        sensitivity_layout.addWidget(self.sensitivity_combo)
        
        sensitivity_desc = QLabel(
            "Higher sensitivity detects more potential threats but may increase false positives."
        )
        sensitivity_desc.setWordWrap(True)
        sensitivity_desc.setStyleSheet("color: gray; font-size: 11px;")
        sensitivity_layout.addWidget(sensitivity_desc)
        
        sensitivity_group.setLayout(sensitivity_layout)
        layout.addWidget(sensitivity_group)
        
        # Threshold Settings
        threshold_group = QGroupBox("Traffic Thresholds (for Anomaly Detection)")
        threshold_layout = QFormLayout()
        
        # WiFi thresholds
        wifi_label = QLabel("WiFi Interfaces:")
        wifi_font = QFont()
        wifi_font.setBold(True)
        wifi_label.setFont(wifi_font)
        threshold_layout.addRow(wifi_label)
        
        self.wifi_in_spin = QDoubleSpinBox()
        self.wifi_in_spin.setRange(0, 1000)
        self.wifi_in_spin.setValue(1.0)
        self.wifi_in_spin.setSuffix(" Mbps")
        self.wifi_in_spin.setDecimals(1)
        threshold_layout.addRow("  Inbound threshold:", self.wifi_in_spin)
        
        self.wifi_out_spin = QDoubleSpinBox()
        self.wifi_out_spin.setRange(0, 1000)
        self.wifi_out_spin.setValue(0.5)
        self.wifi_out_spin.setSuffix(" Mbps")
        self.wifi_out_spin.setDecimals(1)
        threshold_layout.addRow("  Outbound threshold:", self.wifi_out_spin)
        
        # Ethernet thresholds
        eth_label = QLabel("Ethernet Interfaces:")
        eth_font = QFont()
        eth_font.setBold(True)
        eth_label.setFont(eth_font)
        threshold_layout.addRow(eth_label)
        
        self.eth_in_spin = QDoubleSpinBox()
        self.eth_in_spin.setRange(0, 1000)
        self.eth_in_spin.setValue(5.0)
        self.eth_in_spin.setSuffix(" Mbps")
        self.eth_in_spin.setDecimals(1)
        threshold_layout.addRow("  Inbound threshold:", self.eth_in_spin)
        
        self.eth_out_spin = QDoubleSpinBox()
        self.eth_out_spin.setRange(0, 1000)
        self.eth_out_spin.setValue(2.0)
        self.eth_out_spin.setSuffix(" Mbps")
        self.eth_out_spin.setDecimals(1)
        threshold_layout.addRow("  Outbound threshold:", self.eth_out_spin)
        
        threshold_note = QLabel(
            "Traffic above these thresholds will trigger AI analysis. "
            "You can change these later in Settings."
        )
        threshold_note.setWordWrap(True)
        threshold_note.setStyleSheet("color: gray; font-size: 11px; margin-top: 10px;")
        threshold_layout.addRow("", threshold_note)
        
        threshold_group.setLayout(threshold_layout)
        layout.addWidget(threshold_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Connect interface combo to update info
        self.interface_combo.currentIndexChanged.connect(self.on_interface_changed)
    
    def load_interfaces(self):
        """Load available network interfaces"""
        self.interface_combo.clear()
        self.interface_combo.addItem("Auto-detect (Recommended)", "auto")
        
        interfaces = get_network_interfaces()
        for iface in interfaces:
            status = "🟢" if iface['is_up'] else "🔴"
            display = f"{status} {iface['display_name']}"
            self.interface_combo.addItem(display, iface['name'])
    
    def on_interface_changed(self, index):
        """Update info when interface selection changes"""
        data = self.interface_combo.currentData()
        if data == "auto":
            self.interface_info.setText("Auto-detect will monitor all active interfaces")
        else:
            self.interface_info.setText(f"Monitoring specific interface: {data}")
    
    def on_interval_changed(self, value):
        """Sync slider with spinbox"""
        self.interval_slider.setValue(min(value, 60))
    
    def on_slider_changed(self, value):
        """Sync spinbox with slider"""
        self.interval_spin.setValue(value)
    
    def isComplete(self):
        """Validate all fields"""
        # Interval validation
        interval = self.interval_spin.value()
        valid, _ = validate_monitoring_interval(interval)
        if not valid:
            return False
        
        # Threshold validation
        for spin in [self.wifi_in_spin, self.wifi_out_spin, self.eth_in_spin, self.eth_out_spin]:
            valid, _ = validate_threshold(spin.value())
            if not valid:
                return False
        
        return True
    
    def validatePage(self):
        """Validate before proceeding"""
        return self.isComplete()
    
    def get_settings(self) -> dict:
        """Get monitoring settings from page"""
        sensitivity_map = {
            "low": {"wifi_in": 2.0, "wifi_out": 1.0, "eth_in": 10.0, "eth_out": 5.0},
            "medium": {"wifi_in": 1.0, "wifi_out": 0.5, "eth_in": 5.0, "eth_out": 2.0},
            "high": {"wifi_in": 0.5, "wifi_out": 0.25, "eth_in": 2.5, "eth_out": 1.0}
        }
        
        sensitivity = self.sensitivity_combo.currentData()
        defaults = sensitivity_map.get(sensitivity, sensitivity_map["medium"])
        
        return {
            'interface': self.interface_combo.currentData(),
            'interval': self.interval_spin.value(),
            'ai_sensitivity': sensitivity,
            'wifi_threshold_in': self.wifi_in_spin.value(),
            'wifi_threshold_out': self.wifi_out_spin.value(),
            'ethernet_threshold_in': self.eth_in_spin.value(),
            'ethernet_threshold_out': self.eth_out_spin.value()
        }
    
    def nextId(self):
        """Go to email settings page"""
        return 2  # Index of EmailPage
