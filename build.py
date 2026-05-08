#!/usr/bin/env python3
"""
Network AI Monitor - Cross-Platform Build Script
Builds standalone executables for Windows, macOS, and Linux using PyInstaller
"""

import os
import sys
import subprocess
import shutil
import argparse
import platform
from pathlib import Path

def print_step(step: str):
    """Print formatted step message"""
    print(f"\n{'='*60}")
    print(f"  {step}")
    print(f"{'='*60}\n")

def run_command(cmd: list, cwd: str = None, verbose: bool = True) -> bool:
    """Run a command and return success status"""
    try:
        if verbose:
            print(f"  Running: {' '.join(cmd[:10])}{'...' if len(cmd) > 10 else ''}")
        
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=not verbose,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error: Command failed with exit code {e.returncode}")
        if e.stdout:
            print(f"  stdout: {e.stdout[-500:]}")  # Last 500 chars
        if e.stderr:
            print(f"  stderr: {e.stderr[-500:]}")  # Last 500 chars
        return False
    except FileNotFoundError as e:
        print(f"  ✗ Error: Command not found - {e}")
        return False
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        return False

def get_platform():
    """Get current platform"""
    system = platform.system().lower()
    if system == 'darwin':
        return 'macos'
    return system

def get_executable_name():
    """Get executable name based on platform"""
    system = get_platform()
    if system == 'windows':
        return 'NetworkAIMonitor.exe'
    elif system == 'macos':
        return 'NetworkAIMonitor.app'
    else:
        return 'NetworkAIMonitor'

def clean_build():
    """Clean previous build artifacts"""
    print_step("Cleaning previous builds")
    
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  ✓ Removed: {dir_name}")
    
    # Clean pycache in subdirectories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(path)
                    print(f"  ✓ Removed: {path}")
                except:
                    pass

def install_dependencies():
    """Install required dependencies"""
    print_step("Installing dependencies")
    
    # Install pyinstaller
    print("  Installing PyInstaller...")
    if not run_command([sys.executable, '-m', 'pip', 'install', 'pyinstaller', '--upgrade']):
        return False
    
    # Install project requirements
    if os.path.exists('requirements.txt'):
        print("  Installing project requirements...")
        if not run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt']):
            return False
    
    return True

