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
from totp_auth import TOTPAuth, TOTPSetup
from face_verification import FaceVerification
from lock_screen import LockScreen, SimpleLockScreen
from windows_startup import WindowsStartup

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
        print("Settings dialog not yet implemented")
        # TODO: Create settings GUI
    
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
    """First-time setup wizard"""
    print("\n" + "="*60)
    print(" BreakGuard - First Time Setup")
    print("="*60 + "\n")
    
    config = ConfigManager()
    
    # Configure work interval
    print("1. Configure Work Interval")
    work_interval = input(f"  Work interval in minutes (default: 60): ").strip()
    if work_interval.isdigit():
        config.set('work_interval_minutes', int(work_interval))
    
    warning_before = input(f"  Warning before lock in minutes (default: 5): ").strip()
    if warning_before.isdigit():
        config.set('warning_before_minutes', int(warning_before))
    
    # Configure TOTP
    print("\n2. Configure Google Authenticator (TOTP)")
    setup_totp = input("  Setup TOTP authentication? (y/n): ").strip().lower()
    
    if setup_totp == 'y':
        totp_auth, qr_path = TOTPSetup.first_time_setup()
        
        print(f"\n  QR Code saved to: {qr_path}")
        print("  Scan this with Google Authenticator app")
        input("\n  Press Enter when you've scanned the QR code...")
        
        if TOTPSetup.verify_setup(totp_auth):
            config.set('totp_secret', totp_auth.get_secret())
            config.set('auth_enabled', True)
        else:
            print("  Setup incomplete - you can configure this later")
            config.set('auth_enabled', False)
    else:
        config.set('auth_enabled', False)
    
    # Configure Face Verification
    print("\n3. Configure Face Verification")
    setup_face = input("  Setup face verification? (y/n): ").strip().lower()
    
    if setup_face == 'y':
        face_verif = FaceVerification()
        if face_verif.register_face():
            config.set('face_verification', True)
        else:
            print("  Face registration failed - you can configure this later")
            config.set('face_verification', False)
    else:
        config.set('face_verification', False)
    
    # Configure Tinxy API
    print("\n4. Configure Tinxy API (Optional)")
    setup_tinxy = input("  Setup Tinxy API for monitor control? (y/n): ").strip().lower()
    
    if setup_tinxy == 'y':
        api_key = input("  Tinxy API Key: ").strip()
        device_id = input("  Tinxy Device ID: ").strip()
        device_number = input("  Device Number (default: 1): ").strip()
        
        if api_key and device_id:
            config.set('tinxy_api_key', api_key)
            config.set('tinxy_device_id', device_id)
            config.set('tinxy_device_number', int(device_number) if device_number.isdigit() else 1)
    
    # Save configuration
    config.save_config()
    
    print("\n" + "="*60)
    print(" Setup Complete!")
    print("="*60)
    print("\n✓ Configuration saved")
    print("✓ BreakGuard is ready to use")
    print("\nRun 'python main.py' to start BreakGuard\n")

def main():
    """Main entry point"""
    # Check if this is first run
    config = ConfigManager()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        setup_wizard()
        return
    
    # Check if TOTP is configured
    if not config.get('totp_secret') and config.get('auth_enabled', True):
        print("\n⚠ TOTP authentication not configured")
        print("Run 'python main.py --setup' to configure BreakGuard\n")
        
        proceed = input("Continue without TOTP? (y/n): ").strip().lower()
        if proceed != 'y':
            return
    
    # Run application
    app = BreakGuard()
    app.run()

if __name__ == "__main__":
    main()
