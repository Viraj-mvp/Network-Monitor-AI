#!/usr/bin/env python3
"""
Network AI Monitor - Professional Cross-Platform Release Builder
Creates optimized distribution packages for Windows, macOS, and Linux

Usage:
    python build_release.py [--clean] [--onedir] [--onefile]

Output:
    release/NetworkAIMonitor-<Platform>.zip (or .tar.gz)
"""

import os
import sys
import shutil
import platform
import subprocess
import argparse
from pathlib import Path

# Configuration
APP_NAME = "NetworkAIMonitor"
SYSTEM = platform.system().lower()

DIST_DIR = Path("dist")
RELEASE_DIR = Path("release")

# Platform-specific settings
PLATFORM_NAMES = {
    'windows': 'Windows',
    'darwin': 'macOS',
    'linux': 'Linux'
}

def print_step(step: str):
    """Print formatted step message"""
    print(f"\n{'='*60}")
    print(f"  {step}")
    print(f"{'='*60}\n")

def run_command(cmd: list, cwd: str = None) -> bool:
    """Run a command and return success status"""
    try:
        print(f"  Running: {' '.join(cmd[:5])}{'...' if len(cmd) > 5 else ''}")
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=False,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error: Command failed with exit code {e.returncode}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def clean():
    """Clean previous builds"""
    print_step("Cleaning previous builds")
    
    folders = ['build', 'dist', 'release']
    for folder in folders:
        path = Path(folder)
        if path.exists():
            shutil.rmtree(path)
            print(f"  ✓ Removed: {folder}")

def install_dependencies():
    """Install build dependencies"""
    print_step("Installing dependencies")
    
    # Upgrade pip
    if not run_command([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel']):
        return False
    
    # Install PyInstaller
    if not run_command([sys.executable, '-m', 'pip', 'install', 'pyinstaller', 'pillow']):
        return False
    
    # Install project requirements
    if Path('requirements.txt').exists():
        if not run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt']):
            return False
    
    return True

def build_onedir():
    """Build using onedir mode (recommended)"""
    print_step("Building application (onedir mode)")
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        'NetworkMonitor.spec'
    ]
    
    return run_command(cmd)

def build_onefile():
    """Build using onefile mode (alternative)"""
    print_step("Building application (onefile mode)")
    
    platform_name = PLATFORM_NAMES.get(SYSTEM, SYSTEM.capitalize())
    exe_name = f"{APP_NAME}-{platform_name}-Portable"
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        '--onefile',
        '--windowed',
        '--name', exe_name,
    ]
    
    # Add icon if exists
    icon_path = Path('assets/icon.ico') if SYSTEM == 'windows' else Path('assets/icon.png')
    if icon_path.exists():
        cmd.extend(['--icon', str(icon_path)])
    
    # Add data files
    sep = ';' if SYSTEM == 'windows' else ':'
    cmd.extend(['--add-data', f'core{sep}core'])
    cmd.extend(['--add-data', f'dashboard{sep}dashboard'])
    cmd.extend(['--add-data', f'assets{sep}assets'])
    cmd.extend(['--add-data', f'config{sep}config'])
    
    # Hidden imports
    hiddenimports = [
        'PySide6', 'PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets',
        'psutil', 'pyqtgraph', 'darkdetect', 'dotenv',
        'core', 'core.network_monitor', 'core.ai_engine', 'core.email_alert',
        'dashboard', 'dashboard.main_window', 'dashboard.widgets', 'dashboard.theme',
    ]
    for imp in hiddenimports:
        cmd.extend(['--hidden-import', imp])
    
    # Excludes
    excludes = [
        'tkinter', 'unittest', 'pytest', 'pydoc',
        'PyQt5', 'PyQt6', 'matplotlib',
    ]
    for exc in excludes:
        cmd.extend(['--exclude-module', exc])
    
    cmd.append('dashboard_main.py')
    
    return run_command(cmd)

def create_readme(platform_name: str) -> str:
    """Create README content for distribution"""
    return f"""Network AI Monitor v1.0.0
{'='*50}

Quick Start:
1. Extract this ZIP archive to any folder
2. Run {APP_NAME}.exe (Windows) or open {APP_NAME}.app (macOS)
3. Allow firewall access if prompted (required for network monitoring)

Requirements:
- {platform_name}
- Network interface (WiFi/Ethernet)
- 4GB RAM minimum (8GB recommended)

Features:
- Real-time network traffic monitoring
- AI-powered anomaly detection
- Email alerts for suspicious activity
- Live bandwidth visualization
- Dark/Light theme support

No installation required. Fully portable.

For support, visit: https://github.com/Viraj-mvp/Network-Monitor-AI

License: MIT
"""

