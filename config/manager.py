"""
Configuration Manager - Platform-specific config storage
Handles JSON config with schema validation and auto-save
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Callable
from dataclasses import dataclass, asdict
from PySide6.QtCore import QObject, Signal


@dataclass
class MonitoringSettings:
    interface: str = "auto"  # "auto" or specific interface name
    interval: int = 5  # seconds
    wifi_threshold_in: float = 1.0  # Mbps
    wifi_threshold_out: float = 0.5
    ethernet_threshold_in: float = 5.0
    ethernet_threshold_out: float = 2.0
    ai_sensitivity: str = "medium"  # low, medium, high


@dataclass
class EmailSettings:
    enabled: bool = False
    receiver_email: str = ""
    sender_email: str = ""  # Gmail address
    # Note: app_password is stored in credential manager, not config


@dataclass
class AppearanceSettings:
    theme: str = "auto"  # auto, dark, light
    start_minimized: bool = False
    minimize_to_tray: bool = True
    startup_with_system: bool = False


@dataclass
class AppConfig:
    version: str = "1.0.0"
    first_run_completed: bool = False
    monitoring: MonitoringSettings = None
    email: EmailSettings = None
    appearance: AppearanceSettings = None
    
    def __post_init__(self):
        if self.monitoring is None:
            self.monitoring = MonitoringSettings()
        if self.email is None:
            self.email = EmailSettings()
        if self.appearance is None:
            self.appearance = AppearanceSettings()


class ConfigManager(QObject):
    """Platform-specific configuration manager with auto-save"""
    
    config_changed = Signal(str, object)  # section, value
    config_saved = Signal()
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True
        self._config = AppConfig()
        self._config_path = self._get_config_path()
        self._auto_save = True
        self._pending_save = False
        
        # Ensure config directory exists
        self._ensure_config_dir()
        
        # Load existing config if present
        self.load()
    
    def _get_config_dir(self) -> Path:
        """Get platform-specific config directory"""
        if sys.platform == 'win32':
            # Windows: %LOCALAPPDATA%\NetworkAIMonitor
            app_data = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
            return app_data / 'NetworkAIMonitor'
        elif sys.platform == 'darwin':
            # macOS: ~/Library/Application Support/NetworkAIMonitor
            return Path.home() / 'Library' / 'Application Support' / 'NetworkAIMonitor'
        else:
            # Linux: ~/.config/NetworkAIMonitor (XDG spec)
            xdg_config = os.environ.get('XDG_CONFIG_HOME')
            if xdg_config:
                return Path(xdg_config) / 'NetworkAIMonitor'
            return Path.home() / '.config' / 'NetworkAIMonitor'
    
    def _get_config_path(self) -> Path:
        """Get full path to config file"""
        return self._get_config_dir() / 'config.json'
    
    def _ensure_config_dir(self):
        """Create config directory if it doesn't exist"""
        config_dir = self._get_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Also ensure logs directory exists
        logs_dir = config_dir / 'logs'
        logs_dir.mkdir(exist_ok=True)
    
    def _config_to_dict(self) -> dict:
        """Convert config dataclass to dictionary"""
        return {
            'version': self._config.version,
            'first_run_completed': self._config.first_run_completed,
            'monitoring': asdict(self._config.monitoring),
            'email': asdict(self._config.email),
            'appearance': asdict(self._config.appearance)
        }
    
    def _dict_to_config(self, data: dict) -> AppConfig:
        """Convert dictionary to config dataclass"""
        config = AppConfig()
        
        config.version = data.get('version', '1.0.0')
        config.first_run_completed = data.get('first_run_completed', False)
        
        if 'monitoring' in data:
            m = data['monitoring']
            config.monitoring = MonitoringSettings(
                interface=m.get('interface', 'auto'),
                interval=m.get('interval', 5),
                wifi_threshold_in=m.get('wifi_threshold_in', 1.0),
                wifi_threshold_out=m.get('wifi_threshold_out', 0.5),
                ethernet_threshold_in=m.get('ethernet_threshold_in', 5.0),
                ethernet_threshold_out=m.get('ethernet_threshold_out', 2.0),
                ai_sensitivity=m.get('ai_sensitivity', 'medium')
            )
        
        if 'email' in data:
            e = data['email']
            config.email = EmailSettings(
                enabled=e.get('enabled', False),
                receiver_email=e.get('receiver_email', ''),
                sender_email=e.get('sender_email', '')
            )
        
        if 'appearance' in data:
            a = data['appearance']
            config.appearance = AppearanceSettings(
                theme=a.get('theme', 'auto'),
                start_minimized=a.get('start_minimized', False),
                minimize_to_tray=a.get('minimize_to_tray', True),
                startup_with_system=a.get('startup_with_system', False)
            )
        
        return config
    
    def load(self) -> bool:
        """Load configuration from file. Returns True if successful."""
        if not self._config_path.exists():
            return False
        
        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self._config = self._dict_to_config(data)
            return True
        except Exception as e:
            print(f"Error loading config: {e}")
            return False
    
    def save(self) -> bool:
        """Save configuration to file. Returns True if successful."""
        try:
            self._ensure_config_dir()
            with open(self._config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config_to_dict(), f, indent=2)
            self.config_saved.emit()
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def is_first_run(self) -> bool:
        """Check if this is the first run (no config exists)"""
        return not self._config_path.exists() or not self._config.first_run_completed
    
    def mark_first_run_complete(self):
        """Mark first run as completed"""
        self._config.first_run_completed = True
        if self._auto_save:
            self.save()
    
    # Property getters/setters for easy access
    
    @property
    def monitoring(self) -> MonitoringSettings:
        return self._config.monitoring
    
    @monitoring.setter
    def monitoring(self, value: MonitoringSettings):
        self._config.monitoring = value
        self.config_changed.emit('monitoring', value)
        if self._auto_save:
            self.save()
    
    @property
    def email(self) -> EmailSettings:
        return self._config.email
    
    @email.setter
    def email(self, value: EmailSettings):
        self._config.email = value
        self.config_changed.emit('email', value)
        if self._auto_save:
            self.save()
    
    @property
    def appearance(self) -> AppearanceSettings:
        return self._config.appearance
    
    @appearance.setter
    def appearance(self, value: AppearanceSettings):
        self._config.appearance = value
        self.config_changed.emit('appearance', value)
        if self._auto_save:
            self.save()
    
    @property
    def first_run_completed(self) -> bool:
        return self._config.first_run_completed
    
    # Helper methods for individual setting updates
    
    def update_monitoring(self, **kwargs):
        """Update monitoring settings"""
        for key, value in kwargs.items():
            if hasattr(self._config.monitoring, key):
                setattr(self._config.monitoring, key, value)
        self.config_changed.emit('monitoring', self._config.monitoring)
        if self._auto_save:
            self.save()
    
    def update_email(self, **kwargs):
        """Update email settings"""
        for key, value in kwargs.items():
            if hasattr(self._config.email, key):
                setattr(self._config.email, key, value)
        self.config_changed.emit('email', self._config.email)
        if self._auto_save:
            self.save()
    
    def update_appearance(self, **kwargs):
        """Update appearance settings"""
        for key, value in kwargs.items():
            if hasattr(self._config.appearance, key):
                setattr(self._config.appearance, key, value)
        self.config_changed.emit('appearance', self._config.appearance)
        if self._auto_save:
            self.save()
    
    def get_config_path(self) -> str:
        """Get the config file path (for display/debugging)"""
        return str(self._config_path)
    
    def get_logs_dir(self) -> str:
        """Get the logs directory path"""
        return str(self._get_config_dir() / 'logs')


# Singleton accessor
def get_config_manager() -> ConfigManager:
    """Get the global ConfigManager instance"""
    return ConfigManager()
