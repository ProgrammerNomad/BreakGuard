"""
Lock Screen GUI (PyQt6)
Fullscreen lock interface with TOTP and face verification
"""
from __future__ import annotations

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QFrame, QApplication,
                             QTabWidget, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QPropertyAnimation, QSequentialAnimationGroup, QPoint
from PyQt6.QtGui import QFont, QImage, QPixmap, QKeyEvent, QKeySequence
import cv2
import os
import logging
from datetime import datetime

from config_manager import ConfigManager
from totp_auth import TOTPAuth
from face_verification import FaceVerification
from keyboard_blocker import KeyboardBlocker
from theme.theme import load_stylesheet

logger = logging.getLogger(__name__)

class CameraThread(QThread):
    """Thread for camera capture"""
    frame_ready = pyqtSignal(object)
    
    def __init__(self, camera_index=0):
        super().__init__()
        self.running = False
        self.camera = None
        self.camera_index = camera_index
    
    def run(self) -> None:
        """Run camera capture loop"""
        # Use CAP_DSHOW for Windows compatibility
        self.camera = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        self.running = True
        
        while self.running:
            ret, frame = self.camera.read()
            if ret:
                self.frame_ready.emit(frame)
            self.msleep(33)  # ~30 FPS
    
    def stop(self) -> None:
        """Stop camera capture"""
        self.running = False
        if self.camera:
            self.camera.release()

