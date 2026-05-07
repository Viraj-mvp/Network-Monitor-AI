from PySide6.QtCore import QThread, Signal
import time
from datetime import datetime
from core.network_stats import get_interfaces_bandwidth_mbps
from core.detector import InterfaceThresholdDetector
from core.alert_manager import AlertManager

class MonitoringService(QThread):
    data_updated = Signal(dict)  # Signal for interface data
    alert_triggered = Signal(dict)  # Signal for alerts
    
    def __init__(self, interval=5):
        super().__init__()
        self.interval = interval
        self.running = False
        
        # Initialize components
        self.detector = InterfaceThresholdDetector()
        self.alert_manager = AlertManager()
    
    def run(self):
        self.running = True
        
        while self.running:
            try:
                # Get network data
                interfaces_data = get_interfaces_bandwidth_mbps()
                
                # Process each interface
                for iface, data in interfaces_data.items():
                    # Detect anomalies
                    status = self.detector.predict(iface, data['in'], data['out'])
                    
                    # Emit data update
                    self.data_updated.emit({iface: data})
                    
                    # Check for alerts
                    if status != "NORMAL":
                        alert_data = {
                            'timestamp': datetime.now().strftime("%H:%M:%S"),
                            'interface': iface,
                            'type': 'INBOUND' if 'INBOUND' in status else 'OUTBOUND',
                            'value': data['in'] if 'INBOUND' in status else data['out'],
                            'status': status
                        }
                        
                        # Check cooldown and send alert
                        if self.alert_manager.should_alert(iface):
                            self.alert_triggered.emit(alert_data)
                            self.alert_manager.send_alert(alert_data)
                
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
    
    def stop(self):
        self.running = False
        self.wait()