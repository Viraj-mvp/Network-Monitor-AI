# -*- mode: python ; coding: utf-8 -*-
"""
Network AI Monitor - Professional PyInstaller Spec File
Optimized for distribution with onedir mode (not onefile)
"""

import sys
import os
from pathlib import Path

# Application metadata
APP_NAME = "NetworkAIMonitor"
APP_VERSION = "1.0.0"

# Get project root
project_root = Path('.').resolve()

# Determine platform-specific settings
if sys.platform == 'win32':
    icon_file = project_root / 'assets' / 'icon.ico'
    console_mode = False
elif sys.platform == 'darwin':
    icon_file = project_root / 'assets' / 'icon.icns'
    if not icon_file.exists():
        icon_file = project_root / 'assets' / 'icon.png'
    console_mode = False
else:  # Linux
    icon_file = project_root / 'assets' / 'icon.png'
    console_mode = False

# Check if icon exists
if not icon_file.exists():
    icon_file = None

# Data files to include - all project modules
datas = [
    (str(project_root / 'core'), 'core'),
    (str(project_root / 'dashboard'), 'dashboard'),
    (str(project_root / 'utils'), 'utils'),
    (str(project_root / 'services'), 'services'),
    (str(project_root / 'assets'), 'assets'),
    (str(project_root / 'config'), 'config'),
]

# Hidden imports - comprehensive list for cross-platform compatibility
hiddenimports = [
    # PySide6
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtNetwork',
    'PySide6.QtOpenGL',
    # psutil
    'psutil',
    # pyqtgraph and submodules
    'pyqtgraph',
    'pyqtgraph.graphicsItems',
    'pyqtgraph.widgets',
    'pyqtgraph.parametertree',
    'pyqtgraph.parametertree.interactive',
    'pyqtgraph.opengl',
    'pyqtgraph.Point',
    # numpy (needed by pyqtgraph)
    'numpy',
    'numpy.core',
    'numpy.core._dtype',
    'numpy.core._multiarray_umath',
    'numpy.core._umath',
    'numpy.linalg',
    'numpy.linalg._umath_linalg',
    # other deps
    'darkdetect',
    'dotenv',
    # project modules
    'core',
    'core.network_monitor',
    'core.ai_engine',
    'core.email_alert',
    'core.system_monitor',
    'dashboard',
    'dashboard.main_window',
    'dashboard.widgets',
    'dashboard.theme',
    'dashboard.interface_panel',
    'dashboard.alert_panel',
    'dashboard.log_viewer',
    'dashboard.settings_panel',
    'utils',
    'utils.resources',
]

# Modules to exclude (reduces size)
# NOTE: Don't exclude pydoc - needed by pyqtgraph
excludes = [
    'tkinter',
    'tkinter.constants',
    'unittest',
    'unittest.mock',
    'pytest',
    'test',
    'tests',
    'http.server',
    'xmlrpc',
    'xmlrpc.server',
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'matplotlib',
    'matplotlib.pyplot',
    'numpy.random._examples',
    'scipy',
    'pandas',
    'jupyter',
    'notebook',
    'ipython',
    'IPython',
    'docutils',
    'alabaster',
    'babel',
    'sphinx',
]

# Analysis
a = Analysis(
    ['dashboard_main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
    optimize=1,
)

# Remove duplicates
pyz = PYZ(a.pure)

# Create EXE (collect mode for onedir)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=console_mode,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_file) if icon_file else None,
)

# Collect all files into the distribution folder
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)
