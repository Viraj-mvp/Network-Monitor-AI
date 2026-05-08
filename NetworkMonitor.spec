# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Network AI Monitor
Generates standalone executable with all dependencies
"""

import sys
import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
from PyInstaller.building.api import BUNDLE

# Get the project root directory
project_root = os.path.abspath('.')

# Define paths
icon_path = os.path.join(project_root, 'assets', 'icon.ico')
if not os.path.exists(icon_path):
    icon_path = None

# Hidden imports for PySide6 and other packages
hiddenimports = [
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'psutil',
    'matplotlib',
    'matplotlib.backends.backend_qt5agg',
    'pyqtgraph',
    'darkdetect',
    'dotenv',
    'core',
    'core.network_monitor',
    'core.ai_engine',
    'core.email_alert',
    'dashboard',
    'dashboard.main_window',
    'dashboard.widgets',
    'dashboard.theme',
    'dashboard.interface_panel',
    'dashboard.alert_panel',
    'dashboard.log_viewer',
    'dashboard.settings_panel',
]

# Data files to include
datas = [
    ('core', 'core'),
    ('dashboard', 'dashboard'),
    ('assets', 'assets'),
    ('config', 'config'),
    ('logs', 'logs'),
    ('requirements.txt', '.'),
]

# Binary files
binaries = []

# Analysis
a = Analysis(
    ['dashboard_main.py'],
    pathex=[project_root],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'unittest',
        'pytest',
        'pydoc',
        'email',
        'http',
        'xml',
        'html',
        'test',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate files
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NetworkAIMonitor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
    version_info={
        'version': '1.0.0.0',
        'company_name': 'NetworkAI',
        'file_description': 'AI-Powered Network Traffic Monitor',
        'internal_name': 'NetworkAIMonitor',
        'legal_copyright': 'MIT License',
        'original_filename': 'NetworkAIMonitor.exe',
        'product_name': 'Network AI Monitor',
    },
)

# Collect all files into dist folder
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NetworkAIMonitor'
)
