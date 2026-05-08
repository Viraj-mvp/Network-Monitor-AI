#!/usr/bin/env python3
"""
Build script for Network AI Monitor Desktop Application
Generates standalone executable and installer
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path

def print_step(step: str):
    """Print formatted step message"""
    print(f"\n{'='*60}")
    print(f"  {step}")
    print(f"{'='*60}\n")

def run_command(cmd: list, cwd: str = None) -> bool:
    """Run a command and return success status"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        return False

def clean_build():
    """Clean previous build artifacts"""
    print_step("Cleaning previous builds")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed: {dir_name}")
    
    # Clean pycache in subdirectories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                path = os.path.join(root, dir_name)
                shutil.rmtree(path)
                print(f"Removed: {path}")

def install_dependencies():
    """Install required dependencies"""
    print_step("Installing dependencies")
    
    deps = ['pyinstaller', 'pillow']
    
    # Install pyinstaller and other build deps
    if not run_command([sys.executable, '-m', 'pip', 'install'] + deps):
        return False
    
    # Install project requirements
    if os.path.exists('requirements.txt'):
        if not run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt']):
            return False
    
    return True

def create_icon():
    """Create default icon if not exists"""
    icon_dir = Path('assets')
    icon_path = icon_dir / 'icon.ico'
    
    if icon_path.exists():
        return True
    
    print_step("Creating application icon")
    icon_dir.mkdir(exist_ok=True)
    
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple icon (256x256)
        img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a simple network icon
        # Background circle
        draw.ellipse([10, 10, 246, 246], fill='#2196F3', outline='#1976D2', width=5)
        # Inner elements (simplified network representation)
        draw.ellipse([100, 100, 156, 156], fill='white')
        draw.line([(128, 60), (128, 100)], fill='white', width=8)
        draw.line([(128, 156), (128, 196)], fill='white', width=8)
        draw.line([(60, 128), (100, 128)], fill='white', width=8)
        draw.line([(156, 128), (196, 128)], fill='white', width=8)
        
        # Save as ICO
        img.save(icon_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        print(f"Created icon: {icon_path}")
        return True
        
    except ImportError:
        print("PIL not available, skipping icon creation")
        return True
    except Exception as e:
        print(f"Error creating icon: {e}")
        return True  # Non-critical

def build_executable(onefile: bool = False):
    """Build the executable using PyInstaller"""
    print_step(f"Building executable {'(one-file)' if onefile else '(directory)'}")
    
    if onefile:
        cmd = [
            'pyinstaller',
            '--onefile',
            '--windowed',
            '--name', 'NetworkAIMonitor-Portable',
            '--icon', 'assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
            '--add-data', f'core{os.pathsep}core',
            '--add-data', f'dashboard{os.pathsep}dashboard',
            '--add-data', f'assets{os.pathsep}assets',
            '--add-data', f'config{os.pathsep}config',
            '--hidden-import', 'PySide6',
            '--hidden-import', 'PySide6.QtCore',
            '--hidden-import', 'PySide6.QtGui',
            '--hidden-import', 'PySide6.QtWidgets',
            '--hidden-import', 'psutil',
            '--hidden-import', 'matplotlib',
            '--hidden-import', 'pyqtgraph',
            '--hidden-import', 'darkdetect',
            '--hidden-import', 'dotenv',
            'dashboard_main.py'
        ]
        # Remove None values
        cmd = [c for c in cmd if c is not None]
    else:
        cmd = [
            'pyinstaller',
            'NetworkMonitor.spec',
            '--clean',
            '--noconfirm'
        ]
    
    return run_command(cmd)

def build_installer():
    """Build Windows installer using Inno Setup"""
    print_step("Building Windows installer")
    
    inno_setup_paths = [
        r'C:\Program Files (x86)\Inno Setup 6\ISCC.exe',
        r'C:\Program Files\Inno Setup 6\ISCC.exe',
    ]
    
    iscc_path = None
    for path in inno_setup_paths:
        if os.path.exists(path):
            iscc_path = path
            break
    
    if not iscc_path:
        print("Inno Setup not found. Please install it from: https://jrsoftware.org/isdl.php")
        print("Skipping installer creation.")
        return False
    
    return run_command([iscc_path, 'installer.iss'])

def create_portable_zip():
    """Create a portable ZIP distribution"""
    print_step("Creating portable ZIP archive")
    
    import zipfile
    
    dist_dir = Path('dist')
    portable_dir = dist_dir / 'NetworkAIMonitor'
    
    if not portable_dir.exists():
        print(f"Build directory not found: {portable_dir}")
        return False
    
    zip_path = dist_dir / 'NetworkAIMonitor-Portable.zip'
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in portable_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(portable_dir)
                zipf.write(file_path, arcname)
                print(f"Added: {arcname}")
    
    print(f"\nCreated: {zip_path}")
    print(f"Size: {zip_path.stat().st_size / 1024 / 1024:.2f} MB")
    return True

def verify_build():
    """Verify the build output"""
    print_step("Verifying build")
    
    dist_dir = Path('dist')
    exe_path = dist_dir / 'NetworkAIMonitor' / 'NetworkAIMonitor.exe'
    
    if exe_path.exists():
        size = exe_path.stat().st_size / 1024 / 1024
        print(f"✓ Executable created: {exe_path}")
        print(f"  Size: {size:.2f} MB")
        return True
    else:
        print(f"✗ Executable not found: {exe_path}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Build Network AI Monitor Desktop App')
    parser.add_argument('--clean', action='store_true', help='Clean before build')
    parser.add_argument('--onefile', action='store_true', help='Build single executable file')
    parser.add_argument('--installer', action='store_true', help='Build installer (requires Inno Setup)')
    parser.add_argument('--zip', action='store_true', help='Create portable ZIP')
    parser.add_argument('--all', action='store_true', help='Build everything')
    
    args = parser.parse_args()
    
    # If no arguments, build standard executable
    if not any([args.clean, args.onefile, args.installer, args.zip, args.all]):
        args.all = True
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║           Network AI Monitor - Build System                   ║
║                                                              ║
║  Building desktop application with PyInstaller             ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Clean if requested
    if args.clean or args.all:
        clean_build()
    
    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies")
        sys.exit(1)
    
    # Create icon
    create_icon()
    
    success = True
    
    # Build executable
    if args.all or not args.installer:
        if args.onefile or args.all:
            success = build_executable(onefile=True) and success
        if not args.onefile or args.all:
            success = build_executable(onefile=False) and success
    
    # Verify build
    if not args.onefile:
        verify_build()
    
    # Build installer
    if args.installer or args.all:
        build_installer()
    
    # Create portable ZIP
    if args.zip or args.all:
        create_portable_zip()
    
    # Summary
    print("\n" + "="*60)
    print("  BUILD COMPLETE")
    print("="*60)
    print("\nOutput files in 'dist' directory:")
    
    dist_dir = Path('dist')
    if dist_dir.exists():
        for item in dist_dir.iterdir():
            if item.is_file():
                size = item.stat().st_size / 1024 / 1024
                print(f"  • {item.name} ({size:.2f} MB)")
            elif item.is_dir():
                print(f"  • {item.name}/ (directory)")
    
    print("\n✓ Build complete!")
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()
