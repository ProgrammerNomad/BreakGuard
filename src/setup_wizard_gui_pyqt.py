"""
Setup Wizard GUI (PyQt6)
6-step wizard for first-time configuration
"""

from PyQt6.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QSpinBox, QCheckBox,
                             QComboBox, QFrame, QProgressBar, QTextEdit, QApplication)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QPixmap, QImage
import cv2

from config_manager import ConfigManager
from totp_auth import TOTPAuth
from face_verification import FaceVerification
from tinxy_api import TinxyAPI
from windows_startup import WindowsStartup

class CameraThread(QThread):
    """Thread for camera capture during face registration"""
    frame_ready = pyqtSignal(object)
    
    def __init__(self, camera_index=0):
        super().__init__()
        self.running = False
        self.camera = None
        self.camera_index = camera_index
    
    def run(self):
        # Use CAP_DSHOW for Windows compatibility
        self.camera = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        self.running = True
        
        while self.running:
            ret, frame = self.camera.read()
            if ret:
                self.frame_ready.emit(frame)
            self.msleep(33)
    
    def stop(self):
        self.running = False
        if self.camera:
            self.camera.release()

class WelcomePage(QWizardPage):
    """Welcome screen - Step 1/6"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to BreakGuard")
        self.setSubTitle("Your personal health guardian")
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Icon/Logo
        title = QLabel("🛡️")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 72)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Welcome message
        welcome = QLabel("Welcome to BreakGuard")
        welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        welcome.setFont(welcome_font)
        layout.addWidget(welcome)
        
        subtitle = QLabel("Your personal break reminder assistant")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #666666; font-size: 14px;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Features
        features_label = QLabel("Features:")
        features_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(features_label)
        
        features = [
            "⏰ Smart work interval tracking",
            "🔒 Secure two-factor authentication",
            "👤 Optional face verification",
            "🔌 IoT device integration",
            "🚀 Auto-start with Windows"
        ]
        
        for feature in features:
            label = QLabel(feature)
            label.setStyleSheet("font-size: 13px; margin-left: 20px;")
            layout.addWidget(label)
        
        layout.addSpacing(20)
        
        info = QLabel("This wizard will guide you through setup.\nYou can change settings later from the system tray.")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(info)
        
        layout.addStretch()
        self.setLayout(layout)

class WorkIntervalsPage(QWizardPage):
    """Work intervals configuration - Step 2/6"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Configure Work Intervals")
        self.setSubTitle("Set how often you want to take breaks")
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Work interval
        work_layout = QHBoxLayout()
        work_label = QLabel("Work interval (minutes):")
        work_label.setMinimumWidth(200)
        self.work_spin = QSpinBox()
        self.work_spin.setRange(15, 240)
        self.work_spin.setValue(60)
        self.work_spin.setSuffix(" minutes")
        work_layout.addWidget(work_label)
        work_layout.addWidget(self.work_spin)
        work_layout.addStretch()
        layout.addLayout(work_layout)
        
        # Warning time
        warning_layout = QHBoxLayout()
        warning_label = QLabel("Warning before lock:")
        warning_label.setMinimumWidth(200)
        self.warning_spin = QSpinBox()
        self.warning_spin.setRange(1, 30)
        self.warning_spin.setValue(5)
        self.warning_spin.setSuffix(" minutes")
        warning_layout.addWidget(warning_label)
        warning_layout.addWidget(self.warning_spin)
        warning_layout.addStretch()
        layout.addLayout(warning_layout)
        
        layout.addSpacing(20)
        
        # Recommendations
        rec_frame = QFrame()
        rec_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f8ff;
                border: 1px solid #b0d0f0;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        rec_layout = QVBoxLayout(rec_frame)
        
        rec_title = QLabel("💡 Recommended Settings")
        rec_title.setStyleSheet("font-weight: bold; color: #0066cc;")
        rec_layout.addWidget(rec_title)
        
        recommendations = [
            "• 60 minutes: Standard (20-20-20 rule)",
            "• 90 minutes: Extended focus sessions",
            "• 30 minutes: Frequent breaks for eye health"
        ]
        
        for rec in recommendations:
            label = QLabel(rec)
            label.setStyleSheet("color: #333333; font-size: 12px;")
            rec_layout.addWidget(label)
        
        layout.addWidget(rec_frame)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Register fields
        self.registerField("work_interval", self.work_spin)
        self.registerField("warning_time", self.warning_spin)

