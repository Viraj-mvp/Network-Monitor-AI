# setup.py
import os
import sys

def create_project_structure():
    """Create the project directory structure"""
    directories = [
        'core',
        'dashboard',
        'services',
        'assets/icons',
        'logs',
        'config'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # Create __init__.py files
    for dir in ['core', 'dashboard', 'services']:
        init_file = os.path.join(dir, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('')
            print(f"✓ Created: {init_file}")

if __name__ == "__main__":
    create_project_structure()
    print("\n✅ Project structure created successfully!")
    print("\nNext steps:")
    print("1. Copy your existing files to the new structure:")
    print("   - ai_engine.py → core/detector.py")
    print("   - network_monitor.py → core/network_stats.py")
    print("   - email_alert.py → core/alert_manager.py")
    print("   - main.py → core/monitor.py")
    print("\n2. Install dependencies:")
    print("   pip install PySide6 psutil pyqtgraph")
    print("\n3. Run the dashboard:")
    print("   python dashboard_main.py")