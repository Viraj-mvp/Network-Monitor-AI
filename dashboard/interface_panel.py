# dashboard/interface_panel.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from dashboard.widgets import GaugeWidget, TrafficGraph

class InterfacePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("networkPanel")
        self.interface_cards = {}
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QLabel("Network Interfaces")
        header.setObjectName("panelHeader")
        header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(header)
        
        # Scroll area for interfaces
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("networkScrollArea")
        self.scroll_area.setWidgetResizable(True)
        
        self.interfaces_container = QWidget()
        self.interfaces_container.setObjectName("networkListContainer")
        self.interfaces_container.setAttribute(Qt.WA_StyledBackground, True)
        self.interfaces_layout = QVBoxLayout(self.interfaces_container)
        self.interfaces_layout.setContentsMargins(10, 10, 10, 10)
        self.interfaces_layout.setSpacing(15)
        
        self.scroll_area.setWidget(self.interfaces_container)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)
    
    def update_data(self, data):
        # data is expected to be a dict: {iface: {'in': value, 'out': value}}
        for iface, traffic_data in data.items():
            if iface not in self.interface_cards:
                # Create new card
                card = self.create_interface_card(iface, traffic_data)
                self.interface_cards[iface] = card
                self.interfaces_layout.addWidget(card)
            else:
                # Update existing card
                self.update_interface_card(iface, traffic_data)
        
        # Remove cards for interfaces that no longer exist
        current_interfaces = set(data.keys())
        existing_interfaces = set(self.interface_cards.keys())
        
        for missing_iface in existing_interfaces - current_interfaces:
            card = self.interface_cards.pop(missing_iface)
            card.deleteLater()
        
        # Add stretch at the end
        if self.interfaces_layout.count() == 0 or \
           not isinstance(self.interfaces_layout.itemAt(self.interfaces_layout.count() - 1), QSpacerItem):
            self.interfaces_layout.addStretch()
    
    def create_interface_card(self, iface_name, data):
        card = QGroupBox(iface_name)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        layout = QGridLayout()
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setSpacing(10)
        
        # Traffic gauges
        max_in = 10.0  # You can make this configurable
        max_out = 5.0
        
        inbound_gauge = GaugeWidget("Inbound", data.get('in', 0), max_value=max_in, unit="Mbps")
        outbound_gauge = GaugeWidget("Outbound", data.get('out', 0), max_value=max_out, unit="Mbps")
        
        layout.addWidget(inbound_gauge, 0, 0)
        layout.addWidget(outbound_gauge, 0, 1)
        
        # Status indicator
        status_label = QLabel()
        status_label.setObjectName("statusLabel")
        status = self.get_status(data)
        status_label.setText(f"Status: {status}")
        
        # Initial color set via property or dynamic stylesheet managed by theme
        self._update_status_style(status_label, status)
        
        layout.addWidget(status_label, 1, 0, 1, 2)
        
        # Mini graph
        graph = TrafficGraph()
        graph.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        graph.add_data(data.get('in', 0), data.get('out', 0))
        layout.addWidget(graph, 2, 0, 1, 2)
        
        # Store references for updating
        card.inbound_gauge = inbound_gauge
        card.outbound_gauge = outbound_gauge
        card.graph = graph
        card.status_label = status_label
        
        card.setLayout(layout)
        return card

    def _update_status_style(self, label, status):
        color = "#28a745" if status == "NORMAL" else "#dc3545"
        label.setStyleSheet(f"""
            QLabel#statusLabel {{
                background-color: {color};
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
                margin: 5px;
            }}
        """)
    
    def update_interface_card(self, iface_name, data):
        card = self.interface_cards.get(iface_name)
        if not card:
            return
        
        # Update gauges
        if hasattr(card, 'inbound_gauge'):
            card.inbound_gauge.value = data.get('in', 0)
            card.inbound_gauge.update()
        
        if hasattr(card, 'outbound_gauge'):
            card.outbound_gauge.value = data.get('out', 0)
            card.outbound_gauge.update()
        
        # Update graph
        if hasattr(card, 'graph'):
            card.graph.add_data(data.get('in', 0), data.get('out', 0))
        
        # Update status
        if hasattr(card, 'status_label'):
            status = self.get_status(data)
            card.status_label.setText(f"Status: {status}")
            self._update_status_style(card.status_label, status)
    
    def get_status(self, data):
        # Use the status provided by the detector if available
        if 'status' in data:
            return data['status']
            
        inbound = data.get('in', 0)
        outbound = data.get('out', 0)
        
        # Simple threshold logic fallback
        if inbound > 5.0:
            return "ANOMALY_INBOUND"
        elif outbound > 2.0:
            return "ANOMALY_OUTBOUND"
        else:
            return "NORMAL"