def create_icon():
    """Create default icon if not exists"""
    icon_dir = Path('assets')
    icon_dir.mkdir(exist_ok=True)
    
    system = get_platform()
    if system == 'windows':
        icon_path = icon_dir / 'icon.ico'
    elif system == 'macos':
        icon_path = icon_dir / 'icon.icns'
    else:
        icon_path = icon_dir / 'icon.png'
    
    if icon_path.exists():
        return str(icon_path)
    
    print_step("Creating application icon")
    
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple icon (256x256)
        img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple network icon
        draw.ellipse([10, 10, 246, 246], fill='#2196F3', outline='#1976D2', width=5)
        draw.ellipse([100, 100, 156, 156], fill='white')
        draw.line([(128, 60), (128, 100)], fill='white', width=8)
        draw.line([(128, 156), (128, 196)], fill='white', width=8)
        draw.line([(60, 128), (100, 128)], fill='white', width=8)
        draw.line([(156, 128), (196, 128)], fill='white', width=8)
        
        # Save in appropriate format
        if system == 'windows':
            img.save(icon_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        elif system == 'macos':
            # macOS uses .icns, save as PNG for now
            img.save(icon_dir / 'icon.png', format='PNG')
            icon_path = icon_dir / 'icon.png'
        else:
            img.save(icon_path, format='PNG')
        
        print(f"  ✓ Created icon: {icon_path}")
        return str(icon_path)
        
    except ImportError:
        print("  ℹ PIL not available, skipping icon creation")
        return None
    except Exception as e:
        print(f"  ⚠ Error creating icon: {e}")
        return None

def get_add_data_args():
    """Get --add-data arguments for current platform"""
    sep = ';' if get_platform() == 'windows' else ':'
    return [
        f'--add-data', f'core{sep}core',
        f'--add-data', f'dashboard{sep}dashboard',
        f'--add-data', f'assets{sep}assets',
        f'--add-data', f'config{sep}config',
    ]

def get_hidden_imports():
    """Get hidden imports for PyInstaller"""
    return [
        '--hidden-import', 'PySide6',
        '--hidden-import', 'PySide6.QtCore',
        '--hidden-import', 'PySide6.QtGui',
        '--hidden-import', 'PySide6.QtWidgets',
        '--hidden-import', 'psutil',
        '--hidden-import', 'matplotlib',
        '--hidden-import', 'matplotlib.backends.backend_qt5agg',
        '--hidden-import', 'pyqtgraph',
        '--hidden-import', 'darkdetect',
        '--hidden-import', 'dotenv',
        '--hidden-import', 'core',
        '--hidden-import', 'core.network_monitor',
        '--hidden-import', 'core.ai_engine',
        '--hidden-import', 'core.email_alert',
        '--hidden-import', 'dashboard',
        '--hidden-import', 'dashboard.main_window',
        '--hidden-import', 'dashboard.widgets',
        '--hidden-import', 'dashboard.theme',
    ]

def build_executable(onefile: bool = True):
    """Build the executable using PyInstaller"""
    build_type = "one-file" if onefile else "directory"
    print_step(f"Building {build_type} executable for {get_platform().title()}")
    
    # Base command
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--noconfirm',
        '--clean',
    ]
    
    # Windowed mode (no console)
    cmd.append('--windowed')
    
    # One-file or directory mode
    if onefile:
        cmd.append('--onefile')
        name = f"NetworkAIMonitor-{get_platform().title()}-Portable"
    else:
        name = "NetworkAIMonitor"
    
    cmd.extend(['--name', name])
    
    # Icon
    icon_path = create_icon()
    if icon_path and os.path.exists(icon_path):
        cmd.extend(['--icon', icon_path])
    
    # Add data files
    cmd.extend(get_add_data_args())
    
    # Hidden imports
    cmd.extend(get_hidden_imports())
    
    # Exclude unnecessary modules to reduce size and avoid conflicts
    # NOTE: Don't exclude 'email' - it's needed by pkg_resources
    excludes = [
        '--exclude-module', 'tkinter',
        '--exclude-module', 'unittest',
        '--exclude-module', 'pytest',
        '--exclude-module', 'pydoc',
        '--exclude-module', 'http.server',
        '--exclude-module', 'xmlrpc',
        '--exclude-module', 'PyQt6',
        '--exclude-module', 'PyQt5',
        '--exclude-module', 'PyQt4',
        '--exclude-module', 'PyQt6.QtCore',
        '--exclude-module', 'PyQt6.QtGui',
        '--exclude-module', 'PyQt6.QtWidgets',
    ]
    cmd.extend(excludes)
    
    # Main script
    cmd.append('dashboard_main.py')
    
    print(f"  Running: {' '.join(cmd[:5])}...")
    return run_command(cmd)

def create_archive():
    """Create platform-specific archive"""
    print_step("Creating distribution archive")
    
    system = get_platform()
    dist_dir = Path('dist')
    
    if not dist_dir.exists():
        print("  ✗ Dist directory not found")
        return False
    
    # Find the built executable/directory
    exe_name = get_executable_name()
    source_path = dist_dir / exe_name
    
    if not source_path.exists():
        # Try to find any built executable
        for item in dist_dir.iterdir():
            if item.is_dir() or (item.is_file() and not item.name.endswith('.zip')):
                source_path = item
                break
    
    if not source_path or not source_path.exists():
        print("  ✗ Built executable not found")
        return False
    
    # Create archive
    if system == 'windows':
        import zipfile
        zip_path = dist_dir / f'NetworkAIMonitor-{system.title()}.zip'
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            if source_path.is_dir():
                for file_path in source_path.rglob('*'):
                    if file_path.is_file():
                        zf.write(file_path, file_path.relative_to(source_path.parent))
            else:
                zf.write(source_path, source_path.name)
        print(f"  ✓ Created: {zip_path}")
        return True
    else:
        # For macOS and Linux, create tar.gz
        import tarfile
        archive_path = dist_dir / f'NetworkAIMonitor-{system.title()}.tar.gz'
        with tarfile.open(archive_path, 'w:gz') as tar:
            if source_path.is_dir():
                tar.add(source_path, arcname=source_path.name)
            else:
                tar.add(source_path, arcname=source_path.name)
        print(f"  ✓ Created: {archive_path}")
        return True

