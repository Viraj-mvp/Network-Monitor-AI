"""
Main Application Entry Point
Initializes the app, shows splash, handles first-run, creates main window
"""

import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PySide6.QtCore import Qt, QTimer, QSharedMemory, QSystemSemaphore
from PySide6.QtGui import QIcon

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.splash import SplashScreen
from app.tray import SystemTray
from config import get_config_manager
from onboarding import run_setup_wizard
from dashboard.main_window import MainWindow
from dashboard.theme import ThemeManager


class Application:
    """Main application controller"""
    
    APP_NAME = "Network AI Monitor"
    APP_VERSION = "1.0.0"
    
    def __init__(self):
        self._app = None
        self._splash = None
        self._main_window = None
        self._tray = None
        self._theme_manager = None
        self._config = None
        self._single_instance_lock = None
    
    def run(self):
        """Main entry point - run the application"""
        try:
            # Create Qt Application
            self._app = QApplication(sys.argv)
            self._app.setApplicationName(self.APP_NAME)
            self._app.setApplicationVersion(self.APP_VERSION)
            self._app.setOrganizationName("NetworkAI")
            
            # Set application ID for Windows taskbar
            if sys.platform == 'win32':
                try:
                    import ctypes
                    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                        "NetworkAI.Monitor.1.0"
                    )
                except Exception:
                    pass
            
            # Check single instance
            if not self._check_single_instance():
                print("Another instance is already running")
                self._show_already_running_message()
                return 1
            
            # Show splash screen
            self._show_splash()
            
            # Initialize in background
            QTimer.singleShot(100, self._initialize)
            
            # Run event loop
            return self._app.exec()
            
        except Exception as e:
            print(f"Fatal error: {e}")
            import traceback
            traceback.print_exc()
            return 1
        finally:
            self._cleanup()
    
    def _check_single_instance(self) -> bool:
        """Check if another instance is already running"""
        # Use shared memory for single instance check
        self._single_instance_lock = QSharedMemory("NetworkAIMonitor_SingleInstance")
        
        if self._single_instance_lock.attach():
            # Another instance is running
            return False
        
        if not self._single_instance_lock.create(1):
            return False
        
        return True
    
    def _show_already_running_message(self):
        """Show message when another instance is running"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(self.APP_NAME)
        msg.setText("Already Running")
        msg.setInformativeText(
            "Network AI Monitor is already running.\n\n"
            "Check your system tray for the application icon."
        )
        msg.exec()
    
    def _show_splash(self):
        """Show the splash screen"""
        self._splash = SplashScreen()
        self._splash.show()
        self._splash.animate_progress(2000)
    
    def _initialize(self):
        """Initialize application components"""
        try:
            # Load configuration
            self._splash.show_progress(20, "Loading configuration...")
            self._config = get_config_manager()
            
            # Check first run
            is_first_run = self._config.is_first_run()
            
            if is_first_run:
                # Run setup wizard (keep splash)
                self._run_setup_wizard()
            else:
                # Continue loading for existing users
                self._continue_loading()
                
        except Exception as e:
            print(f"Initialization error: {e}")
            import traceback
            traceback.print_exc()
            self._show_error_and_exit("Initialization Error", str(e))
    
    def _run_setup_wizard(self):
        """Run first-time setup wizard"""
        accepted, settings = run_setup_wizard()
        
        if accepted:
            # User completed setup - finish splash and continue
            if self._splash:
                self._splash.finish(None)
                self._splash = None
            self._continue_loading()
        else:
            # User cancelled setup
            self._show_error_and_exit(
                "Setup Required",
                "Network AI Monitor requires initial setup to run.\n"
                "Please complete setup wizard to continue."
            )
    
    def _continue_loading(self):
        """Continue loading after wizard or for returning users"""
        try:
            # Initialize theme
            self._splash.show_progress(40, "Initializing theme...")
            self._theme_manager = ThemeManager()
            self._apply_theme()
            
            # Create system tray
            self._splash.show_progress(60, "Creating system tray...")
            self._tray = SystemTray()
            self._tray.show()
            self._connect_tray_signals()
            
            # Create main window
            self._splash.show_progress(80, "Opening dashboard...")
            self._main_window = MainWindow()
            self._connect_main_window_signals()
            
            # Configure based on settings
            self._configure_from_settings()
            
            # Finish splash and show window
            self._splash.show_progress(100, "Ready!")
            self._splash.finish(self._main_window)
            self._splash = None
            
            # Show or minimize based on settings
            if self._config.appearance.start_minimized:
                self._main_window.hide()
            else:
                self._main_window.show()
                self._main_window.raise_()
                self._main_window.activateWindow()
            
            # Auto-start monitoring (always enabled for professional app)
            QTimer.singleShot(500, self._auto_start_monitoring)
                
        except Exception as e:
            print(f"Error continuing load: {e}")
            import traceback
            traceback.print_exc()
            self._show_error_and_exit("Loading Error", str(e))
    
    def _apply_theme(self):
        """Apply the configured theme"""
        theme = self._config.appearance.theme
        if theme == "auto":
            import darkdetect
            theme = "dark" if darkdetect.isDark() else "light"
        self._theme_manager.set_theme(theme)
    
    def _connect_tray_signals(self):
        """Connect system tray signals"""
        self._tray.show_requested.connect(self._show_main_window)
        self._tray.hide_requested.connect(self._hide_main_window)
        self._tray.start_monitoring_requested.connect(self._start_monitoring)
        self._tray.stop_monitoring_requested.connect(self._stop_monitoring)
        self._tray.settings_requested.connect(self._show_settings)
        self._tray.exit_requested.connect(self._exit_application)
    
    def _connect_main_window_signals(self):
        """Connect main window signals"""
        # Override close event to minimize to tray
        self._main_window.closeEvent = self._on_main_window_close
        
        # Connect monitoring state changes to tray
        # (MainWindow needs to emit signals when monitoring starts/stops)
    
    def _configure_from_settings(self):
        """Configure the app based on saved settings"""
        # Apply settings to main window
        if self._main_window:
            # Apply thresholds
            thresholds = {
                'WiFi': {
                    'in': self._config.monitoring.wifi_threshold_in,
                    'out': self._config.monitoring.wifi_threshold_out
                },
                'Ethernet': {
                    'in': self._config.monitoring.ethernet_threshold_in,
                    'out': self._config.monitoring.ethernet_threshold_out
                }
            }
            
            # Update main window settings
            settings_dict = {
                'thresholds': thresholds,
                'email': {
                    'enabled': self._config.email.enabled,
                    'receiver': self._config.email.receiver_email
                }
            }
            
            # Call update_settings on main window
            if hasattr(self._main_window, 'update_settings'):
                self._main_window.update_settings(settings_dict)
    
    def _auto_start_monitoring(self):
        """Auto-start monitoring if configured"""
        if self._main_window and hasattr(self._main_window, 'start_monitoring'):
            self._main_window.start_monitoring()
            self._tray.set_monitoring_state(True)
    
    def _show_main_window(self):
        """Show the main window"""
        if self._main_window:
            self._main_window.show()
            self._main_window.raise_()
            self._main_window.activateWindow()
    
    def _hide_main_window(self):
        """Hide the main window to tray"""
        if self._main_window:
            self._main_window.hide()
    
    def _start_monitoring(self):
        """Start monitoring from tray"""
        if self._main_window and hasattr(self._main_window, 'start_monitoring'):
            self._main_window.start_monitoring()
            self._tray.set_monitoring_state(True)
    
    def _stop_monitoring(self):
        """Stop monitoring from tray"""
        if self._main_window and hasattr(self._main_window, 'stop_monitoring'):
            self._main_window.stop_monitoring()
            self._tray.set_monitoring_state(False)
    
    def _show_settings(self):
        """Show settings panel"""
        self._show_main_window()
        # Switch to settings tab
        if self._main_window and hasattr(self._main_window, 'settings_panel'):
            # Access the tab widget and switch to settings
            # This depends on main_window structure
            pass
    
    def _on_main_window_close(self, event):
        """Handle main window close - minimize to tray instead"""
        if self._config.appearance.minimize_to_tray and self._tray.is_visible():
            self._hide_main_window()
            self._tray.show_notification(
                "Network AI Monitor",
                "Running in background. Click tray icon to restore.",
                duration_ms=3000
            )
            event.ignore()
        else:
            self._exit_application()
            event.accept()
    
    def _exit_application(self):
        """Exit the application cleanly"""
        # Stop monitoring
        if self._main_window and hasattr(self._main_window, 'stop_monitoring'):
            self._main_window.stop_monitoring()
        
        # Save any pending settings
        if self._config:
            self._config.save()
        
        # Quit application
        if self._app:
            self._app.quit()
    
    def _show_error_and_exit(self, title: str, message: str):
        """Show error dialog and exit"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()
        
        self._cleanup()
        sys.exit(1)
    
    def _cleanup(self):
        """Clean up resources"""
        # Release single instance lock
        if self._single_instance_lock:
            self._single_instance_lock.detach()
        
        # Hide tray
        if self._tray:
            self._tray.hide()


def main():
    """Main entry point"""
    # Enable high DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = Application()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
