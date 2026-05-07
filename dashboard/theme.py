# dashboard/theme.py
from PySide6.QtCore import QObject, Property, QVariantAnimation, Signal, QEasingCurve, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

class ThemePalette:
    def __init__(self, **kwargs):
        self.background = kwargs.get('background', '#ffffff')
        self.surface = kwargs.get('surface', '#f3f3f3')
        self.text = kwargs.get('text', '#333333')
        self.accent_primary = kwargs.get('accent_primary', '#007acc')
        self.accent_secondary = kwargs.get('accent_secondary', '#6200ee')
        self.border = kwargs.get('border', '#cccccc')
        self.card_bg = kwargs.get('card_bg', '#ffffff')
        self.gauge_bg = kwargs.get('gauge_bg', '#e0e0e0')

DARK_PALETTE = {
    'background': '#1e1e1e',
    'surface': '#252526',
    'header_bg': '#2d2d2d',
    'text': '#d4d4d4',
    'disabled_text': '#757575',  # Improved contrast for disabled text
    'accent_primary': '#007acc',
    'accent_secondary': '#bb86fc',
    'border': '#3e3e42',
    'card_bg': '#2d2d2d',
    'network_list_bg': '#1e1e1e',
    'gauge_bg': '#3c3c3c'
}

LIGHT_PALETTE = {
    'background': '#ffffff',
    'surface': '#f3f3f3',
    'header_bg': '#e0e0e0',
    'text': '#333333',
    'disabled_text': '#888888',  # Improved contrast for disabled text
    'accent_primary': '#005c99',
    'accent_secondary': '#4a148c',
    'border': '#cccccc',
    'card_bg': '#ffffff',
    'network_list_bg': '#f9f9f9',
    'gauge_bg': '#e0e0e0'
}

class ThemeManager(QObject):
    theme_changed = Signal()
    theme_interpolating = Signal()
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized: return
        super().__init__()
        self._initialized = True
        self.current_theme = 'dark'
        self.colors = DARK_PALETTE.copy()
        
        self.animation = QVariantAnimation(self)
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.valueChanged.connect(self._interpolate_colors)
        self.animation.finished.connect(self.theme_changed.emit)

    def _interpolate_colors(self, value):
        # Value is the progress (0.0 to 1.0)
        start = self.start_palette
        end = self.end_palette
        
        for key in start:
            c1 = QColor(start[key])
            c2 = QColor(end[key])
            
            r = c1.red() + (c2.red() - c1.red()) * value
            g = c1.green() + (c2.green() - c1.green()) * value
            b = c1.blue() + (c2.blue() - c1.blue()) * value
            
            self.colors[key] = QColor(int(r), int(g), int(b)).name()
        
        self._apply_stylesheet()
        self.theme_interpolating.emit()

    def set_theme(self, theme_name):
        if theme_name == self.current_theme: return
        
        self.start_palette = DARK_PALETTE if self.current_theme == 'dark' else LIGHT_PALETTE
        self.end_palette = DARK_PALETTE if theme_name == 'dark' else LIGHT_PALETTE
        self.current_theme = theme_name
        
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()

    def _apply_stylesheet(self):
        c = self.colors
        stylesheet = f"""
            QMainWindow, QWidget#centralWidget {{ 
                background-color: {c['background']}; 
                color: {c['text']};
            }}
            QLabel {{ color: {c['text']}; }}
            QLabel#panelHeader {{
                font-size: 18px;
                font-weight: bold;
                padding: 12px;
                background-color: {c['header_bg']};
                color: {c['accent_primary']};
                border-bottom: 2px solid {c['border']};
            }}
            
            /* Network Panel Specific Styling */
            QWidget#networkPanel {{
                background-color: {c['background']};
            }}
            QScrollArea#networkScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QWidget#networkListContainer {{
                background-color: {c['network_list_bg']};
                /* Transition handled by ThemeManager interpolation (300ms) */
                border-right: 1px solid {c['border']};
            }}
            
            QGroupBox {{
                border: 2px solid {c['border']};
                border-radius: 8px;
                margin-top: 1.5em;
                padding-top: 10px;
                font-weight: bold;
                background-color: {c['card_bg']};
                color: {c['text']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {c['accent_secondary']};
            }}
            QPushButton {{ 
                background-color: {c['surface']}; 
                color: {c['text']}; 
                border: 1px solid {c['border']}; 
                padding: 8px 16px; 
                border-radius: 4px;
            }}
            QPushButton:hover {{ 
                background-color: {c['accent_primary']}; 
                color: white; 
            }}
            QPushButton#saveButton {{
                background-color: {c['accent_primary']};
                color: white;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton#saveButton:hover {{
                background-color: {c['accent_secondary']};
            }}
            QToolBar {{
                background-color: {c['surface']};
                border-bottom: 1px solid {c['border']};
                spacing: 10px;
                padding: 5px;
            }}
            QToolButton {{
                background-color: transparent;
                color: {c['text']};
                border: 1px solid transparent;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QToolButton:hover {{
                background-color: {c['header_bg']};
                border: 1px solid {c['border']};
            }}
            QToolButton:disabled {{
                color: {c['disabled_text']};
            }}
            QTabWidget::pane {{ 
                border: 1px solid {c['border']}; 
                background-color: {c['background']};
            }}
            QTabBar::tab {{ 
                background-color: {c['surface']}; 
                color: {c['text']}; 
                padding: 10px 20px; 
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{ 
                background-color: {c['accent_primary']}; 
                color: white; 
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {c['surface']};
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {c['border']};
                min-height: 20px;
                border-radius: 5px;
            }}
            QTextEdit, QListWidget {{
                background-color: {c['surface']};
                color: {c['text']};
                border: 1px solid {c['border']};
                border-radius: 4px;
            }}
            QSpinBox, QDoubleSpinBox, QLineEdit {{
                background-color: {c['surface']};
                color: {c['text']};
                border: 1px solid {c['border']};
                padding: 4px;
                border-radius: 4px;
            }}
            QStatusBar {{
                background-color: {c['surface']};
                color: {c['text']};
            }}
            QMenuBar {{
                background-color: {c['surface']};
                color: {c['text']};
            }}
            QMenuBar::item:selected {{
                background-color: {c['accent_primary']};
                color: white;
            }}
            QMenu {{
                background-color: {c['surface']};
                color: {c['text']};
                border: 1px solid {c['border']};
            }}
            QMenu::item:selected {{
                background-color: {c['accent_primary']};
                color: white;
            }}
        """
        app = QApplication.instance()
        if app:
            app.setStyleSheet(stylesheet)

    def get_color(self, key):
        return QColor(self.colors.get(key, '#ff00ff'))
