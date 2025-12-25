"""
Setup Wizard GUI (PyQt6)
6-step wizard for first-time configuration
"""
from __future__ import annotations

from PyQt6.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QLineEdit, QSpinBox, QCheckBox,
                             QComboBox, QFrame, QProgressBar, QTextEdit, QApplication,
                             QGraphicsDropShadowEffect, QGridLayout)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QPixmap, QImage, QKeyEvent, QKeySequence, QColor
from PyQt6.QtMultimedia import QMediaDevices
import cv2
import numpy as np

from config_manager import ConfigManager
from totp_auth import TOTPAuth
from face_verification import FaceVerification
from tinxy_api import TinxyAPI
from windows_startup import WindowsStartup
from theme.theme import load_stylesheet

class CameraThread(QThread):
    """Thread for camera capture during face registration"""
    frame_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, camera_index=0):
        super().__init__()
        self.running = False
        self.camera = None
        self.camera_index = camera_index
    
    def run(self):
        try:
            # Initialize COM for DirectShow in this thread
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except ImportError:
                pass

            # Small delay to ensure resources are ready
            self.msleep(100)

            # Use CAP_DSHOW for Windows compatibility
            print(f"Opening camera {self.camera_index}...")
            self.camera = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            
            if not self.camera.isOpened():
                print(f"Failed to open camera {self.camera_index}")
                self.error_occurred.emit(f"Could not open camera {self.camera_index}")
                return

            # Try to set buffer size to 1 to reduce lag/buffering issues
            try:
                self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            except:
                pass

            print(f"Camera {self.camera_index} opened successfully")
            self.running = True
            
            while self.running:
                try:
                    ret, frame = self.camera.read()
                    if ret and frame is not None and frame.size > 0:
                        self.frame_ready.emit(frame)
                    else:
                        print("Failed to read frame or empty frame")
                        self.msleep(100) # Wait a bit before retrying
                except Exception as e:
                    print(f"Frame read error: {e}")
                    
                self.msleep(33)
        except Exception as e:
            print(f"Camera thread error: {e}")
            self.error_occurred.emit(str(e))
        finally:
            print("Releasing camera...")
            if self.camera:
                self.camera.release()
            
            # Uninitialize COM
            try:
                import pythoncom
                pythoncom.CoUninitialize()
            except ImportError:
                pass
    
    def stop(self):
        self.running = False
        # Camera release happens in run() finally block