def create_release_folder():
    """Create release folder with proper structure"""
    print_step("Creating release package")
    
    RELEASE_DIR.mkdir(exist_ok=True)
    
    # Determine source and destination
    app_dist = DIST_DIR / APP_NAME
    
    if not app_dist.exists():
        print(f"  ✗ Build output not found: {app_dist}")
        return False
    
    platform_name = PLATFORM_NAMES.get(SYSTEM, SYSTEM.capitalize())
    final_name = f"{APP_NAME}-{platform_name}"
    final_path = RELEASE_DIR / final_name
    
    # Copy build output
    print(f"  Copying to: {final_path}")
    if final_path.exists():
        shutil.rmtree(final_path)
    shutil.copytree(app_dist, final_path)
    
    # Add README.txt
    readme_content = create_readme(platform_name)
    readme_path = final_path / 'README.txt'
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    print(f"  ✓ Added README.txt")
    
    return final_name, final_path

def create_archive(final_name: str, final_path: Path):
    """Create platform-specific archive"""
    print_step("Creating distribution archive")
    
    archive_base = RELEASE_DIR / final_name
    
    if SYSTEM == 'windows':
        # Create ZIP for Windows
        archive_path = str(archive_base) + '.zip'
        print(f"  Creating: {final_name}.zip")
        shutil.make_archive(
            str(archive_base),
            'zip',
            root_dir=RELEASE_DIR,
            base_dir=final_name
        )
    elif SYSTEM == 'darwin':
        # Create ZIP for macOS (can also create DMG later)
        archive_path = str(archive_base) + '.zip'
        print(f"  Creating: {final_name}.zip")
        shutil.make_archive(
            str(archive_base),
            'zip',
            root_dir=RELEASE_DIR,
            base_dir=final_name
        )
    else:  # Linux
        # Create tar.gz for Linux
        archive_path = str(archive_base) + '.tar.gz'
        print(f"  Creating: {final_name}.tar.gz")
        shutil.make_archive(
            str(archive_base),
            'gztar',
            root_dir=RELEASE_DIR,
            base_dir=final_name
        )
    
    # Get archive size
    archive_file = Path(archive_path)
    if archive_file.exists():
        size_mb = archive_file.stat().st_size / (1024 * 1024)
        print(f"  ✓ Archive size: {size_mb:.2f} MB")
    
    return archive_path

def main():
    parser = argparse.ArgumentParser(
        description='Network AI Monitor - Professional Release Builder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build_release.py --onedir     # Build directory release (recommended)
  python build_release.py --onefile    # Build single executable
  python build_release.py --clean      # Clean before building
  python build_release.py --all        # Full clean build with onedir
        """
    )
    parser.add_argument('--clean', action='store_true', help='Clean before build')
    parser.add_argument('--onedir', action='store_true', help='Build onedir release (default)')
    parser.add_argument('--onefile', action='store_true', help='Build onefile release')
    parser.add_argument('--all', action='store_true', help='Clean + build + archive')
    
    args = parser.parse_args()
    
    # Print banner
    platform_name = PLATFORM_NAMES.get(SYSTEM, SYSTEM.capitalize())
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           Network AI Monitor - Professional Release          ║
║                                                              ║
║  Platform : {platform_name:20} Distribution Builder    ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Determine build mode
    if args.all:
        args.clean = True
        args.onedir = True
    elif not args.onefile:
        args.onedir = True  # Default to onedir
    
    # Clean if requested
    if args.clean:
        clean()
    
    # Install dependencies
    if not install_dependencies():
        print("\n✗ Failed to install dependencies")
        sys.exit(1)
    
    # Build
    success = False
    if args.onedir:
        success = build_onedir()
    elif args.onefile:
        success = build_onefile()
    
    if not success:
        print("\n✗ Build failed")
        sys.exit(1)
    
    # Create release folder
    result = create_release_folder()
    if not result:
        print("\n✗ Failed to create release folder")
        sys.exit(1)
    
    final_name, final_path = result
    
    # Create archive
    archive_path = create_archive(final_name, final_path)
    
    # Summary
    print("\n" + "="*60)
    print("  RELEASE COMPLETE")
    print("="*60)
    print(f"\n  Output: {archive_path}")
    print(f"\n  To test:")
    if SYSTEM == 'windows':
        print(f"    1. Extract {final_name}.zip")
        print(f"    2. Run {final_name}\\{APP_NAME}.exe")
    elif SYSTEM == 'darwin':
        print(f"    1. Extract {final_name}.zip")
        print(f"    2. Open {final_name}\\{APP_NAME}.app")
    else:
        print(f"    1. tar -xzf {final_name}.tar.gz")
        print(f"    2. ./{final_name}/{APP_NAME}")
    
    print("\n  ✓ Ready for GitHub Release!")
    print("="*60)

if __name__ == "__main__":
    main()
