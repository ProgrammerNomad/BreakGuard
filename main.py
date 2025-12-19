"""
BreakGuard - Main Application Entry Point
Health-discipline application that enforces regular breaks
"""
import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config_manager import ConfigManager
from tinxy_api import TinxyAPI, MonitorController
from work_timer import WorkTimer
from totp_auth import TOTPAuth
from face_verification import FaceVerification
from lock_screen import LockScreen, SimpleLockScreen
from windows_startup import WindowsStartup
from setup_wizard_gui_pyqt import SetupWizard, run_setup_wizard
from settings_gui import SettingsWindow

import pystray
from PIL import Image, ImageDraw
import threading

class BreakGuard:
    """Main BreakGuard application"""
    
    def __init__(self):
        print("=== BreakGuard Starting ===")
        
        # Load configuration
        self.config = ConfigManager()
        
        # Initialize components
        self.totp_auth = None
        self.face_verification = None
        self.monitor_controller = None
        self.work_timer = None
        self.tray_icon = None
        
        # Setup
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all components"""
        # TOTP Authentication
        totp_secret = self.config.get('totp_secret')
        if totp_secret:
            self.totp_auth = TOTPAuth(totp_secret)
            print("✓ TOTP authentication loaded")
        else:
            print("⚠ TOTP not configured")
        
        # Face Verification
        self.face_verification = FaceVerification()
        if self.face_verification.is_registered():
            print("✓ Face verification loaded")
        else:
            print("⚠ Face verification not configured")
        
        # Tinxy API & Monitor Control
        tinxy_key = self.config.get('tinxy_api_key')
        tinxy_device = self.config.get('tinxy_device_id')
        tinxy_number = self.config.get('tinxy_device_number', 1)
        
        if tinxy_key and tinxy_device:
            tinxy_api = TinxyAPI(tinxy_key, tinxy_device, tinxy_number)
            self.monitor_controller = MonitorController(tinxy_api)
            print("✓ Tinxy API configured")
        else:
            self.monitor_controller = MonitorController()
            print("⚠ Tinxy API not configured - using fallback only")
        
        # Work Timer
        work_interval = self.config.get('work_interval_minutes', 60)
        warning_before = self.config.get('warning_before_minutes', 5)
        
        self.work_timer = WorkTimer(
            work_interval_minutes=work_interval,
            warning_before_minutes=warning_before,
            on_warning=self._on_warning,
            on_lock=self._on_lock
        )
        
        print(f"✓ Work timer configured ({work_interval} minutes)")
    
    def _on_warning(self):
        """Called before lock - show warning notification"""
        warning_minutes = self.config.get('warning_before_minutes', 5)
        print(f"\n⚠ WARNING: Break in {warning_minutes} minutes!")
        
        # Could add Windows notification here
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(
                "BreakGuard Warning",
                f"Break time in {warning_minutes} minutes. Save your work!",
                duration=10,
                threaded=True
            )
        except:
            pass
    
    def _on_lock(self):
        """Called when it's time to lock"""
        print("\n🔒 LOCK TIME - Enforcing break!")
        
        # Turn off monitor
        if self.monitor_controller:
            self.monitor_controller.turn_off()
        
        # Show lock screen
        self._show_lock_screen()
    
    def _show_lock_screen(self):
        """Display the lock screen"""
        auth_enabled = self.config.get('auth_enabled', True)
        face_enabled = self.config.get('face_verification', True)
        
        if auth_enabled and self.totp_auth:
            # Full lock screen with TOTP and face
            lock = LockScreen(
                totp_auth=self.totp_auth,
                face_verification=self.face_verification,
                on_unlock=self._on_unlock,
                auth_enabled=auth_enabled,
                face_enabled=face_enabled
            )
            lock.show()
        else:
            # Simple lock screen (for testing)
            lock = SimpleLockScreen(on_unlock=self._on_unlock)
            lock.show()
    
    def _on_unlock(self):
        """Called when screen is unlocked"""
        print("\n✓ Unlocked - Starting new work session")
        
        # Turn monitor back on
        if self.monitor_controller:
            self.monitor_controller.turn_on()
        
        # Reset and restart timer
        self.work_timer.reset()
        self.work_timer.start()
    
    def _create_tray_icon(self):
        """Create system tray icon"""
        # Create icon image
        def create_icon_image():
            width = 64
            height = 64
            image = Image.new('RGB', (width, height), color='#00a8ff')
            dc = ImageDraw.Draw(image)
            
            # Draw a simple pause icon
            dc.rectangle([15, 15, 25, 49], fill='white')
            dc.rectangle([39, 15, 49, 49], fill='white')
            
            return image
        
        icon_image = create_icon_image()
        
        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem(
                'BreakGuard',
                lambda: None,
                enabled=False
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                lambda text: f'Time Remaining: {self.work_timer.get_time_remaining_formatted()}',
                lambda: None,
                enabled=False
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                'Pause Timer',
                self._pause_timer
            ),
            pystray.MenuItem(
                'Resume Timer',
                self._resume_timer
            ),
            pystray.MenuItem(
                'Reset Timer',
                self._reset_timer
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                'Settings',
                self._show_settings
            ),
            pystray.MenuItem(
                'Exit',
                self._exit_app
            )
        )
        
        self.tray_icon = pystray.Icon(
            'BreakGuard',
            icon_image,
            'BreakGuard',
            menu
        )
    
    def _pause_timer(self):
        """Pause the work timer"""
        self.work_timer.pause()
    
    def _resume_timer(self):
        """Resume the work timer"""
        self.work_timer.resume()
    
    def _reset_timer(self):
        """Reset the work timer"""
        self.work_timer.reset()
        self.work_timer.start()
    
    def _show_settings(self):
        """Show settings dialog"""
        settings = SettingsWindow(on_save=self._on_settings_saved)
        settings.show()
    
    def _on_settings_saved(self):
        """Called when settings are saved"""
        # Reload configuration
        self.config = ConfigManager()
        print("Settings updated. Changes will take effect on next break cycle.")
    
    def _exit_app(self):
        """Exit the application"""
        print("\nExiting BreakGuard...")
        self.work_timer.stop()
        if self.tray_icon:
            self.tray_icon.stop()
        sys.exit(0)
    
    def run(self):
        """Run the application"""
        # Check and enable Windows startup if configured
        auto_start = self.config.get('auto_start', True)
        if auto_start and not WindowsStartup.is_enabled():
            print("\n⚙ Enabling Windows startup...")
            WindowsStartup.enable()
        
        # Start work timer
        self.work_timer.start()
        
        # Create and run system tray icon
        self._create_tray_icon()
        
        print("\n✓ BreakGuard is running")
        print(f"  Next break in: {self.work_timer.get_time_remaining_formatted()}")
        print("  Check system tray for controls\n")
        
        # Run tray icon (blocks until exit)
        self.tray_icon.run()

def setup_wizard():
    """First-time setup wizard with GUI"""
    run_setup_wizard()

def main():
    """Main entry point"""
    # Check if this is first run
    config = ConfigManager()
    
    # Handle setup argument
    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        setup_wizard()
        return
    
    # Check if configuration exists (first run)
    if not config.get('totp_secret'):
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        
        result = messagebox.askyesno(
            "Welcome to BreakGuard",
            "This appears to be your first time running BreakGuard.\n\n"
            "Would you like to run the setup wizard?\n\n"
            "(You can also run 'python main.py --setup' later)",
            icon='question'
        )
        
        root.destroy()
        
        if result:
            setup_wizard()
            # After setup, start the app
            config = ConfigManager()  # Reload config
        else:
            print("\n⚠ BreakGuard is not configured.")
            print("Run 'python main.py --setup' to configure.\n")
            return
    
    # Run application
    app = BreakGuard()
    app.run()

if __name__ == "__main__":
    main()
