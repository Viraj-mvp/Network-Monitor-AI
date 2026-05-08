"""
Resource Path Utilities for Network AI Monitor
Handles resource paths for both development and PyInstaller bundled app
"""

import sys
import os
from pathlib import Path


def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and PyInstaller
    
    Args:
        relative_path: Path relative to project root (e.g., 'assets/icon.png')
    
    Returns:
        Absolute path to the resource
    
    Usage:
        from utils.resources import resource_path
        icon_path = resource_path('assets/icon.png')
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # This is where bundled resources are extracted
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # Running in normal Python environment (development)
        # Use the directory containing the script
        if getattr(sys, 'frozen', False):
            # Running as compiled executable but _MEIPASS not set
            base_path = Path(sys.executable).parent
        else:
            # Running from source
            base_path = Path('.').resolve()
    
    return str(base_path / relative_path)


def ensure_dir(path: str) -> str:
    """
    Ensure directory exists, create if not
    
    Args:
        path: Directory path
    
    Returns:
        Absolute path to directory
    """
    dir_path = Path(path).resolve()
    dir_path.mkdir(parents=True, exist_ok=True)
    return str(dir_path)


def get_app_dir() -> str:
    """
    Get application directory (for logs, config, etc.)
    
    Returns:
        Path to application data directory
    """
    if sys.platform == 'win32':
        # Windows: Use %LOCALAPPDATA%
        app_data = Path(os.environ.get('LOCALAPPDATA', '~')) / 'NetworkAIMonitor'
    elif sys.platform == 'darwin':
        # macOS: Use ~/Library/Application Support
        app_data = Path.home() / 'Library' / 'Application Support' / 'NetworkAIMonitor'
    else:
        # Linux: Use ~/.local/share
        app_data = Path.home() / '.local' / 'share' / 'NetworkAIMonitor'
    
    return ensure_dir(app_data)


def get_logs_dir() -> str:
    """Get logs directory"""
    return ensure_dir(Path(get_app_dir()) / 'logs')


def get_config_dir() -> str:
    """Get config directory"""
    return ensure_dir(Path(get_app_dir()) / 'config')
