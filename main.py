"""
BreakGuard - Your Health Guardian
Main entry point for the application
"""

import sys
import os
import argparse
import logging
import logging.handlers
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from theme.theme import load_stylesheet

def setup_logging():
    """Configure application logging"""
    # Import here after src is in path
    from path_utils import get_logs_dir, ensure_app_data_dirs
    
    # Ensure app data directories exist
    ensure_app_data_dirs()
    
    # Use user's AppData folder for logs (writable without admin rights)
    log_dir = get_logs_dir()
    log_file = log_dir / 'breakguard.log'
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler (rotating, 5MB max, 3 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Silence comtypes debug logs
    logging.getLogger('comtypes').setLevel(logging.INFO)
    
    logging.info("Logging initialized")

def global_exception_handler(exctype, value, traceback):
    """Global exception handler to log unhandled exceptions"""
    logging.critical("Unhandled exception", exc_info=(exctype, value, traceback))
    sys.__excepthook__(exctype, value, traceback)

def main():
    """Main entry point"""
    setup_logging()
    sys.excepthook = global_exception_handler
    logger = logging.getLogger(__name__)
    
    parser = argparse.ArgumentParser(description='BreakGuard - Your Health Guardian')
    parser.add_argument('--setup', action='store_true', help='Run setup wizard')
    parser.add_argument('--settings', action='store_true', help='Open settings')
    args = parser.parse_args()
    
    # Ensure app data directories exist
    from path_utils import ensure_app_data_dirs
    ensure_app_data_dirs()
    
    # High DPI scaling (for PyQt6 compatibility)
    try:
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    except AttributeError:
        pass  # Not available in all PyQt6 versions
    
    # Set App User Model ID for Windows notifications
    if sys.platform == 'win32':
        import ctypes
        myappid = 'BreakGuard' # Changed to simple name
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    app = QApplication(sys.argv)
    app.setApplicationName("BreakGuard")
    app.setOrganizationName("BreakGuard")
    
    # Ensure Start Menu shortcut exists (run after app init to avoid COM conflicts)
    if sys.platform == 'win32':
        try:
            logger.debug("Creating Start Menu shortcut...")
            from windows_startup import WindowsStartup
            startup = WindowsStartup()
            startup.create_shortcut()
            logger.debug("Shortcut created successfully")
        except Exception as e:
            logger.error(f"Failed to create shortcut: {e}", exc_info=True)
    
    # Apply global theme
    app.setStyleSheet(load_stylesheet())
    
    # Set application icon
    from PyQt6.QtGui import QIcon
    from path_utils import get_assets_dir
    icon_path = get_assets_dir() / 'logo.png'
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    else:
        # Fallback
        app.setWindowIcon(app.style().standardIcon(
            app.style().StandardPixmap.SP_ComputerIcon
        ))
    
    # Check if first time setup is needed
    from path_utils import get_config_file
    config_path = get_config_file()
    
    # Keep references to prevent garbage collection
    global wizard, break_guard, settings
    wizard = None
    break_guard = None
    settings = None

    def start_app():
        """Start the main application"""
        global break_guard
        from work_timer import BreakGuardApp
        # Ensure app doesn't quit when wizard closes
        app.setQuitOnLastWindowClosed(False)
        break_guard = BreakGuardApp()
        break_guard.start()

    if args.setup or not config_path.exists():
        # Run setup wizard
        from setup_wizard_gui_pyqt import SetupWizard
        wizard = SetupWizard()
        wizard.setup_completed.connect(start_app)
        wizard.show()
    elif args.settings:
        # Open settings
        from settings_gui_pyqt import SettingsWindow
        settings = SettingsWindow()
        settings.show()
    else:
        # Run main application
        start_app()
    
    try:
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
