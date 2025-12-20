"""
Work Timer and System Tray
Main application logic for tracking work time and showing lock screen
"""
from __future__ import annotations

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QAction
from pathlib import Path
import sys
import logging

from config_manager import ConfigManager
from tinxy_api import TinxyAPI
from warning_dialog import WarningDialog
from state_manager import StateManager, AppState
from debug_window import DebugWindow

logger = logging.getLogger(__name__)

class BreakGuardApp(QObject):
    """Main BreakGuard application with timer and system tray"""
    
    # Signals
    lock_requested = pyqtSignal()
    warning_requested = pyqtSignal(int)  # minutes remaining
    
    def __init__(self):
        """Initialize BreakGuard application"""
        super().__init__()
        
        self.config = ConfigManager()
        self.state_manager = StateManager(auto_persist=True)
        self.tray_icon = None
        self.debug_window = None
        self.work_timer = QTimer()
        self.warning_timer = QTimer()
        
        self.time_remaining_seconds = 0
        self.is_paused = False
        self.is_locked = False
        self.snooze_count = 0
        
        # Load saved state (for crash recovery)
        if self.state_manager.load_state():
            logger.info(f"Restored previous state: {self.state_manager.get_state_name()}")
            # Restore timer values if they exist
            saved_time = self.state_manager.get_data('time_remaining_seconds')
            if saved_time is not None:
                self.time_remaining_seconds = saved_time
            saved_snooze = self.state_manager.get_data('snooze_count')
            if saved_snooze is not None:
                self.snooze_count = saved_snooze
        # StateManager already initializes to IDLE state by default, no need to transition
        
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
    
    def _setup_timers(self) -> None:
        """Setup work and warning timers"""
        # Work timer ticks every second
        self.work_timer.timeout.connect(self._on_timer_tick)
        self.work_timer.setInterval(1000)  # 1 second
        
        # Warning timer fires once
        self.warning_timer.timeout.connect(self._show_warning)
        self.warning_timer.setSingleShot(True)
    
    def _setup_tray_icon(self) -> None:
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
        
        # Quick Settings submenu
        quick_settings_menu = menu.addMenu("⚡ Quick Settings")
        
        # Work interval shortcuts
        intervals = [(30, "30 minutes"), (60, "1 hour"), (90, "90 minutes"), (120, "2 hours")]
        for minutes, label in intervals:
            action = QAction(f"🕒 {label}", quick_settings_menu)
            action.triggered.connect(lambda checked, m=minutes: self._quick_change_interval(m))
            quick_settings_menu.addAction(action)
        
        menu.addSeparator()
        
        # Pause/Resume
        self.pause_action = QAction("⏸️ Pause Timer", menu)
        self.pause_action.triggered.connect(self.toggle_pause)
        menu.addAction(self.pause_action)
        
        # Settings
        settings_action = QAction("⚙️ Settings", menu)
        settings_action.triggered.connect(self.open_settings)
        menu.addAction(settings_action)
        
        # Debug Window
        debug_action = QAction("🐛 Debug Info", menu)
        debug_action.triggered.connect(self.open_debug_window)
        menu.addAction(debug_action)
        
        # Run setup again
        setup_action = QAction("🔄 Run Setup Again", menu)
        setup_action.triggered.connect(self.run_setup)
        menu.addAction(setup_action)
        
        menu.addSeparator()
        
        # Skip break (requires authentication)
        skip_action = QAction("⏭️ Skip Current Break", menu)
        skip_action.triggered.connect(self._skip_break)
        menu.addAction(skip_action)
        
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
    
    def _on_tray_activated(self, reason) -> None:
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_status()
    
    def _on_timer_tick(self) -> None:
        """Called every second while timer is running"""
        if self.is_paused or self.is_locked:
            return
        
        self.time_remaining_seconds -= 1
        
        # Persist time remaining every 10 seconds
        if self.time_remaining_seconds % 10 == 0:
            self.state_manager.set_data('time_remaining_seconds', self.time_remaining_seconds)
            self.state_manager.set_data('snooze_count', self.snooze_count)
        
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
    
    def _show_warning(self) -> None:
        """Show warning notification before lock"""
        if not self.state_manager.is_state(AppState.WARNING):
            self.state_manager.transition_to(AppState.WARNING)
        
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
        
        # Start tray icon animation
        self.icon_blink_timer.start(500)  # Blink every 500ms
        
        # Also show tray notification as backup
        if self.tray_icon:
            self.tray_icon.showMessage(
                "⚠️ Break Time Soon",
                f"Break in {warning_mins} minutes - save your work!",
                QSystemTrayIcon.MessageIcon.Warning,
                5000
            )
        
        self.warning_requested.emit(warning_mins)
    
    def _on_snooze(self) -> None:
        """Handle snooze request"""
        self.snooze_count += 1
        
        # Stop icon blinking
        self.icon_blink_timer.stop()
        self._restore_normal_icon()
        
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
    
    def _trigger_lock(self) -> None:
        """Trigger lock screen"""
        self.is_locked = True
        self.work_timer.stop()
        
        # Stop icon blinking
        self.icon_blink_timer.stop()
        self._restore_normal_icon()
        
        # Transition to LOCKED state
        if not self.state_manager.is_state(AppState.LOCKED):
            self.state_manager.transition_to(AppState.LOCKED)
        
        # Turn off monitor via Tinxy if enabled
        if self.tinxy and self.config.is_tinxy_enabled():
            device_num = self.config.get('tinxy_device_number', 1)
            self.tinxy.turn_off(device_num)
        
        # Show lock screen
        from lock_screen_pyqt import LockScreen, OverlayScreen
        self.lock_screen = LockScreen(self.config)
        self.lock_screen.unlocked.connect(self._on_unlock)
        self.lock_screen.showFullScreen()
        
        # Handle multi-monitor
        self.overlays = []
        screens = QApplication.screens()
        if len(screens) > 1:
            # Lock screen is on primary screen by default
            primary = QApplication.primaryScreen()
            for screen in screens:
                if screen != primary:
                    overlay = OverlayScreen()
                    overlay.setGeometry(screen.geometry())
                    overlay.showFullScreen()
                    self.overlays.append(overlay)
        
        self.lock_requested.emit()
    
    def _on_unlock(self) -> None:
        """Called when lock screen is unlocked"""
        self.is_locked = False
        
        # Transition to IDLE state
        if not self.state_manager.is_state(AppState.IDLE):
            self.state_manager.transition_to(AppState.IDLE)
        self.state_manager.set_data('time_remaining_seconds', 0)
        
        # Close overlays
        for overlay in self.overlays:
            overlay.close()
        self.overlays.clear()
        
        # Turn monitor back on via Tinxy if enabled
        if self.tinxy and self.config.is_tinxy_enabled():
            device_num = self.config.get('tinxy_device_number', 1)
            self.tinxy.turn_on(device_num)
        
        # Restart work timer
        self.start()
    
    def start(self) -> None:
        """Start the work timer"""
        # Reset timer to full work interval
        self.time_remaining_seconds = self.config.get_work_interval_seconds()
        self.snooze_count = 0
        
        # Transition to WORKING state (only if not already working)
        if not self.state_manager.is_state(AppState.WORKING):
            self.state_manager.transition_to(AppState.WORKING)
        self.state_manager.set_data('time_remaining_seconds', self.time_remaining_seconds)
        self.state_manager.set_data('snooze_count', self.snooze_count)
        
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
    
    def toggle_pause(self) -> None:
        """Pause or resume timer"""
        if self.is_locked:
            return
        
        if self.is_paused:
            # Resume
            self.is_paused = False
            self.work_timer.start()
            self.pause_action.setText("⏸️ Pause Timer")
            self.status_action.setText("🟢 Active")
            if not self.state_manager.is_state(AppState.WORKING):
                self.state_manager.transition_to(AppState.WORKING)
        else:
            # Pause
            self.is_paused = True
            self.work_timer.stop()
            self.warning_timer.stop()
            self.pause_action.setText("▶️ Resume Timer")
            self.status_action.setText("⏸️ Paused")
            if not self.state_manager.is_state(AppState.PAUSED):
                self.state_manager.transition_to(AppState.PAUSED)
    
    def _quick_change_interval(self, minutes: int) -> None:
        """Quickly change work interval from tray menu
        
        Args:
            minutes: New work interval in minutes
        """
        # Update config
        self.config.set('work_interval_minutes', minutes)
        self.config.save_config()
        
        # Restart timer if running
        if not self.is_paused and not self.is_locked:
            self.start()
            self.tray_icon.showMessage(
                "Work Interval Changed",
                f"Work interval set to {minutes} minutes. Timer restarted.",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
    
    def show_status(self) -> None:
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
    
    def open_settings(self) -> None:
        """Open settings window"""
        from settings_gui_pyqt import SettingsWindow
        self.settings_window = SettingsWindow(self.config)
        self.settings_window.settings_saved.connect(self._on_settings_changed)
        self.settings_window.show()
    
    def open_debug_window(self) -> None:
        """Open debug window for troubleshooting"""
        if not self.debug_window:
            self.debug_window = DebugWindow(self.config)
            self.debug_window.closed.connect(self._on_debug_window_closed)
        self.debug_window.show()
        self.debug_window.raise_()
        self.debug_window.activateWindow()
    
    def _on_debug_window_closed(self) -> None:
        """Handle debug window close"""
        self.debug_window = None
    
    def _on_settings_changed(self) -> None:
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
    
    def run_setup(self) -> None:
        """Run setup wizard again"""
        from setup_wizard_gui_pyqt import SetupWizard
        self.setup_wizard = SetupWizard()
        self.setup_wizard.setup_completed.connect(self._on_settings_changed)
        self.setup_wizard.show()
    
    def _skip_break(self) -> None:
        """Skip current break with authentication"""
        if not self.is_locked:
            self.tray_icon.showMessage(
                "No Active Break",
                "There is no active break to skip.",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
            return
        
        # Show authentication dialog
        from PyQt6.QtWidgets import QInputDialog, QMessageBox
        
        code, ok = QInputDialog.getText(
            None,
            "Skip Break - Authentication Required",
            "Enter your TOTP code to skip this break:",
            QLineEdit.EchoMode.Normal
        )
        
        if not ok or not code:
            return
        
        # Verify TOTP code
        from totp_auth import TOTPAuth
        totp = TOTPAuth()
        totp.load_secret()
        
        if totp.verify_code(code):
            # Unlock and skip break
            if self.lock_screen:
                self.lock_screen.close()
            self._on_unlock()
            
            self.tray_icon.showMessage(
                "Break Skipped",
                "Break skipped successfully. Timer restarted.",
                QSystemTrayIcon.MessageIcon.Information,
                3000
            )
        else:
            QMessageBox.warning(
                None,
                "Authentication Failed",
                "Invalid TOTP code. Break not skipped."
            )
    
    def _blink_icon(self) -> None:
        """Animate tray icon by alternating between full and dimmed states"""
        if not self.tray_icon:
            return
        
        # Toggle state
        self.icon_blink_state = not self.icon_blink_state
        
        # Get original icon
        assets_dir = Path(__file__).parent.parent / 'assets'
        icon_path = assets_dir / 'logo.png'
        
        if icon_path.exists():
            original_icon = QIcon(str(icon_path))
            
            if self.icon_blink_state:
                # Bright icon
                self.tray_icon.setIcon(original_icon)
            else:
                # Create dimmed version
                pixmap = original_icon.pixmap(64, 64)
                dimmed = pixmap.copy()
                # Simple dimming by reducing alpha
                painter = QPainter(dimmed)
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
                painter.fillRect(dimmed.rect(), QColor(0, 0, 0, 128))
                painter.end()
                self.tray_icon.setIcon(QIcon(dimmed))
    
    def _restore_normal_icon(self) -> None:
        """Restore tray icon to normal state"""
        if not self.tray_icon:
            return
        
        assets_dir = Path(__file__).parent.parent / 'assets'
        icon_path = assets_dir / 'logo.png'
        
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        else:
            self.tray_icon.setIcon(QApplication.style().standardIcon(
                QApplication.style().StandardPixmap.SP_ComputerIcon
            ))
        
        self.icon_blink_state = False
    
    def exit_app(self) -> None:
        """Exit the application"""
        self.work_timer.stop()
        self.warning_timer.stop()
        self.icon_blink_timer.stop()
        
        if self.tray_icon:
            self.tray_icon.hide()
        
        QApplication.quit()