class GoogleAuthPage(QWizardPage):
    """Google Authenticator setup - Step 3/6"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Setup Google Authenticator")
        self.setSubTitle("Secure your breaks with two-factor authentication")
        
        self.totp = TOTPAuth()
        self.secret = None
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Enable checkbox
        self.enable_check = QCheckBox("Enable Google Authenticator")
        self.enable_check.setChecked(True)
        self.enable_check.stateChanged.connect(self._on_toggle_enabled)
        layout.addWidget(self.enable_check)
        
        # Generate button
        self.generate_btn = QPushButton("Generate QR Code")
        self.generate_btn.clicked.connect(self._generate_qr)
        layout.addWidget(self.generate_btn)
        
        # QR Code and Instructions layout
        content_layout = QHBoxLayout()
        
        # QR Code
        self.qr_label = QLabel("Click 'Generate QR Code' to start")
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setFixedSize(250, 250)
        self.qr_label.setStyleSheet("border: 2px solid #cccccc; background-color: white;")
        content_layout.addWidget(self.qr_label)
        
        # Instructions
        inst_frame = QFrame()
        inst_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #dddddd;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        inst_layout = QVBoxLayout(inst_frame)
        inst_layout.setSpacing(5)
        
        inst_title = QLabel("✓ QR Code Generated!")
        inst_title.setMinimumHeight(25)
        inst_title.setStyleSheet("font-weight: bold; color: #00aa00; font-size: 14px;")
        inst_layout.addWidget(inst_title)
        
        inst_layout.addSpacing(10)
        
        instructions = [
            "Scan with Google Authenticator:",
            "1. Open app on phone",
            "2. Tap '+' button",
            "3. Scan QR code",
            "4. Enter code below"
        ]
        
        for inst in instructions:
            label = QLabel(inst)
            label.setStyleSheet("font-size: 12px;")
            inst_layout.addWidget(label)
        
        inst_layout.addSpacing(10)
        
        self.secret_label = QLabel("Secret: (generate first)")
        self.secret_label.setWordWrap(True)
        self.secret_label.setStyleSheet("font-family: monospace; font-size: 11px; color: #666;")
        inst_layout.addWidget(self.secret_label)
        
        inst_layout.addStretch()
        content_layout.addWidget(inst_frame)
        
        layout.addLayout(content_layout)
        
        layout.addSpacing(10)
        
        # Verification
        verify_frame = QFrame()
        verify_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #dddddd;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        verify_layout = QVBoxLayout(verify_frame)
        
        verify_title = QLabel("🔓 Verify Your Setup")
        verify_title.setStyleSheet("font-weight: bold;")
        verify_layout.addWidget(verify_title)
        
        verify_subtitle = QLabel("Enter 6-digit code:")
        verify_layout.addWidget(verify_subtitle)
        
        # OTP input boxes
        otp_layout = QHBoxLayout()
        self.otp_inputs = []
        for i in range(6):
            input_box = QLineEdit()
            input_box.setMaxLength(1)
            input_box.setFixedSize(40, 40)
            input_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
            input_box.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #cccccc;
                    border-radius: 5px;
                    font-size: 20px;
                    font-weight: bold;
                }
                QLineEdit:focus {
                    border-color: #0066cc;
                }
            """)
            input_box.textChanged.connect(lambda text, idx=i: self._on_digit_entered(text, idx))
            self.otp_inputs.append(input_box)
            otp_layout.addWidget(input_box)
        
        verify_layout.addLayout(otp_layout)
        
        verify_layout.addSpacing(15)
        
        self.verify_btn = QPushButton("Verify Code")
        self.verify_btn.clicked.connect(self._verify_code)
        verify_layout.addWidget(self.verify_btn)
        
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        verify_layout.addWidget(self.status_label)
        
        info = QLabel("💡 Code changes every 30 seconds")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #888888; font-size: 11px;")
        verify_layout.addWidget(info)
        
        layout.addWidget(verify_frame)
        layout.addStretch()
        
        self.setLayout(layout)
        self.registerField("totp_enabled", self.enable_check)
    
    def _on_toggle_enabled(self, state):
        """Handle enable checkbox toggle"""
        enabled = bool(state)
        self.generate_btn.setEnabled(enabled)
        self.verify_btn.setEnabled(enabled)
    
    def _generate_qr(self):
        """Generate QR code"""
        self.secret = self.totp.generate_secret()
        qr_img = self.totp.generate_qr_code(self.secret)
        
        # Convert PIL image to QPixmap
        qr_img = qr_img.resize((220, 220))
        qr_img_rgb = qr_img.convert('RGB')
        
        import numpy as np
        img_array = np.array(qr_img_rgb)
        h, w, ch = img_array.shape
        bytes_per_line = ch * w
        qt_image = QImage(img_array.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        self.qr_label.setPixmap(pixmap)
        self.secret_label.setText(f"Secret: {self.secret}")
        
        self.generate_btn.setText("Regenerate QR Code")
    
    def _on_digit_entered(self, text, index):
        """Move to next box on digit entry"""
        if text and index < 5:
            self.otp_inputs[index + 1].setFocus()
    
    def _verify_code(self):
        """Verify OTP code"""
        if not self.secret:
            self.status_label.setText("❌ Generate QR code first")
            self.status_label.setStyleSheet("color: red;")
            return
        
        code = ''.join(box.text() for box in self.otp_inputs)
        
        if len(code) != 6:
            self.status_label.setText("Please enter all 6 digits")
            self.status_label.setStyleSheet("color: orange;")
            return
        
        if self.totp.verify_code(code, self.secret):
            self.status_label.setText("✅ Code verified successfully!")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            # Save secret
            self.totp.save_secret(self.secret)
        else:
            self.status_label.setText("❌ Invalid code. Try again.")
            self.status_label.setStyleSheet("color: red;")
            for box in self.otp_inputs:
                box.clear()
            self.otp_inputs[0].setFocus()

class FaceVerificationPage(QWizardPage):
    """Face verification setup - Step 4/6"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Face Verification Setup")
        self.setSubTitle("Add an extra layer of security (optional)")
        
        self.face_verifier = FaceVerification()
        self.camera_thread = None
        self.photos_taken = 0
        self.target_photos = 10
        self.current_frame = None
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Enable checkbox
        self.enable_check = QCheckBox("Enable Face Verification")
        self.enable_check.setChecked(True)
        self.enable_check.stateChanged.connect(self._on_toggle_enabled)
        layout.addWidget(self.enable_check)
        
        # Camera Selection
        cam_layout = QHBoxLayout()
        cam_label = QLabel("Select Camera:")
        self.cam_combo = QComboBox()
        self.cam_combo.addItems([f"Camera {i}" for i in range(5)])
        cam_layout.addWidget(cam_label)
        cam_layout.addWidget(self.cam_combo)
        cam_layout.addStretch()
        layout.addLayout(cam_layout)
        
        # Camera preview
        self.camera_label = QLabel("Camera preview will appear here")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setFixedSize(640, 480)
        self.camera_label.setStyleSheet("border: 2px solid #cccccc; background-color: #f0f0f0;")
        layout.addWidget(self.camera_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Status
        self.status_label = QLabel("Status: Ready to capture")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Progress
        self.progress_label = QLabel(f"Photos taken: {self.photos_taken}/{self.target_photos}")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_label)
        
        # Instructions
        inst_label = QLabel("Instructions:\n• Look directly at camera\n• Keep face centered\n• Photos will be taken automatically")
        inst_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inst_label.setStyleSheet("color: #666666; font-size: 12px;")
        layout.addWidget(inst_label)
        
        # Capture button
        self.capture_btn = QPushButton("Start Capture")
        self.capture_btn.clicked.connect(self._start_capture)
        layout.addWidget(self.capture_btn)
        
        layout.addStretch()
        self.setLayout(layout)
        
        self.registerField("face_enabled", self.enable_check)
        self.registerField("camera_index", self.cam_combo)
    
    def _on_toggle_enabled(self, state):
        """Handle enable checkbox toggle"""
        self.capture_btn.setEnabled(bool(state))
    
    def _start_capture(self):
        """Start camera capture"""
        if not self.camera_thread:
            camera_idx = self.cam_combo.currentIndex()
            self.camera_thread = CameraThread(camera_idx)
            self.camera_thread.frame_ready.connect(self._on_camera_frame)
            self.camera_thread.start()
            
            self.capture_btn.setText("Stop Capture")
            self.cam_combo.setEnabled(False)  # Disable selection while capturing
            self.status_label.setText("Status: Capturing...")
            
            # Start auto-capture timer
            self.capture_timer = QTimer()
            self.capture_timer.timeout.connect(self._auto_capture)
            self.capture_timer.start(1000)  # Capture every second
        else:
            self._stop_capture()
    
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
        
        scaled = pixmap.scaled(
            self.camera_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.camera_label.setPixmap(scaled)
    
    def _auto_capture(self):
        """Auto-capture face"""
        if self.current_frame is not None and self.photos_taken < self.target_photos:
            if self.face_verifier.register_face(self.current_frame):
                self.photos_taken += 1
                self.progress_label.setText(f"Photos taken: {self.photos_taken}/{self.target_photos}")
                
                if self.photos_taken >= self.target_photos:
                    self._complete_capture()
    
    def _complete_capture(self):
        """Complete face capture"""
        self._stop_capture()
        self.face_verifier.save_registered_faces()
        self.status_label.setText("Status: ✅ Face registration complete!")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
    
    def _stop_capture(self):
        """Stop camera capture"""
        if self.capture_timer:
            self.capture_timer.stop()
        
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread.wait()
            self.camera_thread = None
        
        self.capture_btn.setText("Start Capture")
        self.cam_combo.setEnabled(True)  # Re-enable selection
        self.camera_label.clear()
        self.camera_label.setText("Camera preview will appear here")
    
    def cleanupPage(self):
        """Cleanup when leaving page"""
        self._stop_capture()

class TinxyPage(QWizardPage):
    """Tinxy IoT integration - Step 5/6"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Tinxy Device Integration")
        self.setSubTitle("Control IoT devices during breaks (Optional)")
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Enable checkbox
        self.enable_check = QCheckBox("Enable Tinxy Integration")
        self.enable_check.setChecked(False)
        self.enable_check.stateChanged.connect(self._on_toggle_enabled)
        layout.addWidget(self.enable_check)
        
        # Config frame
        config_frame = QFrame()
        config_frame.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #dddddd;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        config_layout = QVBoxLayout(config_frame)
        
        config_title = QLabel("API Configuration")
        config_title.setStyleSheet("font-weight: bold;")
        config_layout.addWidget(config_title)
        
        # API Key
        api_layout = QHBoxLayout()
        api_label = QLabel("API Key:")
        api_label.setMinimumWidth(120)
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("Enter Tinxy API key")
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_input)
        config_layout.addLayout(api_layout)
        
        # Device ID
        device_layout = QHBoxLayout()
        device_label = QLabel("Device ID:")
        device_label.setMinimumWidth(120)
        self.device_input = QLineEdit()
        self.device_input.setPlaceholderText("Enter device ID")
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_input)
        config_layout.addLayout(device_layout)
        
        # Device Number
        num_layout = QHBoxLayout()
        num_label = QLabel("Device Number:")
        num_label.setMinimumWidth(120)
        self.device_num_spin = QSpinBox()
        self.device_num_spin.setRange(1, 4)
        self.device_num_spin.setValue(1)
        num_layout.addWidget(num_label)
        num_layout.addWidget(self.device_num_spin)
        num_layout.addStretch()
        config_layout.addLayout(num_layout)
        
        # Test button
        self.test_btn = QPushButton("Test Connection")
        self.test_btn.clicked.connect(self._test_connection)
        config_layout.addWidget(self.test_btn)
        
        # Status
        self.status_label = QLabel("Status: Not connected")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        config_layout.addWidget(self.status_label)
        
        layout.addWidget(config_frame)
        
        # Info
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #e8f4f8;
                border: 1px solid #b0d8e8;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_title = QLabel("ℹ️ What is Tinxy?")
        info_title.setStyleSheet("font-weight: bold; color: #0066cc;")
        info_layout.addWidget(info_title)
        
        info_text = QLabel("Control smart switches/devices during breaks.\nCan turn off monitor automatically.")
        info_text.setStyleSheet("color: #333333; font-size: 12px;")
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_frame)
        
        layout.addStretch()
        self.setLayout(layout)
        
        self.registerField("tinxy_enabled", self.enable_check)
        self.registerField("tinxy_api_key", self.api_input)
        self.registerField("tinxy_device_id", self.device_input)
        self.registerField("tinxy_device_number", self.device_num_spin)
        
        self._on_toggle_enabled(False)
    
    def _on_toggle_enabled(self, state):
        """Handle enable checkbox toggle"""
        enabled = bool(state)
        self.api_input.setEnabled(enabled)
        self.device_input.setEnabled(enabled)
        self.device_num_spin.setEnabled(enabled)
        self.test_btn.setEnabled(enabled)
    
    def _test_connection(self):
        """Test Tinxy connection"""
        api_key = self.api_input.text().strip()
        device_id = self.device_input.text().strip()
        
        if not api_key or not device_id:
            self.status_label.setText("Status: ❌ Please enter API key and device ID")
            self.status_label.setStyleSheet("color: red;")
            return
        
        self.status_label.setText("Status: Testing...")
        self.status_label.setStyleSheet("color: orange;")
        QApplication.processEvents()
        
        tinxy = TinxyAPI(api_key, device_id)
        if tinxy.test_connection():
            self.status_label.setText("Status: ✅ Connected successfully!")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.status_label.setText("Status: ❌ Connection failed")
            self.status_label.setStyleSheet("color: red;")

