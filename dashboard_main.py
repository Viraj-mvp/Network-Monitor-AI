"""
Legacy entry point - redirects to new app/main.py
Kept for backward compatibility during development
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import and run the new main application
from app.main import main

if __name__ == "__main__":
    main()