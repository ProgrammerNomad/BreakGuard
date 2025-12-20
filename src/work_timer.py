"""
Work Timer and System Tray
Main application logic for tracking work time and showing lock screen
"""

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QAction
from pathlib import Path
import sys

from config_manager import ConfigManager
from tinxy_api import TinxyAPI
from warning_dialog import WarningDialog

class BreakGuardApp(QObject):
    """Main BreakGuard application with timer and system tray"""
    
    # Signals
    lock_requested = pyqtSignal()
    warning_requested = pyqtSignal(int)  # minutes remaining
    
    def __init__(self):
        """Initialize BreakGuard application"""
        super().__init__()
        
        self.config = ConfigManager()
        self.tray_icon = None
        self.work_timer = QTimer()
        self.warning_timer = QTimer()
        
        self.time_remaining_seconds = 0
        self.is_paused = False
        self.is_locked = False
        self.snooze_count = 0
        
        # Tinxy API (optional)
        if self.config.is_tinxy_enabled():
            tinxy_creds = self.config.get_tinxy_credentials()
            self.tinxy = TinxyAPI(
                tinxy_creds['api_key'],
                tinxy_creds['device_id']
            )
        else:
            self.tinxy = None
        
        self._setup_timers()
        self._setup_tray_icon()
    
    def _setup_timers(self):
        """Setup work and warning timers"""
        # Work timer ticks every second
        self.work_timer.timeout.connect(self._on_timer_tick)
        self.work_timer.setInterval(1000)  # 1 second
        
        # Warning timer fires once
        self.warning_timer.timeout.connect(self._show_warning)
        self.warning_timer.setSingleShot(True)
    
    def _setup_tray_icon(self):
        """Create system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon()
        
        # Load icon
        assets_dir = Path(__file__).parent.parent / 'assets'
        icon_path = assets_dir / 'logo.png'
        
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        else:
            self.tray_icon.setIcon(QApplication.style().standardIcon(
                QApplication.style().StandardPixmap.SP_ComputerIcon
            ))
        
        # Create menu
        menu = QMenu()
        
        # Status action (not clickable, just shows info)
        self.status_action = QAction("🟢 Active", menu)
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)
        
        menu.addSeparator()
        
        # Pause/Resume
        self.pause_action = QAction("⏸️ Pause Timer", menu)
        self.pause_action.triggered.connect(self.toggle_pause)
        menu.addAction(self.pause_action)
        
        # Settings
        settings_action = QAction("⚙️ Settings", menu)
        settings_action.triggered.connect(self.open_settings)
        menu.addAction(settings_action)
        
        # Run setup again
        setup_action = QAction("🔄 Run Setup Again", menu)
        setup_action.triggered.connect(self.run_setup)
        menu.addAction(setup_action)
        
        menu.addSeparator()
        
        # Exit
        exit_action = QAction("🚪 Exit BreakGuard", menu)
        exit_action.triggered.connect(self.exit_app)
        menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.setToolTip("BreakGuard - Your Health Guardian")
        
        # Double-click to show status
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        self.tray_icon.show()
    
    def _on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_status()
    
    def _on_timer_tick(self):
        """Called every second while timer is running"""
        if self.is_paused or self.is_locked:
            return
        
        self.time_remaining_seconds -= 1
        
        # Update tray tooltip
        minutes = self.time_remaining_seconds // 60
        seconds = self.time_remaining_seconds % 60
        self.tray_icon.setToolTip(
            f"BreakGuard - {minutes}:{seconds:02d} remaining"
        )
        
        # Update status action
        self.status_action.setText(
            f"🟢 Active ({minutes} min remaining)"
        )
        
        # Check if time's up
        if self.time_remaining_seconds <= 0:
            self._trigger_lock()
    
    def _show_warning(self):
        """Show warning notification before lock"""
        warning_mins = self.config.get('warning_before_minutes', 5)
        work_interval = self.config.get('work_interval_minutes', 60)
        max_snooze = self.config.get('max_snooze_count', 1)
        
        # Calculate work duration (approximate)
        work_duration = work_interval - warning_mins
        
        # Show dialog
        can_snooze = self.snooze_count < max_snooze
        self.warning_dialog = WarningDialog(warning_mins, work_duration, can_snooze)
        self.warning_dialog.snooze_requested.connect(self._on_snooze)
        self.warning_dialog.show()
        
        # Also show tray notification as backup
        if self.tray_icon:
            self.tray_icon.showMessage(
                "⚠️ Break Time Soon",
                f"Break in {warning_mins} minutes - save your work!",
                QSystemTrayIcon.MessageIcon.Warning,
                5000
            )
        
        self.warning_requested.emit(warning_mins)
    
    def _on_snooze(self):
        """Handle snooze request"""
        self.snooze_count += 1
        
        # Add 5 minutes to timer
        self.time_remaining_seconds += (5 * 60)
        
        # Restart warning timer for next warning
        warning_seconds = self.config.get_warning_time_seconds()
        if self.time_remaining_seconds > warning_seconds:
            warning_delay = (self.time_remaining_seconds - warning_seconds) * 1000
            self.warning_timer.start(warning_delay)
            
        self.tray_icon.showMessage(
            "💤 Snoozed",
            "Break snoozed for 5 minutes.",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
    
    def _trigger_lock(self):
        """Trigger lock screen"""
        self.is_locked = True
        self.work_timer.stop()
        
        # Turn off monitor via Tinxy if enabled
        if self.tinxy and self.config.is_tinxy_enabled():
            device_num = self.config.get('tinxy_device_number', 1)
            self.tinxy.turn_off(device_num)
        
        # Show lock screen
        from lock_screen_pyqt import LockScreen
        self.lock_screen = LockScreen(self.config)
        self.lock_screen.unlocked.connect(self._on_unlock)
        self.lock_screen.showFullScreen()
        
        self.lock_requested.emit()
    
    def _on_unlock(self):
        """Called when lock screen is unlocked"""
        self.is_locked = False
        
        # Turn monitor back on via Tinxy if enabled
        if self.tinxy and self.config.is_tinxy_enabled():
            device_num = self.config.get('tinxy_device_number', 1)
            self.tinxy.turn_on(device_num)
        
        # Restart work timer
        self.start()
    
    def start(self):
        """Start the work timer"""
        # Reset timer to full work interval
        self.time_remaining_seconds = self.config.get_work_interval_seconds()
        self.snooze_count = 0
        
        # Schedule warning
        warning_seconds = self.config.get_warning_time_seconds()
        if warning_seconds > 0 and warning_seconds < self.time_remaining_seconds:
            warning_delay = (self.time_remaining_seconds - warning_seconds) * 1000
            self.warning_timer.start(warning_delay)
        
        # Start work timer
        self.is_paused = False
        self.work_timer.start()
        
        # Update tray
        self.status_action.setText("🟢 Active")
        self.tray_icon.showMessage(
            "BreakGuard Started",
            f"Work timer started. Break in {self.time_remaining_seconds // 60} minutes.",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
    
    def toggle_pause(self):
        """Pause or resume timer"""
        if self.is_locked:
            return
        
        if self.is_paused:
            # Resume
            self.is_paused = False
            self.work_timer.start()
            self.pause_action.setText("⏸️ Pause Timer")
            self.status_action.setText("🟢 Active")
        else:
            # Pause
            self.is_paused = True
            self.work_timer.stop()
            self.warning_timer.stop()
            self.pause_action.setText("▶️ Resume Timer")
            self.status_action.setText("⏸️ Paused")
    
    def show_status(self):
        """Show status window or notification"""
        minutes = self.time_remaining_seconds // 60
        
        if self.is_paused:
            status = "Paused"
        elif self.is_locked:
            status = "Break time - Locked"
        else:
            status = f"Active - {minutes} min remaining"
        
        self.tray_icon.showMessage(
            "BreakGuard Status",
            status,
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
    
    def open_settings(self):
        """Open settings window"""
        from settings_gui_pyqt import SettingsWindow
        self.settings_window = SettingsWindow(self.config)
        self.settings_window.settings_saved.connect(self._on_settings_changed)
        self.settings_window.show()
    
    def _on_settings_changed(self):
        """Handle settings changes"""
        # Reload config
        self.config = ConfigManager()
        
        # Update Tinxy if needed
        if self.config.is_tinxy_enabled():
            tinxy_creds = self.config.get_tinxy_credentials()
            self.tinxy = TinxyAPI(
                tinxy_creds['api_key'],
                tinxy_creds['device_id']
            )
        else:
            self.tinxy = None
        
        # Restart timer if not locked
        if not self.is_locked:
            self.work_timer.stop()
            self.warning_timer.stop()
            self.start()
    
    def run_setup(self):
        """Run setup wizard again"""
        from setup_wizard_gui_pyqt import SetupWizard
        self.setup_wizard = SetupWizard()
        self.setup_wizard.setup_completed.connect(self._on_settings_changed)
        self.setup_wizard.show()
    
    def exit_app(self):
        """Exit the application"""
        self.work_timer.stop()
        self.warning_timer.stop()
        
        if self.tray_icon:
            self.tray_icon.hide()
        
        QApplication.quit()