class WelcomePage(QWizardPage):
    """Welcome screen - Step 1/6"""
    
    def __init__(self):
        super().__init__()
        # Clear default header to implement custom design
        self.setTitle("")
        self.setSubTitle("")
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(10)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Logo
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        from pathlib import Path
        assets_dir = Path(__file__).parent.parent / 'assets'
        logo_path = assets_dir / 'logo.png'
        
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            
            # Add subtle soft shadow/glow
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 40))
            shadow.setOffset(0, 4)
            logo_label.setGraphicsEffect(shadow)
            
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("🛡️")
            title_font = QFont("Segoe UI", 80)
            logo_label.setFont(title_font)
            
        layout.addWidget(logo_label)
        layout.addSpacing(20)
        
        # Header
        title = QLabel("Welcome to BreakGuard")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 26, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #2c3e50;") 
        layout.addWidget(title)
        
        subtitle = QLabel("Your personal health guardian")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = QFont("Segoe UI", 13)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #7f8c8d;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        # Description
        desc = QLabel("BreakGuard helps you build healthy work habits by enforcing regular breaks.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        desc_font = QFont("Segoe UI", 11)
        desc.setFont(desc_font)
        desc.setStyleSheet("color: #34495e;")
        layout.addWidget(desc)
        
        layout.addSpacing(30)
        
        # Features Section
        features_frame = QFrame()
        features_layout = QGridLayout(features_frame)
        features_layout.setVerticalSpacing(15)
        features_layout.setHorizontalSpacing(15)
        features_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        features = [
            ("⏱️", "Smart work intervals"),
            ("🔐", "Two-factor protection"),
            ("👤", "Optional face verification"),
            ("🔌", "IoT device control"),
            ("🚀", "Auto-start with Windows")
        ]
        
        for row, (icon, text) in enumerate(features):
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Segoe UI", 12))
            icon_label.setStyleSheet("color: #555;")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            text_label = QLabel(text)
            text_label.setFont(QFont("Segoe UI", 11))
            text_label.setStyleSheet("color: #333;")
            text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            
            features_layout.addWidget(icon_label, row, 0)
            features_layout.addWidget(text_label, row, 1)
            
        layout.addWidget(features_frame)
        
        layout.addStretch()
        
        # Footer
        footer = QLabel("This setup wizard will guide you through the initial configuration.")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #95a5a6; font-size: 11px;")
        layout.addWidget(footer)
        
        self.setLayout(layout)

class WorkIntervalsPage(QWizardPage):
    """Work intervals configuration - Step 2/6"""
    
    def __init__(self):
        super().__init__()
        # Clear default header for custom design
        self.setTitle("")
        self.setSubTitle("")
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 20, 40, 20)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Configure Work Intervals")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        subtitle = QLabel("Set how often you want to take breaks")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #7f8c8d;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)
        
        # Settings Card
        settings_card = QFrame()
        settings_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
            QLabel {
                border: none;
            }
        """)
        card_layout = QVBoxLayout(settings_card)
        card_layout.setSpacing(20)
        card_layout.setContentsMargins(25, 25, 25, 25)
        
        # Work Interval Section
        work_section = QVBoxLayout()
        work_section.setSpacing(5)
        
        work_label = QLabel("Work interval")
        work_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        work_label.setStyleSheet("color: #34495e;")
        work_section.addWidget(work_label)
        
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 240)
        self.work_spin.setValue(60)
        self.work_spin.setSuffix(" minutes")
        self.work_spin.setFixedHeight(35)
        self.work_spin.setFont(QFont("Segoe UI", 11))
        # Styling for spinbox
        self.work_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                background-color: #f8f9fa;
            }
            QSpinBox:focus {
                border: 1px solid #3498db;
                background-color: #ffffff;
            }
        """)
        work_section.addWidget(self.work_spin)
        
        work_helper = QLabel("After this time, BreakGuard will lock your screen.")
        work_helper.setFont(QFont("Segoe UI", 9))
        work_helper.setStyleSheet("color: #95a5a6;")
        work_section.addWidget(work_helper)
        
        card_layout.addLayout(work_section)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #ecf0f1; border: none; max-height: 1px;")
        card_layout.addWidget(line)
        
        # Warning Section
        warning_section = QVBoxLayout()
        warning_section.setSpacing(5)
        
        warning_label = QLabel("Warning before lock")
        warning_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        warning_label.setStyleSheet("color: #34495e;")
        warning_section.addWidget(warning_label)
        
        self.warning_spin = QSpinBox()
        self.warning_spin.setRange(1, 30)
        self.warning_spin.setValue(5)
        self.warning_spin.setSuffix(" minutes")
        self.warning_spin.setFixedHeight(35)
        self.warning_spin.setFont(QFont("Segoe UI", 11))
        self.warning_spin.setStyleSheet(self.work_spin.styleSheet())
        warning_section.addWidget(self.warning_spin)
        
        warning_helper = QLabel("You'll receive a reminder before the lock activates.")
        warning_helper.setFont(QFont("Segoe UI", 9))
        warning_helper.setStyleSheet("color: #95a5a6;")
        warning_section.addWidget(warning_helper)
        
        card_layout.addLayout(warning_section)
        
        layout.addWidget(settings_card)
        
        # Recommendations Card
        rec_card = QFrame()
        rec_card.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """)
        rec_layout = QVBoxLayout(rec_card)
        rec_layout.setSpacing(10)
        rec_layout.setContentsMargins(20, 15, 20, 15)
        
        rec_header = QLabel("💡 Recommended Settings")
        rec_header.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        rec_header.setStyleSheet("color: #2c3e50; border: none;")
        rec_layout.addWidget(rec_header)
        
        # Preset Buttons
        presets = [
            ("60 minutes - Balanced work & eye care", 60),
            ("90 minutes - Extended focus sessions", 90),
            ("30 minutes - Frequent breaks for eye health", 30)
        ]
        
        for text, val in presets:
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    border: none;
                    background: transparent;
                    color: #34495e;
                    padding: 5px;
                    font-family: "Segoe UI";
                    font-size: 13px;
                }
                QPushButton:hover {
                    color: #2980b9;
                    background-color: #ecf0f1;
                    border-radius: 4px;
                }
            """)
            # Use lambda with default arg to capture value correctly
            btn.clicked.connect(lambda checked, v=val: self.apply_preset(v))
            rec_layout.addWidget(btn)
            
        layout.addWidget(rec_card)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Register fields
        self.registerField("work_interval", self.work_spin)
        self.registerField("warning_time", self.warning_spin)
        
        # Connect validation
        self.work_spin.valueChanged.connect(self.validate_inputs)
        self.warning_spin.valueChanged.connect(self.validate_inputs)

    def apply_preset(self, minutes):
        self.work_spin.setValue(minutes)
        # Adjust warning time intelligently if needed
        if minutes <= 30:
            self.warning_spin.setValue(3)
        else:
            self.warning_spin.setValue(5)
            
    def validate_inputs(self):
        # Ensure warning time is less than work interval
        if self.warning_spin.value() >= self.work_spin.value():
            self.warning_spin.setValue(max(1, self.work_spin.value() - 1))

    def initializePage(self):
        """Initialize page - set tab order"""
        self.setTabOrder(self.work_spin, self.warning_spin)

