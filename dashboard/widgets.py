# dashboard/widgets.py
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import pyqtgraph as pg
import numpy as np
from dashboard.theme import ThemeManager

class GaugeWidget(QWidget):
    def __init__(self, title, value, max_value=10, unit="Mbps"):
        super().__init__()
        self.title = title
        self.value = value
        self.max_value = max_value
        self.unit = unit
        self.setMinimumSize(150, 150)
        
        # Connect to theme changes
        self.theme = ThemeManager()
        self.theme.theme_interpolating.connect(self.update)
        self.theme.theme_changed.connect(self.update)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Colors from theme
        bg_color = self.theme.get_color('gauge_bg')
        text_color = self.theme.get_color('text')
        accent_color = self.theme.get_color('accent_secondary')
        
        # Calculate percentage
        percent = min(self.value / self.max_value, 1.0)
        
        # Draw gauge background
        rect = QRect(10, 10, self.width() - 20, self.height() - 50)
        painter.setPen(QPen(bg_color.darker(120), 2))
        painter.setBrush(bg_color)
        painter.drawEllipse(rect)
        
        # Draw gauge value
        color = self.get_color(percent)
        painter.setPen(QPen(color, 8))
        start_angle = 90 * 16
        span_angle = -percent * 360 * 16
        painter.drawArc(rect, start_angle, span_angle)
        
        # Draw text
        painter.setPen(text_color)
        painter.setFont(QFont("Segoe UI", 10))
        
        # Title
        painter.drawText(0, self.height() - 30, self.width(), 20,
                         Qt.AlignCenter, self.title)
        
        # Value
        value_text = f"{self.value:.2f} {self.unit}"
        painter.setFont(QFont("Segoe UI", 14, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, value_text)
    
    def get_color(self, percent):
        if percent < 0.5:
            return QColor(40, 167, 69)  # Green
        elif percent < 0.8:
            return QColor(255, 193, 7)   # Yellow
        else:
            return QColor(220, 53, 69)   # Red

class TrafficGraph(QWidget):
    def __init__(self, history_size=20):
        super().__init__()
        self.history_size = history_size
        self.inbound_data = []
        self.outbound_data = []
        self.setMinimumHeight(80)
        self.setMaximumHeight(120)
        
        # Connect to theme changes
        self.theme = ThemeManager()
        self.theme.theme_interpolating.connect(self.update)
        self.theme.theme_changed.connect(self.update)
    
    def add_data(self, inbound, outbound):
        self.inbound_data.append(inbound)
        self.outbound_data.append(outbound)
        
        # Keep only last N values
        if len(self.inbound_data) > self.history_size:
            self.inbound_data = self.inbound_data[-self.history_size:]
            self.outbound_data = self.outbound_data[-self.history_size:]
        
        self.update()
    
    def paintEvent(self, event):
        if len(self.inbound_data) < 2:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        margin = 10
        
        # Colors from theme
        bg_color = self.theme.get_color('surface')
        grid_color = self.theme.get_color('border')
        
        # Draw background
        painter.fillRect(0, 0, width, height, bg_color)
        
        # Split height into two sections
        graph_height = (height - 2 * margin) / 2
        mid_y = margin + graph_height
        
        # Draw separator line
        painter.setPen(QPen(grid_color, 1, Qt.SolidLine))
        painter.drawLine(margin, mid_y, width - margin, mid_y)
        
        # Calculate scaling for each section
        max_in = max(self.inbound_data or [0.1])
        max_out = max(self.outbound_data or [0.1])
        max_val = max(max_in, max_out, 0.1)
        
        # Draw grid for both sections
        painter.setPen(QPen(grid_color, 1, Qt.DashLine))
        for i in range(1, 3):
            # Upper section grid
            y_up = margin + (graph_height * i / 3)
            painter.drawLine(margin, y_up, width - margin, y_up)
            # Lower section grid
            y_down = mid_y + (graph_height * i / 3)
            painter.drawLine(margin, y_down, width - margin, y_down)
        
        # Draw inbound line (Upper section)
        if len(self.inbound_data) > 1:
            self.draw_line(painter, self.inbound_data, max_val, 
                          QColor(0, 200, 255), "Inbound", width, graph_height, margin, offset_y=margin)
        
        # Draw outbound line (Lower section)
        if len(self.outbound_data) > 1:
            self.draw_line(painter, self.outbound_data, max_val,
                          QColor(255, 100, 100), "Outbound", width, graph_height, margin, offset_y=mid_y)
    
    def draw_line(self, painter, data, max_value, color, label, width, section_height, margin, offset_y):
        painter.setPen(QPen(color, 2))
        
        points = []
        for i, value in enumerate(data):
            x = margin + (width - 2 * margin) * i / (len(data) - 1) if len(data) > 1 else width // 2
            # Scale value to fit within section_height
            normalized_val = (value / max_value) if max_value > 0 else 0
            y = offset_y + section_height - (section_height * normalized_val)
            points.append(QPointF(x, y))
        
        path = QPainterPath()
        if points:
            path.moveTo(points[0])
            for point in points[1:]:
                path.lineTo(point)
            painter.drawPath(path)
        
        # Draw label
        painter.setPen(color)
        painter.setFont(QFont("Segoe UI", 8, QFont.Bold))
        painter.drawText(margin + 5, offset_y + 15, label)

class PyQtGraphWidget(pg.PlotWidget):
    """Alternative using pyqtgraph for better performance"""
    def __init__(self):
        super().__init__()
        self.theme = ThemeManager()
        self.theme.theme_interpolating.connect(self.update_theme)
        self.theme.theme_changed.connect(self.update_theme)
        self.update_theme()
        
        self.showGrid(x=True, y=True, alpha=0.3)
        self.setLabel('left', 'Mbps')
        self.setLabel('bottom', 'Time')
        
        self.inbound_curve = self.plot(pen='c', name='Inbound')
        self.outbound_curve = self.plot(pen='r', name='Outbound')
        
        self.inbound_data = []
        self.outbound_data = []
        self.timestamps = []
    
    def update_theme(self):
        bg = self.theme.get_color('background').name()
        text = self.theme.get_color('text').name()
        self.setBackground(bg)
        # We'd need to update more pyqtgraph internal pens here if needed

    
    def add_data(self, inbound, outbound):
        from datetime import datetime
        self.timestamps.append(datetime.now())
        self.inbound_data.append(inbound)
        self.outbound_data.append(outbound)
        
        # Keep last 50 points
        keep = 50
        if len(self.timestamps) > keep:
            self.timestamps = self.timestamps[-keep:]
            self.inbound_data = self.inbound_data[-keep:]
            self.outbound_data = self.outbound_data[-keep:]
        
        # Update plot
        x = list(range(len(self.timestamps)))
        self.inbound_curve.setData(x, self.inbound_data)
        self.outbound_curve.setData(x, self.outbound_data)