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
    log_dir = Path(__file__).parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
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
    
    logging.info("Logging initialized")

def main():
    """Main entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    parser = argparse.ArgumentParser(description='BreakGuard - Your Health Guardian')
    parser.add_argument('--setup', action='store_true', help='Run setup wizard')
    parser.add_argument('--settings', action='store_true', help='Open settings')
    args = parser.parse_args()
    
    # Create data directory if it doesn't exist
    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(exist_ok=True)
    
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
        
        # Ensure Start Menu shortcut exists for notifications to have icon
        try:
            from windows_startup import WindowsStartup
            startup = WindowsStartup()
            startup.create_shortcut()
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName("BreakGuard")
    app.setOrganizationName("BreakGuard")
    
    # Apply global theme
    app.setStyleSheet(load_stylesheet())
    
    # Set application icon
    from PyQt6.QtGui import QIcon
    assets_dir = Path(__file__).parent / 'assets'
    icon_path = assets_dir / 'logo.png'
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    else:
        # Fallback
        app.setWindowIcon(app.style().standardIcon(
            app.style().StandardPixmap.SP_ComputerIcon
        ))
    
    # Check if first time setup is needed
    config_path = Path(__file__).parent / 'config.json'
    
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
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