class LockScreen(QWidget):
    """Fullscreen lock screen with authentication"""
    
    unlocked = pyqtSignal()
    
    def __init__(self, config: ConfigManager = None):
        """Initialize lock screen
        
        Args:
            config: ConfigManager instance
        """
        super().__init__()
        
        self.config = config or ConfigManager()
        self.totp = TOTPAuth()
        
        # Initialize components with error handling
        try:
            self.face_verifier = FaceVerification()
        except Exception as e:
            logger.error(f"Failed to initialize FaceVerification: {e}")
            self.face_verifier = None
            
        try:
            self.keyboard_blocker = KeyboardBlocker()
        except Exception as e:
            logger.error(f"Failed to initialize KeyboardBlocker: {e}")
            self.keyboard_blocker = None
        
        self.attempts_remaining = 5
        self.lockout_count = 0  # Track number of lockouts for exponential backoff
        self.camera_thread = None
        self.current_frame = None
        
        # Break duration
        self.break_remaining_seconds = self.config.get('break_duration_minutes', 5) * 60
        
        self._setup_ui()
        self._load_authentication()
        
        # Start blocking keyboard
        if self.keyboard_blocker:
            try:
                self.keyboard_blocker.start()
            except Exception as e:
                logger.error(f"Failed to start KeyboardBlocker: {e}")
        
        # Start Task Manager killer
        self.tm_timer = QTimer()
        self.tm_timer.timeout.connect(self._check_task_manager)
        self.tm_timer.start(500)  # Check every 500ms
        
        # Block keyboard shortcuts
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Fade in animation
        self.setWindowOpacity(0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
    
    def _setup_ui(self) -> None:
        """Setup lock screen UI"""
        # Make fullscreen and always on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # Set object name for styling
        self.setObjectName("LockScreen")
        # Theme is loaded at app level in main.py
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)
        
        # Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        from pathlib import Path
        assets_dir = Path(__file__).parent.parent / 'assets'
        logo_path = assets_dir / 'logo.png'
        
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            scaled_pixmap = pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            layout.addWidget(logo_label)
        
        # Title
        title = QLabel("BREAK TIME")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 48, QFont.Weight.Bold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Time to take a break and rest your eyes")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont("Segoe UI", 16)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #8c8c8c;")  # WCAG AA compliant on dark background
        layout.addWidget(subtitle)
        
        # Current time
        self.time_label = QLabel(datetime.now().strftime("%I:%M %p"))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_font = QFont("Segoe UI", 24)
        self.time_label.setFont(time_font)
        self.time_label.setStyleSheet("color: #8c8c8c;")  # WCAG AA compliant
        layout.addWidget(self.time_label)
        
        # Update time every second
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self._update_time)
        self.time_timer.start(1000)
        
        layout.addSpacing(30)
        
        # Authentication Tabs
        self.auth_tabs = QTabWidget()
        self.auth_tabs.setMaximumWidth(650)
        self.auth_tabs.setMinimumWidth(320)
        self.auth_tabs.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.auth_tabs.setAccessibleName("Authentication methods")
        self.auth_tabs.setAccessibleName("Authentication methods")
        
        # TOTP Tab
        if self.config.is_totp_enabled():
            totp_frame = self._create_totp_section()
            # Remove frame styling as it's now inside tab
            totp_frame.setStyleSheet("background-color: transparent;")
            self.auth_tabs.addTab(totp_frame, "🔐 Authenticator Code")
            
        # Face Verification Tab
        if self.config.is_face_verification_enabled() and self.face_verifier:
            face_frame = self._create_face_section()
            face_frame.setStyleSheet("background-color: transparent;")
            self.auth_tabs.addTab(face_frame, "👤 Face Verification")
            
        # Handle tab changes
        self.auth_tabs.currentChanged.connect(self._on_tab_changed)
        
        layout.addWidget(self.auth_tabs, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Status message
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_font = QFont("Segoe UI", 14)
        self.status_label.setFont(status_font)
        self.status_label.setAccessibleName("Status message")
        layout.addWidget(self.status_label)
        
        # Attempts remaining
        self.attempts_label = QLabel(f"Attempts remaining: {self.attempts_remaining}/5")
        self.attempts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.attempts_label.setStyleSheet("color: #ffa500;")
        self.attempts_label.setAccessibleName("Attempts remaining")
        layout.addWidget(self.attempts_label)
        
        layout.addSpacing(20)
        
        # Break duration timer
        self.break_timer_label = QLabel(self._format_break_time())
        self.break_timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.break_timer_label.setFont(QFont("Segoe UI", 18))
        self.break_timer_label.setStyleSheet("color: #ffffff;")
        self.break_timer_label.setAccessibleName("Break time remaining")
        layout.addWidget(self.break_timer_label)
    
    def _create_totp_section(self) -> QFrame:
        """Create TOTP input section"""
        self.totp_frame = QFrame()
        self.totp_frame.setMaximumWidth(600)
        
        layout = QVBoxLayout(self.totp_frame)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🔐 Enter Google Authenticator Code")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 16, QFont.Weight.Bold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # 6-digit input boxes
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        self.otp_inputs = []
        for i in range(6):
            input_box = QLineEdit()
            input_box.setMaxLength(1)
            input_box.setMinimumSize(50, 60)
            input_box.setMaximumSize(80, 90)
            input_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
            input_box.setProperty("class", "otp-input")
            input_box.setAccessibleName(f"Digit {i+1}")
            input_box.textChanged.connect(lambda text, idx=i: self._on_digit_entered(text, idx))
            # Track focus for visual indication
            input_box.focusInEvent = lambda event, idx=i: self._on_otp_focus_in(event, idx)
            input_box.focusOutEvent = lambda event, idx=i: self._on_otp_focus_out(event, idx)
            # Install event filter for paste support
            input_box.installEventFilter(self)
            self.otp_inputs.append(input_box)
            input_layout.addWidget(input_box)
        
        layout.addLayout(input_layout)
        
        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self._clear_totp_inputs)
        self.clear_button.setToolTip("Clear all digits (Esc)")
        self.clear_button.setAccessibleName("Clear TOTP inputs")
        self.clear_button.setMaximumWidth(100)
        layout.addWidget(self.clear_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Unlock button
        self.unlock_button = QPushButton("&Unlock")
        self.unlock_button.clicked.connect(self._verify_totp)
        self.unlock_button.setToolTip("Click or press Alt+U to unlock screen")
        self.unlock_button.setAccessibleName("Unlock button")
        self.unlock_button.setShortcut("Alt+U")
        
        # Loading indicator (spinner animation)
        self.loading_label = QLabel("⟳ Verifying...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("color: #0d7377; font-weight: bold;")
        self.loading_label.setVisible(False)  # Hidden by default
        self.loading_spinner_timer = QTimer()
        self.spinner_index = 0
        self.spinner_chars = ["⟳", "⟳", "⟳"]  # Animation frames
        self.loading_spinner_timer.timeout.connect(self._update_spinner)
        
        # Set tab order for OTP inputs
        if self.otp_inputs:
            for i in range(len(self.otp_inputs) - 1):
                self.totp_frame.setTabOrder(self.otp_inputs[i], self.otp_inputs[i+1])
            self.totp_frame.setTabOrder(self.otp_inputs[-1], self.clear_button)
            self.totp_frame.setTabOrder(self.clear_button, self.unlock_button)
        
        # Button layout with loading indicator
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.unlock_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Loading indicator layout
        layout.addWidget(self.loading_label)
        
        # Info
        info = QLabel("💡 Code changes every 30 seconds")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #b3b3b3; font-size: 12px;")  # Better contrast on dark background
        layout.addWidget(info)
        
        return self.totp_frame
    
    def _create_face_section(self) -> QFrame:
        """Create face verification section"""
        frame = QFrame()
        frame.setMaximumWidth(600)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("👤 Face Verification")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 16, QFont.Weight.Bold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Camera preview
        self.camera_label = QLabel("Camera preview will appear here")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setMinimumSize(400, 300)
        self.camera_label.setProperty("class", "qr-box")
        self.camera_label.setAccessibleName("Camera preview")
        layout.addWidget(self.camera_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Scan button
        self.scan_button = QPushButton("Scan Face")
        self.scan_button.clicked.connect(self._start_face_scan)
        self.scan_button.setToolTip("Start face scanning for verification")
        self.scan_button.setAccessibleName("Scan Face button")
        layout.addWidget(self.scan_button)
        
        # Face verification loading indicator
        self.face_loading_label = QLabel("⟳ Analyzing face...")
        self.face_loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.face_loading_label.setStyleSheet("color: #0d7377; font-weight: bold;")
        self.face_loading_label.setVisible(False)
        layout.addWidget(self.face_loading_label)
        
        # Set tab order
        frame.setTabOrder(self.scan_button, self.scan_button)
        
        return frame
    
    def eventFilter(self, obj, event):
        """Event filter for paste support"""
        if event.type() == QKeyEvent.Type.KeyPress:
            if event.matches(QKeySequence.StandardKey.Paste):
                # Handle paste event
                clipboard = QApplication.clipboard()
                text = clipboard.text().strip()
                
                # Check if it's a 6-digit code
                if text.isdigit() and len(text) == 6:
                    # Fill all input boxes
                    for i, digit in enumerate(text):
                        self.otp_inputs[i].setText(digit)
                    # Auto-submit
                    self._verify_totp()
                    return True
        
        return super().eventFilter(obj, event)
    
    def _clear_totp_inputs(self) -> None:
        """Clear all TOTP input boxes"""
        for box in self.otp_inputs:
            box.clear()
        self.otp_inputs[0].setFocus()
        self._show_status("", False)
    
    def _clear_totp_inputs_after_error(self) -> None:
        """Clear TOTP inputs after showing error message"""
        for box in self.otp_inputs:
            box.clear()
        self.otp_inputs[0].setFocus()
    
    def _on_digit_entered(self, text: str, index: int) -> None:
        """Handle digit entry in OTP boxes"""
        if text and index < 5:
            # Move to next box
            self.otp_inputs[index + 1].setFocus()
        
        # Auto-submit when all 6 digits entered
        if all(box.text() for box in self.otp_inputs):
            self._verify_totp()
    
    def _on_otp_focus_in(self, event, index: int) -> None:
        """Handle TOTP input gaining focus - add visual indicator"""
        input_box = self.otp_inputs[index]
        # Add active class for enhanced styling
        input_box.setProperty("active", True)
        input_box.setStyleSheet(input_box.styleSheet())  # Force refresh
        # Call original handler
        QLineEdit.focusInEvent(input_box, event)
    
    def _on_otp_focus_out(self, event, index: int) -> None:
        """Handle TOTP input losing focus - remove visual indicator"""
        input_box = self.otp_inputs[index]
        # Remove active class
        input_box.setProperty("active", False)
        input_box.setStyleSheet(input_box.styleSheet())  # Force refresh
        # Call original handler
        QLineEdit.focusOutEvent(input_box, event)
    
    def _verify_totp(self) -> None:
        """Verify TOTP code"""
        # Get code from input boxes
        code = ''.join(box.text() for box in self.otp_inputs)
        
        if len(code) != 6:
            self._show_status("Please enter all 6 digits", False)
            return
        
        # Show loading indicator
        self._show_loading(True)
        self.unlock_button.setEnabled(False)
        
        # Disable inputs during verification
        for box in self.otp_inputs:
            box.setEnabled(False)
        self.clear_button.setEnabled(False)
        
        # Verify
        if self.totp.verify_code(code):
            self._show_status("✅ Code verified!", True)
            QTimer.singleShot(500, self._unlock)  # Give user feedback before unlocking
        else:
            # Hide loading and re-enable inputs on failure
            self._show_loading(False)
            self.unlock_button.setEnabled(True)
            for box in self.otp_inputs:
                box.setEnabled(True)
            self.clear_button.setEnabled(True)
            
            self.attempts_remaining -= 1
            self.attempts_label.setText(f"Attempts remaining: {self.attempts_remaining}/5")
            
            if self.attempts_remaining <= 0:
                # Exponential backoff: 1m, 5m, 15m
                self.lockout_count += 1
                lockout_times = [60, 300, 900]  # seconds
                lockout_duration = lockout_times[min(self.lockout_count - 1, len(lockout_times) - 1)]
                minutes = lockout_duration // 60
                
                self._show_status(f"❌ Too many attempts! Locked for {minutes} minute(s)", False)
                self._shake_totp_inputs()
                self._disable_inputs(lockout_duration)
                
                # Log security event
                logger.warning(f"Authentication lockout #{self.lockout_count} triggered: {lockout_duration}s")
            else:
                self._show_status("❌ Invalid code!", False)
                self._shake_totp_inputs()
                
                # Clear inputs after 1 second
                QTimer.singleShot(1000, self._clear_totp_inputs_after_error)
                self._shake_totp_inputs()
            
            # Clear inputs
            for box in self.otp_inputs:
                box.clear()
            self.otp_inputs[0].setFocus()
    
    def _start_face_scan(self):
        """Start camera for face scanning"""
        if not self.camera_thread:
            camera_idx = int(self.config.get('camera_index', 0))
            self.camera_thread = CameraThread(camera_idx)
            self.camera_thread.frame_ready.connect(self._on_camera_frame)
            self.camera_thread.start()
            
            self.scan_button.setText("Verifying...")
            self.scan_button.setEnabled(False)
            
            # Auto-verify after 3 seconds
            QTimer.singleShot(3000, self._verify_face)
    
    def _on_camera_frame(self, frame) -> None:
        """Update camera preview"""
        self.current_frame = frame
        
        # Draw face rectangle
        frame_with_rect = self.face_verifier.draw_face_rectangle(frame.copy())
        
        # Convert to QPixmap
        rgb_frame = cv2.cvtColor(frame_with_rect, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        # Scale to fit label
        scaled = pixmap.scaled(
            self.camera_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.camera_label.setPixmap(scaled)
    
    def _verify_face(self):
        """Verify face from camera"""
        # Show loading indicator
        self.face_loading_label.setVisible(True)
        self.loading_spinner_timer.start(300) if not self.loading_spinner_timer.isActive() else None
        
        if self.current_frame is None:
            self._show_status("❌ No camera frame available", False)
            self.face_loading_label.setVisible(False)
            self._stop_camera()
            return
        
        if self.face_verifier.verify_face(self.current_frame):
            self.face_loading_label.setVisible(False)
            self._show_status("✅ Face verified!", True)
            self._stop_camera()
            QTimer.singleShot(500, self._unlock)
        else:
            self.face_loading_label.setVisible(False)
            self.attempts_remaining -= 1
            self.attempts_label.setText(f"Attempts remaining: {self.attempts_remaining}/5")
            
            if self.attempts_remaining <= 0:
                self._show_status("❌ Too many failed attempts. Try again in 1 minute.", False)
                self._disable_inputs(60)
            else:
                self._show_status("❌ Face not recognized. Try again.", False)
            
            self._stop_camera()
    
    def _stop_camera(self) -> None:
        """Stop camera thread"""
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread.wait()
            self.camera_thread = None
        
        self.scan_button.setText("Scan Face")
        self.scan_button.setEnabled(True)
        self.camera_label.clear()
        self.camera_label.setText("Camera preview will appear here")
    
    def _check_task_manager(self) -> None:
        """Check if Task Manager is running and kill it"""
        try:
            # Use tasklist to check for Taskmgr.exe
            import subprocess
            
            # Check if process exists
            output = subprocess.check_output('tasklist /FI "IMAGENAME eq Taskmgr.exe"', shell=True)
            if b"Taskmgr.exe" in output:
                # Kill it
                subprocess.call('taskkill /F /IM Taskmgr.exe', shell=True)
                self._show_status("⚠️ Task Manager is blocked!", False)
        except Exception:
            pass

    def _show_loading(self, show: bool) -> None:
        """Show or hide loading indicator
        
        Args:
            show: Whether to show the loading indicator
        """
        if show:
            self.loading_label.setVisible(True)
            self.spinner_index = 0
            self.loading_spinner_timer.start(300)  # Update spinner every 300ms
        else:
            self.loading_label.setVisible(False)
            self.loading_spinner_timer.stop()
    
    def _update_spinner(self) -> None:
        """Update spinner animation"""
        spinner_frames = ["⟳", "↻", "⟲"]
        self.spinner_index = (self.spinner_index + 1) % len(spinner_frames)
        frame = spinner_frames[self.spinner_index]
        self.loading_label.setText(f"{frame} Verifying...")
        # Also update face loading label if visible
        if self.face_loading_label.isVisible():
            self.face_loading_label.setText(f"{frame} Analyzing face...")
    
    def _unlock(self) -> None:
        """Unlock screen"""
        self._show_loading(False)  # Stop loading animation
        self._stop_camera()
        if self.keyboard_blocker:
            self.keyboard_blocker.stop()
        self.tm_timer.stop()
        if hasattr(self, 'time_timer'):
            self.time_timer.stop()
        self.unlocked.emit()
        self.close()
    
    def _show_status(self, message: str, success: bool) -> None:
        """Show status message"""
        color = "#00ff00" if success else "#ff0000"
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def _on_tab_changed(self, index) -> None:
        """Handle tab switching"""
        # Stop camera if switching away from Face Verification
        # Assuming Face Verification is the second tab (index 1) or checking tab text
        current_tab_text = self.auth_tabs.tabText(index)
        
        if "Face Verification" not in current_tab_text:
            self._stop_camera()
            
        # If switching to TOTP, focus first input
        if "Authenticator Code" in current_tab_text and self.otp_inputs:
            self.otp_inputs[0].setFocus()

    def _disable_inputs(self, seconds: int) -> None:
        """Disable inputs for specified seconds"""
        for box in self.otp_inputs:
            box.setEnabled(False)
        self.unlock_button.setEnabled(False)
        self.scan_button.setEnabled(False)
        
        # Re-enable after timeout
        QTimer.singleShot(seconds * 1000, self._enable_inputs)
    
    def _enable_inputs(self) -> None:
        """Re-enable inputs"""
        for box in self.otp_inputs:
            box.setEnabled(True)
        self.unlock_button.setEnabled(True)
        self.scan_button.setEnabled(True)
        self.attempts_remaining = 5
        self.attempts_label.setText(f"Attempts remaining: {self.attempts_remaining}/5")
    
    def _shake_totp_inputs(self) -> None:
        """Shake animation for invalid TOTP code"""
        if not hasattr(self, 'totp_frame') or self.totp_frame is None:
            return
        
        # Create shake animation sequence
        original_pos = self.totp_frame.pos()
        shake_distance = 10
        shake_duration = 50
        
        animation_group = QSequentialAnimationGroup(self)
        
        # Shake left
        anim1 = QPropertyAnimation(self.totp_frame, b"pos")
        anim1.setDuration(shake_duration)
        anim1.setStartValue(original_pos)
        anim1.setEndValue(QPoint(original_pos.x() - shake_distance, original_pos.y()))
        animation_group.addAnimation(anim1)
        
        # Shake right
        anim2 = QPropertyAnimation(self.totp_frame, b"pos")
        anim2.setDuration(shake_duration)
        anim2.setStartValue(QPoint(original_pos.x() - shake_distance, original_pos.y()))
        anim2.setEndValue(QPoint(original_pos.x() + shake_distance, original_pos.y()))
        animation_group.addAnimation(anim2)
        
        # Shake left again
        anim3 = QPropertyAnimation(self.totp_frame, b"pos")
        anim3.setDuration(shake_duration)
        anim3.setStartValue(QPoint(original_pos.x() + shake_distance, original_pos.y()))
        anim3.setEndValue(QPoint(original_pos.x() - shake_distance, original_pos.y()))
        animation_group.addAnimation(anim3)
        
        # Return to center
        anim4 = QPropertyAnimation(self.totp_frame, b"pos")
        anim4.setDuration(shake_duration)
        anim4.setStartValue(QPoint(original_pos.x() - shake_distance, original_pos.y()))
        anim4.setEndValue(original_pos)
        animation_group.addAnimation(anim4)
        
        animation_group.start()
        self.shake_animation = animation_group  # Keep reference
    
    def _update_time(self) -> None:
        """Update current time display"""
        self.time_label.setText(datetime.now().strftime("%I:%M %p"))
        
        # Update break timer
        if self.break_remaining_seconds > 0:
            self.break_remaining_seconds -= 1
            self.break_timer_label.setText(self._format_break_time())
        else:
            # Check for auto-unlock
            if self.config.get('auto_unlock_after_break', False):
                self._unlock()
                return
                
            self.break_timer_label.setText("Break Complete - You may unlock now")
            self.break_timer_label.setStyleSheet("color: #00ff00;")

    def _format_break_time(self) -> str:
        """Format break time remaining"""
        minutes = self.break_remaining_seconds // 60
        seconds = self.break_remaining_seconds % 60
        return f"Break duration: {minutes}:{seconds:02d} remaining"
    
    def _load_authentication(self) -> None:
        """Load TOTP and face verification data"""
        self.totp.load_secret()
        if self.face_verifier:
            self.face_verifier.load_registered_faces()
    
    def keyPressEvent(self, event):
        """Block certain keyboard shortcuts"""
        # Block Alt+F4, Alt+Tab, Win+D, etc.
        if event.key() == Qt.Key.Key_F4 and event.modifiers() == Qt.KeyboardModifier.AltModifier:
            event.ignore()
            return
        
        # Block Escape key (no debug backdoor in production)
        if event.key() == Qt.Key.Key_Escape:
            event.ignore()
            return
        
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle close event"""
        self._stop_camera()
        if self.keyboard_blocker:
            self.keyboard_blocker.stop()
        if hasattr(self, 'tm_timer'):
            self.tm_timer.stop()
        super().closeEvent(event)

class OverlayScreen(QWidget):
    """Simple overlay for secondary monitors"""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setStyleSheet("background-color: #000000;")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        from pathlib import Path
        assets_dir = Path(__file__).parent.parent / 'assets'
        logo_path = assets_dir / 'logo.png'
        
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            layout.addWidget(logo_label)
        
        label = QLabel("Please complete authentication on the main screen")
        label.setStyleSheet("color: white; font-size: 24px; font-family: 'Segoe UI';")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