def verify_build():
    """Verify the build output"""
    print_step("Verifying build")
    
    dist_dir = Path('dist')
    exe_name = get_executable_name()
    exe_path = dist_dir / exe_name
    
    # Also check for platform-specific portable version
    portable_names = [
        f'NetworkAIMonitor-{get_platform().title()}-Portable.exe',
        f'NetworkAIMonitor-{get_platform().title()}-Portable',
        'NetworkAIMonitor-Portable.exe',
        'NetworkAIMonitor-Portable',
    ]
    
    found = False
    for name in portable_names + [exe_name]:
        path = dist_dir / name
        if path.exists():
            if path.is_file():
                size = path.stat().st_size / 1024 / 1024
                print(f"  ✓ Found: {name} ({size:.2f} MB)")
            else:
                print(f"  ✓ Found: {name}/ (directory)")
            found = True
            break
    
    if not found:
        print(f"  ✗ Executable not found in {dist_dir}")
        # List what's in dist
        if dist_dir.exists():
            print("  Contents:")
            for item in dist_dir.iterdir():
                print(f"    - {item.name}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description='Build Network AI Monitor - Cross-Platform Executable Builder'
    )
    parser.add_argument('--clean', action='store_true', help='Clean before build')
    parser.add_argument('--onefile', action='store_true', help='Build single executable file (default)')
    parser.add_argument('--directory', action='store_true', help='Build directory bundle instead of one-file')
    parser.add_argument('--archive', action='store_true', help='Create compressed archive')
    parser.add_argument('--install', action='store_true', help='Install dependencies only')
    parser.add_argument('--all', action='store_true', help='Build all formats (onefile + archive)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Print banner
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           Network AI Monitor - Cross-Platform Build           ║
║                                                              ║
║  Platform: {get_platform().title():20} PyInstaller Bundle           ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Install only mode
    if args.install:
        if install_dependencies():
            print("\n✓ Dependencies installed successfully!")
            sys.exit(0)
        else:
            print("\n✗ Failed to install dependencies")
            sys.exit(1)
    
    # Clean if requested
    if args.clean:
        clean_build()
    
    # Install dependencies
    if not install_dependencies():
        print("\n✗ Failed to install dependencies")
        sys.exit(1)
    
    success = True
    
    # Determine build type
    build_onefile = not args.directory  # Default to onefile unless --directory specified
    
    if args.all or build_onefile:
        success = build_executable(onefile=True) and success
    
    if args.directory or args.all:
        success = build_executable(onefile=False) and success
    
    # Verify build
    verify_build()
    
    # Create archive if requested
    if args.archive or args.all:
        create_archive()
    
    # Summary
    print("\n" + "="*60)
    print("  BUILD SUMMARY")
    print("="*60)
    
    dist_dir = Path('dist')
    if dist_dir.exists():
        files = list(dist_dir.iterdir())
        if files:
            print(f"\n  Output files in 'dist/':")
            for item in files:
                if item.is_file():
                    size = item.stat().st_size / 1024 / 1024
                    print(f"    • {item.name:40} ({size:6.2f} MB)")
                else:
                    print(f"    • {item.name}/ (directory)")
            
            print(f"\n  ✓ Build successful!")
            print(f"\n  To run the app:")
            exe_name = get_executable_name()
            if get_platform() == 'windows':
                print(f"    dist\\{exe_name}")
            else:
                print(f"    ./{exe_name}  (or open the .app on macOS)")
        else:
            print("  ✗ No output files found")
            success = False
    else:
        print("  ✗ Build failed - no dist directory")
        success = False
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
