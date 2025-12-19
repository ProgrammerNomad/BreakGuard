"""
BreakGuard - Your Health Guardian
Main entry point for the application
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

def main():
    """Main entry point"""
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
    except AttributeError:
        pass  # Not available in all PyQt6 versions
    
    app = QApplication(sys.argv)
    app.setApplicationName("BreakGuard")
    app.setOrganizationName("BreakGuard")
    
    # Check if first time setup is needed
    config_path = Path(__file__).parent / 'config.json'
    
    if args.setup or not config_path.exists():
        # Run setup wizard
        from setup_wizard_gui_pyqt import SetupWizard
        wizard = SetupWizard()
        wizard.show()
    elif args.settings:
        # Open settings
        from settings_gui_pyqt import SettingsWindow
        settings = SettingsWindow()
        settings.show()
    else:
        # Run main application
        from work_timer import BreakGuardApp
        break_guard = BreakGuardApp()
        break_guard.start()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
