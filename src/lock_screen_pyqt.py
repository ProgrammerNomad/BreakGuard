"""
Lock Screen GUI (PyQt6)
Fullscreen lock interface with TOTP and face verification
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QFrame, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QImage, QPixmap
import cv2
from datetime import datetime

from config_manager import ConfigManager
from totp_auth import TOTPAuth
from face_verification import FaceVerification

class CameraThread(QThread):
    """Thread for camera capture"""
    frame_ready = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.camera = None
    
    def run(self):
        """Run camera capture loop"""
        self.camera = cv2.VideoCapture(0)
        self.running = True
        
        while self.running:
            ret, frame = self.camera.read()
            if ret:
                self.frame_ready.emit(frame)
            self.msleep(33)  # ~30 FPS
    
    def stop(self):
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
        self.face_verifier = FaceVerification()
        
        self.attempts_remaining = 5
        self.camera_thread = None
        self.current_frame = None
        
        self._setup_ui()
        self._load_authentication()
        
        # Block keyboard shortcuts
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    
    def _setup_ui(self):
        """Setup lock screen UI"""
        # Make fullscreen and always on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        # Set dark background
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14a19f;
            }
            QPushButton:pressed {
                background-color: #0a5456;
            }
            QLineEdit {
                background-color: #2d2d2d;
                border: 2px solid #3d3d3d;
                border-radius: 5px;
                padding: 10px;
                font-size: 24px;
                color: white;
                text-align: center;
            }
            QLineEdit:focus {
                border-color: #0d7377;
            }
            QFrame {
                background-color: #2d2d2d;
                border-radius: 10px;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)
        
        # Title
        title = QLabel("⏸ BREAK TIME")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 48, QFont.Weight.Bold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Time to take a break and rest your eyes")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont("Segoe UI", 16)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #a0a0a0;")
        layout.addWidget(subtitle)
        
        # Current time
        self.time_label = QLabel(datetime.now().strftime("%I:%M %p"))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_font = QFont("Segoe UI", 24)
        self.time_label.setFont(time_font)
        self.time_label.setStyleSheet("color: #a0a0a0;")
        layout.addWidget(self.time_label)
        
        # Update time every second
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self._update_time)
        self.time_timer.start(1000)
        
        layout.addSpacing(30)
        
        # TOTP Input Section
        if self.config.is_totp_enabled():
            totp_frame = self._create_totp_section()
            layout.addWidget(totp_frame)
        
        layout.addWidget(QLabel("OR"))
        
        # Face Verification Section
        if self.config.is_face_verification_enabled():
            face_frame = self._create_face_section()
            layout.addWidget(face_frame)
        
        # Status message
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_font = QFont("Segoe UI", 14)
        self.status_label.setFont(status_font)
        layout.addWidget(self.status_label)
        
        # Attempts remaining
        self.attempts_label = QLabel(f"Attempts remaining: {self.attempts_remaining}/5")
        self.attempts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.attempts_label.setStyleSheet("color: #ffa500;")
        layout.addWidget(self.attempts_label)
    
    def _create_totp_section(self) -> QFrame:
        """Create TOTP input section"""
        frame = QFrame()
        frame.setMaximumWidth(600)
        
        layout = QVBoxLayout(frame)
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
            input_box.setFixedSize(60, 70)
            input_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
            input_box.textChanged.connect(lambda text, idx=i: self._on_digit_entered(text, idx))
            self.otp_inputs.append(input_box)
            input_layout.addWidget(input_box)
        
        layout.addLayout(input_layout)
        
        # Unlock button
        self.unlock_button = QPushButton("Unlock")
        self.unlock_button.clicked.connect(self._verify_totp)
        layout.addWidget(self.unlock_button)
        
        # Info
        info = QLabel("💡 Code changes every 30 seconds")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(info)
        
        return frame
    
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
        self.camera_label.setFixedSize(400, 300)
        self.camera_label.setStyleSheet("border: 2px solid #3d3d3d;")
        layout.addWidget(self.camera_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Scan button
        self.scan_button = QPushButton("Scan Face")
        self.scan_button.clicked.connect(self._start_face_scan)
        layout.addWidget(self.scan_button)
        
        return frame
    
    def _on_digit_entered(self, text: str, index: int):
        """Handle digit entry in OTP boxes"""
        if text and index < 5:
            # Move to next box
            self.otp_inputs[index + 1].setFocus()
        
        # Auto-submit when all 6 digits entered
        if all(box.text() for box in self.otp_inputs):
            self._verify_totp()
    
    def _verify_totp(self):
        """Verify TOTP code"""
        # Get code from input boxes
        code = ''.join(box.text() for box in self.otp_inputs)
        
        if len(code) != 6:
            self._show_status("Please enter all 6 digits", False)
            return
        
        # Verify
        if self.totp.verify_code(code):
            self._show_status("✅ Code verified!", True)
            self._unlock()
        else:
            self.attempts_remaining -= 1
            self.attempts_label.setText(f"Attempts remaining: {self.attempts_remaining}/5")
            
            if self.attempts_remaining <= 0:
                self._show_status("❌ Too many failed attempts. Try again in 1 minute.", False)
                self._disable_inputs(60)
            else:
                self._show_status("❌ Invalid code. Try again.", False)
            
            # Clear inputs
            for box in self.otp_inputs:
                box.clear()
            self.otp_inputs[0].setFocus()
    
    def _start_face_scan(self):
        """Start camera for face scanning"""
        if not self.camera_thread:
            self.camera_thread = CameraThread()
            self.camera_thread.frame_ready.connect(self._on_camera_frame)
            self.camera_thread.start()
            
            self.scan_button.setText("Verifying...")
            self.scan_button.setEnabled(False)
            
            # Auto-verify after 3 seconds
            QTimer.singleShot(3000, self._verify_face)
    
    def _on_camera_frame(self, frame):
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
        if self.current_frame is None:
            self._show_status("❌ No camera frame available", False)
            self._stop_camera()
            return
        
        if self.face_verifier.verify_face(self.current_frame):
            self._show_status("✅ Face verified!", True)
            self._stop_camera()
            self._unlock()
        else:
            self.attempts_remaining -= 1
            self.attempts_label.setText(f"Attempts remaining: {self.attempts_remaining}/5")
            
            if self.attempts_remaining <= 0:
                self._show_status("❌ Too many failed attempts. Try again in 1 minute.", False)
                self._disable_inputs(60)
            else:
                self._show_status("❌ Face not recognized. Try again.", False)
            
            self._stop_camera()
    
    def _stop_camera(self):
        """Stop camera thread"""
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread.wait()
            self.camera_thread = None
        
        self.scan_button.setText("Scan Face")
        self.scan_button.setEnabled(True)
        self.camera_label.clear()
        self.camera_label.setText("Camera preview will appear here")
    
    def _unlock(self):
        """Unlock screen"""
        self._stop_camera()
        self.unlocked.emit()
        self.close()
    
    def _show_status(self, message: str, success: bool):
        """Show status message"""
        color = "#00ff00" if success else "#ff0000"
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def _disable_inputs(self, seconds: int):
        """Disable inputs for specified seconds"""
        for box in self.otp_inputs:
            box.setEnabled(False)
        self.unlock_button.setEnabled(False)
        self.scan_button.setEnabled(False)
        
        # Re-enable after timeout
        QTimer.singleShot(seconds * 1000, self._enable_inputs)
    
    def _enable_inputs(self):
        """Re-enable inputs"""
        for box in self.otp_inputs:
            box.setEnabled(True)
        self.unlock_button.setEnabled(True)
        self.scan_button.setEnabled(True)
        self.attempts_remaining = 5
        self.attempts_label.setText(f"Attempts remaining: {self.attempts_remaining}/5")
    
    def _update_time(self):
        """Update current time display"""
        self.time_label.setText(datetime.now().strftime("%I:%M %p"))
    
    def _load_authentication(self):
        """Load TOTP and face verification data"""
        self.totp.load_secret()
        self.face_verifier.load_registered_faces()
    
    def keyPressEvent(self, event):
        """Block certain keyboard shortcuts"""
        # Block Alt+F4, Alt+Tab, Win+D, etc.
        if event.key() == Qt.Key.Key_F4 and event.modifiers() == Qt.KeyboardModifier.AltModifier:
            event.ignore()
            return
        
        # Allow Escape only in debug mode
        if event.key() == Qt.Key.Key_Escape:
            # Uncomment for testing:
            # self._unlock()
            event.ignore()
            return
        
        super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """Handle close event"""
        self._stop_camera()
        super().closeEvent(event)
