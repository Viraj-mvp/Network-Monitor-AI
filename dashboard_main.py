import sys
from PySide6.QtWidgets import QApplication
from dashboard.main_window import MainWindow

def main():
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("AI Network Monitor")
    app.setOrganizationName("NetworkAI")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()