class GoogleAuthPage(QWizardPage):
    """Google Authenticator setup - Step 3/6"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Set up Google Authenticator")
        self.setSubTitle("Secure your breaks with two-factor authentication")
        
        self.totp = TOTPAuth()
        self.secret = None
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # Enable checkbox (standard PyQt6 style)
        self.enable_check = QCheckBox("Enable Google Authenticator")
        self.enable_check.setChecked(True)
        self.enable_check.stateChanged.connect(self._on_toggle_enabled)
        self.enable_check.setToolTip("Enable two-factor authentication for unlocking")
        self.enable_check.setAccessibleName("Enable Google Authenticator checkbox")
        self.enable_check.setAccessibleDescription("When enabled, you will need to enter a code from Google Authenticator to unlock")
        layout.addWidget(self.enable_check)
        
        # Main Content Area (Two Columns)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        
        # Left Column: QR Code
        qr_frame = QFrame()
        qr_layout = QVBoxLayout(qr_frame)
        qr_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_layout.setSpacing(0) # Reset spacing, control manually
        
        qr_layout.addStretch()
        
        # QR Box Container (The visible border)
        qr_box = QFrame()
        qr_box.setFixedSize(220, 220)
        qr_box.setProperty("class", "qr-box")
        qr_box_layout = QVBoxLayout(qr_box)
        qr_box_layout.setContentsMargins(0,0,0,0)
        qr_box_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.qr_label = QLabel("Click 'Generate QR Code' to start")
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setFixedSize(200, 200)
        self.qr_label.setAccessibleName("QR Code image")
        
        qr_box_layout.addWidget(self.qr_label)
        qr_layout.addWidget(qr_box)
        
        qr_layout.addStretch()
        
        content_layout.addWidget(qr_frame, 1) # Stretch factor 1
        
        # Right Column: Instructions
        inst_frame = QFrame()
        inst_layout = QVBoxLayout(inst_frame)
        inst_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        inst_layout.setSpacing(15)
        
        # Generate button (moved to right column top)
        self.generate_btn = QPushButton("Generate QR Code")
        self.generate_btn.clicked.connect(self._generate_qr)
        self.generate_btn.setToolTip("Click to generate a new QR code for setup")
        inst_layout.addWidget(self.generate_btn)
        
        self.inst_list = QFrame()
        self.inst_list.setVisible(False) # Hidden initially
        list_layout = QVBoxLayout(self.inst_list)
        list_layout.setSpacing(10)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        self.step_labels = []
        steps = [
            "1. Open Google Authenticator on your phone",
            "2. Tap the '+' button",
            "3. Scan the QR code",
            "4. Enter the 6-digit code below"
        ]
        
        for step in steps:
            lbl = QLabel(step)
            lbl.setWordWrap(True)
            list_layout.addWidget(lbl)
            self.step_labels.append(lbl)
            
        inst_layout.addWidget(self.inst_list)
        inst_layout.addStretch()
        
        content_layout.addWidget(inst_frame, 1) # Stretch factor 1
        
        layout.addLayout(content_layout)
        layout.addSpacing(30)
        
        # Verification Section (Bottom)
        verify_frame = QFrame()
        verify_frame.setProperty("class", "card")
        verify_layout = QVBoxLayout(verify_frame)
        verify_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        verify_title = QLabel("Verify setup")
        verify_title.setProperty("class", "h2")
        verify_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        verify_layout.addWidget(verify_title)
        
        verify_subtitle = QLabel("Enter the 6-digit code from your app")
        verify_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        verify_subtitle.setProperty("class", "text-secondary")
        verify_layout.addWidget(verify_subtitle)
        
        verify_layout.addSpacing(15)
        
        # OTP input boxes
        otp_layout = QHBoxLayout()
        otp_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.otp_inputs = []
        for i in range(6):
            input_box = QLineEdit()
            input_box.setMaxLength(1)
            input_box.setFixedSize(50, 50) # Larger inputs
            input_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
            input_box.setProperty("class", "otp-input")
            input_box.setAccessibleName(f"OTP digit {i+1}")
            input_box.textChanged.connect(lambda text, idx=i: self._on_digit_entered(text, idx))
            input_box.installEventFilter(self)
            self.otp_inputs.append(input_box)
            otp_layout.addWidget(input_box)
        
        verify_layout.addLayout(otp_layout)
        
        verify_layout.addSpacing(20)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.verify_btn = QPushButton("Verify & Continue")
        self.verify_btn.setMinimumWidth(200)
        self.verify_btn.clicked.connect(self._verify_code)
        btn_layout.addWidget(self.verify_btn)
        
        verify_layout.addLayout(btn_layout)
        
        # Status and Helper Text
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        verify_layout.addWidget(self.status_label)
        
        helper_text = QLabel("Code refreshes every 30 seconds")
        helper_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        helper_text.setProperty("class", "text-small text-secondary")
        verify_layout.addWidget(helper_text)
        
        layout.addWidget(verify_frame)
        
        self.setLayout(layout)
        self.registerField("totp_enabled", self.enable_check)
        
    def initializePage(self):
        """Initialize page - set tab order"""
        self.setTabOrder(self.enable_check, self.generate_btn)
        if self.otp_inputs:
            self.setTabOrder(self.generate_btn, self.otp_inputs[0])
            for i in range(len(self.otp_inputs) - 1):
                self.setTabOrder(self.otp_inputs[i], self.otp_inputs[i+1])
            self.setTabOrder(self.otp_inputs[-1], self.verify_btn)

    def _on_toggle_enabled(self, state):
        """Handle enable checkbox toggle"""
        enabled = bool(state)
        self.generate_btn.setEnabled(enabled)
        self.verify_btn.setEnabled(enabled)
        for inp in self.otp_inputs:
            inp.setEnabled(enabled)
    
    def _generate_qr(self):
        """Generate QR code"""
        self.secret = self.totp.generate_secret()
        qr_img = self.totp.generate_qr_code(self.secret)
        
        # Convert PIL image to QPixmap
        qr_img = qr_img.resize((200, 200)) # Larger size
        qr_img_rgb = qr_img.convert('RGB')
        
        import numpy as np
        img_array = np.array(qr_img_rgb)
        h, w, ch = img_array.shape
        bytes_per_line = ch * w
        qt_image = QImage(img_array.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        
        self.qr_label.setText("")  # Remove placeholder text to prevent overlap
        self.qr_label.setPixmap(pixmap)
        
        # Show UI elements
        self.inst_list.setVisible(True)
        
        # Update step 3 with secret key
        self.step_labels[2].setText(f"3. Scan the QR code Or use setup key: <span style='font-family: Consolas; font-weight: bold;'>{self.secret}</span>")
        self.step_labels[2].setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        self.generate_btn.setText("Regenerate QR Code")
        
        # Focus first input
        if self.otp_inputs:
            self.otp_inputs[0].setFocus()
    
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
                    return True
        
        return super().eventFilter(obj, event)
    
    def _on_digit_entered(self, text, index):
        """Move to next box on digit entry"""
        if text and index < 5:
            self.otp_inputs[index + 1].setFocus()
        elif text and index == 5:
            # Auto-verify or focus button?
            self.verify_btn.setFocus()
    
    def _verify_code(self):
        """Verify OTP code"""
        if not self.secret:
            self.status_label.setText("Generate QR code first")
            self.status_label.setStyleSheet("color: red;")
            return
        
        code = ''.join(box.text() for box in self.otp_inputs)
        
        if len(code) != 6:
            self.status_label.setText("Please enter all 6 digits")
            self.status_label.setStyleSheet("color: orange;")
            return
        
        if self.totp.verify_code(code, self.secret):
            self.status_label.setText("Code verified successfully!")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.totp.save_secret(self.secret)
        else:
            self.status_label.setText("Invalid code. Try again.")
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
        self.capture_timer = None
        self.photos_taken = 0
        self.target_photos = 10
        self.current_frame = None
        self.is_capturing = False
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Controls Container
        controls_layout = QHBoxLayout()
        
        # Enable checkbox (standard PyQt6 style)
        self.enable_check = QCheckBox("Enable face verification")
        self.enable_check.setChecked(True)
        self.enable_check.stateChanged.connect(self._on_toggle_enabled)
        self.enable_check.setToolTip("Enable facial recognition for unlocking")
        self.enable_check.setAccessibleName("Enable face verification checkbox")
        self.enable_check.setAccessibleDescription("When enabled, your camera will be used to verify your face before unlocking")
        controls_layout.addWidget(self.enable_check)
        
        controls_layout.addStretch()
        
        # Camera Selector
        cam_label = QLabel("Camera:")
        self.cam_combo = QComboBox()
        self.cam_combo.setFixedWidth(200)  # Wider for names
        self._populate_cameras()
        self.cam_combo.currentIndexChanged.connect(self._restart_camera)
        controls_layout.addWidget(cam_label)
        controls_layout.addWidget(self.cam_combo)
        
        layout.addLayout(controls_layout)
        
        layout.addSpacing(10)
        
        # Camera Preview
        self.preview_container = QLabel()
        self.preview_container.setFixedSize(480, 270)
        self.preview_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_container.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                border-radius: 12px;
                border: 1px solid #3d3d3d;
            }
        """)
        self.preview_container.setText("Camera preview")
        layout.addWidget(self.preview_container, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.target_photos)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedSize(480, 6)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #3d3d3d;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #0d7377;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Status & Progress Section
        status_layout = QVBoxLayout()
        status_layout.setSpacing(5)
        
        # Status Text
        self.status_label = QLabel("Ready to start")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #e0e0e0;")
        status_layout.addWidget(self.status_label)
        
        # Progress Text
        self.progress_text = QLabel("")
        self.progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_text.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        status_layout.addWidget(self.progress_text)
        
        layout.addLayout(status_layout)
        
        layout.addSpacing(10)
        
        # Primary Action Button
        self.capture_btn = QPushButton("Start Capture")
        self.capture_btn.setMinimumWidth(200)
        self.capture_btn.setFixedHeight(40)
        self.capture_btn.clicked.connect(self._toggle_capture)
        self.capture_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                color: white;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #14a19f;
            }
            QPushButton:disabled {
                background-color: #555;
            }
        """)
        layout.addWidget(self.capture_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Privacy Message
        privacy_label = QLabel("Your photos are stored locally and never leave your device.")
        privacy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        privacy_label.setStyleSheet("color: #888888; font-size: 11px; margin-top: 10px;")
        layout.addWidget(privacy_label)
        
        layout.addStretch()
        self.setLayout(layout)
        
        self.registerField("face_enabled", self.enable_check)
        self.registerField("camera_index", self.cam_combo)
        
    def _populate_cameras(self):
        """Populate camera list using pygrabber (Windows) or QtMultimedia"""
        self.cam_combo.clear()
        
        # Try pygrabber first on Windows for better DirectShow support
        import platform
        if platform.system() == 'Windows':
            try:
                from pygrabber.dshow_graph import FilterGraph
                graph = FilterGraph()
                devices = graph.get_input_devices()
                # Explicitly release the graph to free COM resources
                del graph
                import gc
                gc.collect()
                
                if devices:
                    for i, device_name in enumerate(devices):
                        self.cam_combo.addItem(device_name, i)
                    return
            except ImportError:
                pass
        
        # Fallback to QtMultimedia
        cameras = QMediaDevices.videoInputs()
        
        if cameras:
            for i, camera in enumerate(cameras):
                # Use description (name) and store index as user data
                self.cam_combo.addItem(camera.description(), i)
        else:
            # Fallback
            self.cam_combo.addItems([f"Camera {i}" for i in range(3)])

    def initializePage(self):
        """Initialize page"""
        self.setTabOrder(self.enable_check, self.cam_combo)
        self.setTabOrder(self.cam_combo, self.capture_btn)
        self._start_camera_preview()

    def cleanupPage(self):
        """Cleanup when leaving page"""
        self._stop_camera()

    def _on_toggle_enabled(self, state):
        """Handle enable checkbox toggle"""
        enabled = bool(state)
        self.cam_combo.setEnabled(enabled)
        self.capture_btn.setEnabled(enabled)
        if enabled:
            self._start_camera_preview()
        else:
            self._stop_camera()
            
    def _restart_camera(self):
        """Restart camera when selection changes"""
        if self.camera_thread:
            self._stop_camera()
            self._start_camera_preview()

    def _start_camera_preview(self):
        """Start camera preview thread"""
        if not self.camera_thread and self.enable_check.isChecked():
            # Get index from user data, default to current index if None
            camera_idx = self.cam_combo.currentData()
            if camera_idx is None:
                camera_idx = self.cam_combo.currentIndex()
                
            self.camera_thread = CameraThread(camera_idx)
            self.camera_thread.frame_ready.connect(self._on_camera_frame)
            self.camera_thread.error_occurred.connect(self._on_camera_error)
            self.camera_thread.start()

    def _on_camera_error(self, error_msg):
        """Handle camera errors"""
        self.status_label.setText(f"Camera Error: {error_msg}")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.preview_container.setText("Camera Error")

    def _stop_camera(self):
        """Stop camera and cleanup"""
        self._stop_capture_process()
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread.wait()
            self.camera_thread = None
        self.preview_container.clear()
        self.preview_container.setText("Camera preview")

    def _toggle_capture(self):
        """Toggle capture state"""
        if self.is_capturing:
            self._stop_capture_process()
        else:
            self._start_capture_process()

    def _start_capture_process(self):
        """Start the capture process"""
        self.is_capturing = True
        self.photos_taken = 0
        self.progress_bar.setValue(0)
        self.capture_btn.setText("Stop Capture")
        self.capture_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        
        # Disable navigation
        if self.wizard():
            self.wizard().button(QWizard.WizardButton.NextButton).setEnabled(False)
            self.wizard().button(QWizard.WizardButton.BackButton).setEnabled(False)
        
        self.cam_combo.setEnabled(False)
        
        # Start timer
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self._auto_capture)
        self.capture_timer.start(1000)

    def _stop_capture_process(self):
        """Stop the capture process"""
        self.is_capturing = False
        if self.capture_timer:
            self.capture_timer.stop()
            self.capture_timer = None
        
        self.capture_btn.setText("Start Capture")
        # Restore button style
        self.capture_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                color: white;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #14a19f;
            }
        """)
        
        # Re-enable navigation
        if self.wizard():
            self.wizard().button(QWizard.WizardButton.NextButton).setEnabled(True)
            self.wizard().button(QWizard.WizardButton.BackButton).setEnabled(True)
        
        self.cam_combo.setEnabled(True)
        self.status_label.setText("Capture stopped")

    def _on_camera_frame(self, frame):
        """Update camera preview"""
        if frame is None or frame.size == 0:
            return
            
        try:
            self.current_frame = frame
            
            # Detect face for feedback
            # Note: This runs in UI thread, might need optimization if slow
            face_loc = self.face_verifier.detect_face(frame)
            
            # Create a copy for display to draw the rectangle
            display_frame = frame.copy()
            
            if face_loc:
                x, y, w, h = face_loc
                # Draw green rectangle around face
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                if not self.is_capturing:
                    self.status_label.setText("Face detected - Ready to capture")
                    self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0d7377;")
            else:
                if not self.is_capturing:
                    self.status_label.setText("Position your face in the frame")
                    self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #e0e0e0;")
            
            # Display frame
            # Ensure frame is contiguous and in correct format
            if not display_frame.flags['C_CONTIGUOUS']:
                display_frame = np.ascontiguousarray(display_frame)
                
            rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            
            # Scale to fit container while keeping aspect ratio
            scaled = pixmap.scaled(
                self.preview_container.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_container.setPixmap(scaled)
        except Exception as e:
            print(f"Error processing frame: {e}")

    def _auto_capture(self):
        """Auto-capture face"""
        if self.current_frame is not None and self.photos_taken < self.target_photos:
            # Check if face is present before capturing
            if self.face_verifier.detect_face(self.current_frame):
                if self.face_verifier.register_face(self.current_frame):
                    self.photos_taken += 1
                    self.progress_bar.setValue(self.photos_taken)
                    self.progress_text.setText(f"Capturing photos: {self.photos_taken} of {self.target_photos}")
                    self.status_label.setText("Capturing...")
                    self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0d7377;")
                    
                    if self.photos_taken >= self.target_photos:
                        self._complete_capture()
            else:
                self.status_label.setText("Face not found - Look at camera")
                self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: orange;")

    def _complete_capture(self):
        """Complete face capture"""
        self._stop_capture_process()
        self.face_verifier.save_registered_faces()
        self.status_label.setText("Face verification setup complete!")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: green;")
        self.capture_btn.setText("Retake Photos")
        self.progress_text.setText("All photos captured successfully")

class TinxyPage(QWizardPage):
    """Tinxy IoT integration - Step 5/6"""
    
    def __init__(self):
        super().__init__()
        # Clear default header
        self.setTitle("")
        self.setSubTitle("")
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 20, 40, 20)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Tinxy Device Integration")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        subtitle = QLabel("Control IoT devices during breaks (optional)")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #7f8c8d;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)
        
        # Enable checkbox (standard PyQt6 style)
        self.enable_check = QCheckBox("Enable Tinxy integration")
        self.enable_check.setFont(QFont("Segoe UI", 11))
        self.enable_check.setToolTip("Control IoT devices during breaks (optional)")
        self.enable_check.setAccessibleName("Enable Tinxy integration checkbox")
        self.enable_check.setAccessibleDescription("When enabled, you can control Tinxy IoT devices like turning off monitors during breaks")
        self.enable_check.stateChanged.connect(self._on_toggle_enabled)
        layout.addWidget(self.enable_check)
        
        # Configuration Card
        self.config_card = QFrame()
        self.config_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
            QLabel {
                border: none;
                color: #34495e;
            }
            QLineEdit, QSpinBox {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 8px;
                background-color: #f8f9fa;
                font-family: "Segoe UI";
                font-size: 13px;
            }
            QLineEdit:focus, QSpinBox:focus {
                border: 1px solid #3498db;
                background-color: #ffffff;
            }
            QLineEdit:disabled, QSpinBox:disabled {
                background-color: #f0f0f0;
                color: #95a5a6;
            }
        """)
        card_layout = QVBoxLayout(self.config_card)
        card_layout.setSpacing(15)
        card_layout.setContentsMargins(25, 25, 25, 25)
        
        card_title = QLabel("Connect your Tinxy device")
        card_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        card_layout.addWidget(card_title)
        
        # API Key
        api_layout = QVBoxLayout()
        api_layout.setSpacing(5)
        api_label = QLabel("API Key")
        api_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("Paste your Tinxy API key")
        self.api_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_input.textChanged.connect(self._check_fields)
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_input)
        card_layout.addLayout(api_layout)
        
        # Device ID & Number Row (Grid for perfect alignment)
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(15)
        grid_layout.setVerticalSpacing(5)
        
        # Labels
        dev_label = QLabel("Device ID")
        dev_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        grid_layout.addWidget(dev_label, 0, 0)
        
        num_label = QLabel("Device #")
        num_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        grid_layout.addWidget(num_label, 0, 1)
        
        # Inputs
        self.device_input = QLineEdit()
        self.device_input.setPlaceholderText("e.g. device_123456")
        self.device_input.setFixedHeight(38) # Fixed height for consistency
        self.device_input.textChanged.connect(self._check_fields)
        grid_layout.addWidget(self.device_input, 1, 0)
        
        self.device_num_spin = QSpinBox()
        self.device_num_spin.setRange(1, 4)
        self.device_num_spin.setValue(1)
        self.device_num_spin.setFixedHeight(38) # Fixed height for consistency
        grid_layout.addWidget(self.device_num_spin, 1, 1)
        
        # Column stretch
        grid_layout.setColumnStretch(0, 2)
        grid_layout.setColumnStretch(1, 1)
        
        card_layout.addLayout(grid_layout)
        
        helper = QLabel("Used when your device has multiple switches")
        helper.setFont(QFont("Segoe UI", 9))
        helper.setStyleSheet("color: #95a5a6;")
        card_layout.addWidget(helper)
        
        card_layout.addSpacing(10)
        
        # Test Connection Row
        test_layout = QHBoxLayout()
        
        self.test_btn = QPushButton("Test connection")
        self.test_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.test_btn.setFixedWidth(140)
        self.test_btn.clicked.connect(self._test_connection)
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14a19f;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        test_layout.addWidget(self.test_btn)
        
        self.status_label = QLabel("Not connected")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setStyleSheet("color: #95a5a6; margin-left: 10px;")
        test_layout.addWidget(self.status_label)
        test_layout.addStretch()
        
        card_layout.addLayout(test_layout)
        
        layout.addWidget(self.config_card)
        
        # Info Card
        info_card = QFrame()
        info_card.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """)
        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(20, 15, 20, 15)
        
        info_title = QLabel("What is Tinxy?")
        info_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        info_title.setStyleSheet("color: #2c3e50; border: none;")
        info_layout.addWidget(info_title)
        
        info_text = QLabel("Tinxy allows BreakGuard to control smart switches during breaks - for example, turning off your monitor automatically.")
        info_text.setWordWrap(True)
        info_text.setFont(QFont("Segoe UI", 10))
        info_text.setStyleSheet("color: #7f8c8d; border: none;")
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_card)
        layout.addStretch()
        
        self.setLayout(layout)
        
        self.registerField("tinxy_enabled", self.enable_check)
        self.registerField("tinxy_api_key", self.api_input)
        self.registerField("tinxy_device_id", self.device_input)
        self.registerField("tinxy_device_number", self.device_num_spin)
        
        # Initialize state
        self._on_toggle_enabled(False)
        self._check_fields()
    
    def _on_toggle_enabled(self, state):
        """Handle enable checkbox toggle"""
        enabled = bool(state)
        self.config_card.setEnabled(enabled)
        
        # Visual feedback for disabled state
        if enabled:
            self.config_card.setStyleSheet(self.config_card.styleSheet().replace("opacity: 0.6;", ""))
        else:
            # Add opacity to look disabled
            self.config_card.setStyleSheet(self.config_card.styleSheet() + "QFrame { opacity: 0.6; }")
            
        self._check_fields()
    
    def _check_fields(self):
        """Enable test button only if fields are filled and enabled"""
        if not self.enable_check.isChecked():
            self.test_btn.setEnabled(False)
            return
            
        has_api = bool(self.api_input.text().strip())
        has_device = bool(self.device_input.text().strip())
        self.test_btn.setEnabled(has_api and has_device)
    
    def _test_connection(self):
        """Test Tinxy connection"""
        api_key = self.api_input.text().strip()
        device_id = self.device_input.text().strip()
        
        self.status_label.setText("Connecting...")
        self.status_label.setStyleSheet("color: #f39c12; margin-left: 10px;")
        self.test_btn.setEnabled(False)
        QApplication.processEvents()
        
        tinxy = TinxyAPI(api_key, device_id)
        if tinxy.test_connection():
            self.status_label.setText("Connected successfully")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold; margin-left: 10px;")
        else:
            self.status_label.setText("Connection failed")
            self.status_label.setStyleSheet("color: #c0392b; margin-left: 10px;")
        
        self.test_btn.setEnabled(True)