class CompletePage(QWizardPage):
    """Setup complete - Step 6/6"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Setup Complete!")
        self.setSubTitle("BreakGuard is ready to protect your health")
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Success icon
        success = QLabel("✅")
        success.setAlignment(Qt.AlignmentFlag.AlignCenter)
        success_font = QFont("Segoe UI", 72)
        success.setFont(success_font)
        layout.addWidget(success)
        
        title = QLabel("Setup Complete!")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        subtitle = QLabel("BreakGuard is ready to protect your health\nand productivity!")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #666666; font-size: 14px;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Summary
        self.summary_label = QLabel()
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.summary_label.setStyleSheet("""
            QLabel {
                background-color: #f9f9f9;
                border: 1px solid #dddddd;
                border-radius: 5px;
                padding: 15px;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.summary_label)
        
        layout.addSpacing(10)
        
        info = QLabel("The app will start in the system tray.\nRight-click the icon to access settings.")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("color: #888888; font-size: 12px;")
        layout.addWidget(info)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def initializePage(self):
        """Called when page is shown"""
        # Build summary from wizard fields
        wizard = self.wizard()
        
        work_interval = wizard.field("work_interval")
        warning_time = wizard.field("warning_time")
        totp_enabled = wizard.field("totp_enabled")
        face_enabled = wizard.field("face_enabled")
        tinxy_enabled = wizard.field("tinxy_enabled")
        
        summary = f"""Configuration Summary:

⏰ Work interval: {work_interval} minutes
⚠️ Warning time: {warning_time} minutes
🔐 Authentication: {"Google Authenticator" if totp_enabled else "Disabled"}
👤 Face verification: {"Enabled" if face_enabled else "Disabled"}
🔌 Tinxy IoT: {"Enabled" if tinxy_enabled else "Disabled"}"""
        
        self.summary_label.setText(summary)