class CompletePage(QWizardPage):
    """Setup complete - Step 6/6"""
    
    def __init__(self):
        super().__init__()
        # Clear default header
        self.setTitle("")
        self.setSubTitle("")
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        icon_label = QLabel("COMPLETE")
        icon_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("color: #27ae60;")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        icon_label.setGraphicsEffect(shadow)
        layout.addWidget(icon_label)
        
        # Title
        title = QLabel("Setup complete")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("BreakGuard is ready to protect your health and productivity.")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #7f8c8d;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(10)
        
        # Summary Card
        self.summary_card = QFrame()
        self.summary_card.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
            QLabel {
                border: none;
                font-family: "Segoe UI";
                font-size: 13px;
            }
        """)
        self.summary_layout = QVBoxLayout(self.summary_card)
        self.summary_layout.setSpacing(10)
        self.summary_layout.setContentsMargins(25, 20, 25, 20)
        
        # Header for summary
        summary_header = QLabel("Your settings")
        summary_header.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        summary_header.setStyleSheet("color: #95a5a6; text-transform: uppercase; letter-spacing: 1px;")
        self.summary_layout.addWidget(summary_header)
        self.summary_layout.addSpacing(5)
        
        # Placeholder for rows (will be added in initializePage)
        self.rows_layout = QVBoxLayout()
        self.rows_layout.setSpacing(8)
        self.summary_layout.addLayout(self.rows_layout)
        
        layout.addWidget(self.summary_card)
        
        layout.addSpacing(20)
        
        # Footer Info
        footer = QLabel("BreakGuard will now run in the system tray.\nYou can adjust settings anytime by right-clicking the tray icon.")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #95a5a6; font-size: 11px;")
        layout.addWidget(footer)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def initializePage(self):
        """Populate summary when page is shown"""
        # Clear previous items
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        wizard = self.wizard()
        
        # Get values
        work_interval = wizard.field("work_interval")
        warning_time = wizard.field("warning_time")
        totp_enabled = wizard.field("totp_enabled")
        face_enabled = wizard.field("face_enabled")
        tinxy_enabled = wizard.field("tinxy_enabled")
        
        # Add rows
        self._add_row("⏱️", "Work interval", f"{work_interval} minutes")
        self._add_row("⏰", "Warning before lock", f"{warning_time} minutes")
        self._add_row("🔐", "Authentication", "Google Authenticator" if totp_enabled else "Disabled")
        self._add_row("👤", "Face verification", "Enabled" if face_enabled else "Disabled")
        self._add_row("🔌", "Tinxy integration", "Enabled" if tinxy_enabled else "Disabled")

    def _add_row(self, icon, label, value):
        row = QHBoxLayout()
        
        icon_lbl = QLabel(icon)
        icon_lbl.setFixedWidth(25)
        icon_lbl.setStyleSheet("font-size: 14px;")
        
        label_lbl = QLabel(label + ":")
        label_lbl.setStyleSheet("color: #7f8c8d; font-weight: 500;")
        
        val_lbl = QLabel(str(value))
        val_lbl.setStyleSheet("color: #2c3e50; font-weight: bold;")
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        row.addWidget(icon_lbl)
        row.addWidget(label_lbl)
        row.addStretch()
        row.addWidget(val_lbl)
        
        container = QFrame()
        container.setLayout(row)
        container.setStyleSheet("background: transparent; border: none;")
        row.setContentsMargins(0, 0, 0, 0)
        
        self.rows_layout.addWidget(container)

class SetupWizard(QWizard):
    """Main setup wizard"""
    
    setup_completed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("BreakGuard Setup Wizard")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setMinimumSize(800, 700)
        # Theme is loaded at app level in main.py
        
        # Add pages
        self.addPage(WelcomePage())
        self.addPage(WorkIntervalsPage())
        self.addPage(GoogleAuthPage())
        face_page = FaceVerificationPage()
        self.face_verification_page_id = self.addPage(face_page)
        self.addPage(TinxyPage())
        self.addPage(CompletePage())
        
        # Customize buttons
        self.setButtonText(QWizard.WizardButton.NextButton, "Next →")
        self.setButtonText(QWizard.WizardButton.BackButton, "← Back")
        self.setButtonText(QWizard.WizardButton.FinishButton, "Finish")
        
        # Track page changes to manage camera lifecycle
        self.currentIdChanged.connect(self._on_page_changed)
        self.face_verification_page_id = None
        
        # Connect finish
        self.finished.connect(self._on_finish)
    
    def _on_page_changed(self, page_id):
        """Handle page changes - stop camera when leaving face verification page"""
        # If we're leaving the face verification page, ensure camera is stopped
        if hasattr(self, 'face_verification_page_id') and self.face_verification_page_id is not None:
            # Get the face verification page
            face_page = self.page(self.face_verification_page_id)
            if face_page and page_id != self.face_verification_page_id:
                # We've left the face verification page, ensure camera is stopped
                if hasattr(face_page, '_stop_camera'):
                    face_page._stop_camera()
    
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
    
    def closeEvent(self, event):
        """Ensure camera is stopped when wizard closes"""
        if hasattr(self, 'face_verification_page_id') and self.face_verification_page_id is not None:
            face_page = self.page(self.face_verification_page_id)
            if face_page and hasattr(face_page, '_stop_camera'):
                face_page._stop_camera()
        super().closeEvent(event)