class SetupWizard(QWizard):
    """Main setup wizard"""
    
    setup_completed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("BreakGuard Setup Wizard")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setFixedSize(800, 700)
        
        # Add pages
        self.addPage(WelcomePage())
        self.addPage(WorkIntervalsPage())
        self.addPage(GoogleAuthPage())
        self.addPage(FaceVerificationPage())
        self.addPage(TinxyPage())
        self.addPage(CompletePage())
        
        # Customize buttons
        self.setButtonText(QWizard.WizardButton.NextButton, "Next →")
        self.setButtonText(QWizard.WizardButton.BackButton, "← Back")
        self.setButtonText(QWizard.WizardButton.FinishButton, "Finish")
        
        # Connect finish
        self.finished.connect(self._on_finish)
    
    def _on_finish(self, result):
        """Handle wizard completion"""
        if result == QWizard.DialogCode.Accepted:
            # Save configuration
            config = ConfigManager()
            
            config.set('work_interval_minutes', self.field("work_interval"))
            config.set('warning_before_minutes', self.field("warning_time"))
            config.set('totp_enabled', self.field("totp_enabled"))
            config.set('face_verification_enabled', self.field("face_enabled"))
            config.set('camera_index', self.field("camera_index"))
            config.set('tinxy_enabled', self.field("tinxy_enabled"))
            config.set('tinxy_api_key', self.field("tinxy_api_key"))
            config.set('tinxy_device_id', self.field("tinxy_device_id"))
            config.set('tinxy_device_number', self.field("tinxy_device_number"))
            
            config.mark_setup_complete()
            
            # Setup Windows startup
            startup = WindowsStartup()
            if config.get('auto_start_windows', True):
                startup.add_to_startup()
            
            self.setup_completed.emit()
