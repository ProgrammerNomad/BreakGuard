"""
Modern Setup Wizard GUI for BreakGuard using PyQt6
Professional, user-friendly interface with Material Design inspiration
"""
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                              QCheckBox, QSpinBox, QProgressBar, QFrame,
                              QStackedWidget, QMessageBox, QScrollArea)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QImage, QFont, QPalette, QColor
from PIL import Image
import io
import sys


class SetupWizard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BreakGuard Setup Wizard")
        self.setMinimumSize(900, 650)
        self.resize(950, 680)
        
        # Setup data
        self.config_data = {
            'work_interval_minutes': 60,
            'warning_before_minutes': 5,
            'auth_enabled': True,
            'face_verification': True,
            'auto_start': True,
            'totp_secret': '',
            'tinxy_api_key': '',
            'tinxy_device_id': '',
            'tinxy_device_number': 1
        }
        
        self.current_step = 0
        self.totp_auth = None
        self.face_verif = None
        self.totp_verified = False
        self.qr_pixmap = None
        
        # Apply modern stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QLabel {
                color: #2f3542;
            }
            QPushButton {
                background-color: #0984e3;
                color: white;
                border: none;
                padding: 12px 30px;
                font-size: 11pt;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #0770c9;
            }
            QPushButton:pressed {
                background-color: #065ea8;
            }
            QPushButton:disabled {
                background-color: #dfe6e9;
                color: #b2bec3;
            }
            QLineEdit, QSpinBox {
                padding: 10px;
                border: 2px solid #dfe6e9;
                border-radius: 6px;
                font-size: 11pt;
                background-color: white;
            }
            QLineEdit:focus, QSpinBox:focus {
                border: 2px solid #0984e3;
            }
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #dfe6e9;
                height: 8px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00b894;
                border-radius: 4px;
            }
            QCheckBox {
                font-size: 11pt;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
        """)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(20)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(6)
        self.progress_bar.setValue(1)
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Stacked widget for steps
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 1)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 10, 0, 0)
        
        self.back_btn = QPushButton("← Back")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #2f3542;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
        """)
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setEnabled(False)
        nav_layout.addWidget(self.back_btn)
        
        nav_layout.addStretch()
        
        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self.go_next)
        nav_layout.addWidget(self.next_btn)
        
        main_layout.addLayout(nav_layout)
        
        # Create all steps
        self.create_all_steps()
        
    def create_all_steps(self):
        """Create all wizard steps"""
        self.stacked_widget.addWidget(self.create_welcome_step())
        self.stacked_widget.addWidget(self.create_interval_step())
        self.stacked_widget.addWidget(self.create_totp_step())
        self.stacked_widget.addWidget(self.create_face_step())
        self.stacked_widget.addWidget(self.create_tinxy_step())
        self.stacked_widget.addWidget(self.create_completion_step())
        
    def create_welcome_step(self):
        """Welcome screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        
        title = QLabel("🛡️ Welcome to BreakGuard")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Your personal break reminder and eye health assistant")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: #636e72;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(30)
        
        features = [
            "⏰ Smart work interval tracking",
            "🔒 Secure authentication with Google Authenticator",
            "👤 Optional face verification",
            "🔌 IoT device integration (Tinxy)",
            "🚀 Auto-start with Windows"
        ]
        
        for feature in features:
            label = QLabel(feature)
            label.setFont(QFont("Segoe UI", 11))
            label.setStyleSheet("padding: 8px;")
            layout.addWidget(label)
        
        layout.addSpacing(20)
        
        info = QLabel("This setup wizard will guide you through the initial configuration.\n"
                     "You can change these settings later from the system tray menu.")
        info.setFont(QFont("Segoe UI", 10))
        info.setStyleSheet("color: #636e72; padding: 15px; background-color: #e8f4f8; border-radius: 8px;")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        return widget
        
    def create_interval_step(self):
        """Work interval configuration"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(25)
        
        title = QLabel("⏱️ Configure Work Intervals")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        layout.addWidget(title)
        
        subtitle = QLabel("Set how often you want to take breaks")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #636e72;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Work interval
        work_layout = QHBoxLayout()
        work_label = QLabel("Work interval (minutes):")
        work_label.setFont(QFont("Segoe UI", 11))
        work_layout.addWidget(work_label)
        
        self.work_interval_spin = QSpinBox()
        self.work_interval_spin.setRange(15, 180)
        self.work_interval_spin.setValue(60)
        self.work_interval_spin.setSuffix(" min")
        work_layout.addWidget(self.work_interval_spin)
        work_layout.addStretch()
        
        layout.addLayout(work_layout)
        
        # Warning time
        warning_layout = QHBoxLayout()
        warning_label = QLabel("Warning before lock (minutes):")
        warning_label.setFont(QFont("Segoe UI", 11))
        warning_layout.addWidget(warning_label)
        
        self.warning_spin = QSpinBox()
        self.warning_spin.setRange(1, 30)
        self.warning_spin.setValue(5)
        self.warning_spin.setSuffix(" min")
        warning_layout.addWidget(self.warning_spin)
        warning_layout.addStretch()
        
        layout.addLayout(warning_layout)
        
        layout.addSpacing(20)
        
        # Recommendations
        rec_label = QLabel("💡 Recommended Settings")
        rec_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(rec_label)
        
        recommendations = [
            "• 60 minutes: Standard (follows 20-20-20 rule)",
            "• 90 minutes: Extended focus sessions",
            "• 30 minutes: Frequent breaks for eye health"
        ]
        
        for rec in recommendations:
            label = QLabel(rec)
            label.setFont(QFont("Segoe UI", 10))
            label.setStyleSheet("color: #636e72; padding: 4px 0;")
            layout.addWidget(label)
        
        layout.addStretch()
        
        return widget
        
    def create_totp_step(self):
        """Google Authenticator setup"""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setSpacing(20)
        
        title = QLabel("🔐 Setup Google Authenticator")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        main_layout.addWidget(title)
        
        subtitle = QLabel("Secure your breaks with two-factor authentication")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #636e72;")
        main_layout.addWidget(subtitle)
        
        # Enable checkbox
        self.totp_enabled = QCheckBox("Enable Google Authenticator")
        self.totp_enabled.setChecked(True)
        self.totp_enabled.setFont(QFont("Segoe UI", 11))
        self.totp_enabled.toggled.connect(self.toggle_totp_setup)
        main_layout.addWidget(self.totp_enabled)
        
        # TOTP setup container
        self.totp_container = QWidget()
        totp_layout = QVBoxLayout(self.totp_container)
        totp_layout.setContentsMargins(0, 0, 0, 0)
        
        # Generate button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.generate_qr_btn = QPushButton("Generate QR Code")
        self.generate_qr_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.generate_qr_btn.clicked.connect(self.generate_totp)
        btn_layout.addWidget(self.generate_qr_btn)
        btn_layout.addStretch()
        totp_layout.addLayout(btn_layout)
        
        totp_layout.addSpacing(15)
        
        # Horizontal layout for QR and verification
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        
        # Left: QR Code
        qr_frame = QFrame()
        qr_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dfe6e9;
                border-radius: 8px;
            }
        """)
        qr_frame.setFixedSize(360, 360)
        qr_layout = QVBoxLayout(qr_frame)
        qr_layout.setContentsMargins(15, 15, 15, 15)
        
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setFixedSize(330, 330)
        self.qr_label.setStyleSheet("background-color: white;")
        qr_layout.addWidget(self.qr_label)
        
        content_layout.addWidget(qr_frame)
        
        # Right: Instructions and verification
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.totp_instructions = QLabel("")
        self.totp_instructions.setFont(QFont("Segoe UI", 10))
        self.totp_instructions.setWordWrap(True)
        self.totp_instructions.setStyleSheet("color: #2f3542;")
        right_layout.addWidget(self.totp_instructions)
        
        right_layout.addSpacing(15)
        
        # Verification card
        self.verify_frame = QFrame()
        self.verify_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #dfe6e9;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        verify_layout = QVBoxLayout(self.verify_frame)
        
        verify_title = QLabel("🔓 Verify Your Setup")
        verify_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        verify_layout.addWidget(verify_title)
        
        verify_desc = QLabel("Enter the 6-digit code from Google Authenticator:")
        verify_desc.setFont(QFont("Segoe UI", 10))
        verify_desc.setStyleSheet("color: #636e72;")
        verify_layout.addWidget(verify_desc)
        
        verify_layout.addSpacing(10)
        
        self.verify_code_entry = QLineEdit()
        self.verify_code_entry.setMaxLength(6)
        self.verify_code_entry.setPlaceholderText("000000")
        self.verify_code_entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.verify_code_entry.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.verify_code_entry.setFixedHeight(50)
        verify_layout.addWidget(self.verify_code_entry)
        
        verify_layout.addSpacing(10)
        
        self.verify_btn = QPushButton("Verify Code")
        self.verify_btn.clicked.connect(self.verify_totp_code)
        verify_layout.addWidget(self.verify_btn)
        
        self.verify_status = QLabel("")
        self.verify_status.setFont(QFont("Segoe UI", 10))
        self.verify_status.setWordWrap(True)
        self.verify_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        verify_layout.addWidget(self.verify_status)
        
        hint = QLabel("💡 Code changes every 30 seconds")
        hint.setFont(QFont("Segoe UI", 9))
        hint.setStyleSheet("color: #95a5a6;")
        verify_layout.addWidget(hint)
        
        self.verify_frame.hide()
        right_layout.addWidget(self.verify_frame)
        right_layout.addStretch()
        
        content_layout.addWidget(right_widget, 1)
        totp_layout.addLayout(content_layout)
        
        main_layout.addWidget(self.totp_container)
        main_layout.addStretch()
        
        return widget
        
    def create_face_step(self):
        """Face verification setup"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        title = QLabel("👤 Face Verification Setup")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        layout.addWidget(title)
        
        subtitle = QLabel("Add an extra layer of security")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #636e72;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        info = QLabel("Face verification ensures that only you can unlock the computer during breaks.\n"
                     "We'll take a few photos to train the recognition model.")
        info.setFont(QFont("Segoe UI", 10))
        info.setWordWrap(True)
        info.setStyleSheet("color: #636e72; padding: 15px; background-color: #fff5e6; border-radius: 8px;")
        layout.addWidget(info)
        
        layout.addStretch()
        
        return widget
        
    def create_tinxy_step(self):
        """Tinxy IoT setup"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        title = QLabel("🔌 Tinxy Device Integration")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        layout.addWidget(title)
        
        subtitle = QLabel("Control IoT devices during breaks (Optional)")
        subtitle.setFont(QFont("Segoe UI", 11))
        subtitle.setStyleSheet("color: #636e72;")
        layout.addWidget(subtitle)
        
        layout.addStretch()
        
        return widget
        
    def create_completion_step(self):
        """Completion screen"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("✅ Setup Complete!")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        message = QLabel("BreakGuard is ready to protect your health and productivity!")
        message.setFont(QFont("Segoe UI", 12))
        message.setStyleSheet("color: #636e72;")
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message)
        
        return widget
        
    def toggle_totp_setup(self, checked):
        """Toggle TOTP setup visibility"""
        self.totp_container.setVisible(checked)
        
    def generate_totp(self):
        """Generate TOTP QR code"""
        from totp_auth import TOTPAuth
        
        self.generate_qr_btn.setEnabled(False)
        self.generate_qr_btn.setText("Generating...")
        
        try:
            self.totp_auth = TOTPAuth()
            qr_img = self.totp_auth.generate_qr_code()
            
            # Convert PIL image to QPixmap
            buffer = io.BytesIO()
            qr_img.save(buffer, format='PNG')
            buffer.seek(0)
            
            qimage = QImage()
            qimage.loadFromData(buffer.read())
            
            # Scale to fit
            self.qr_pixmap = QPixmap.fromImage(qimage).scaled(
                330, 330,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.qr_label.setPixmap(self.qr_pixmap)
            
            # Update instructions
            instructions = (
                "✓ QR Code Generated Successfully!\n\n"
                "Scan with Google Authenticator:\n\n"
                "1. Open Google Authenticator on your phone\n"
                "2. Tap the '+' button to add account\n"
                "3. Select 'Scan a QR code'\n"
                "4. Point camera at the QR code\n"
                "5. A 6-digit code will appear\n\n"
                f"Manual Entry Secret:\n{self.totp_auth.get_secret()}\n\n"
                "(Save this key safely!)"
            )
            self.totp_instructions.setText(instructions)
            
            self.config_data['totp_secret'] = self.totp_auth.get_secret()
            
            # Show verification
            self.verify_frame.show()
            self.totp_verified = False
            
            self.generate_qr_btn.setText("Regenerate QR Code")
            self.generate_qr_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate QR code: {str(e)}")
            self.generate_qr_btn.setText("Generate QR Code")
            self.generate_qr_btn.setEnabled(True)
            
    def verify_totp_code(self):
        """Verify TOTP code"""
        if not self.totp_auth:
            self.verify_status.setText("❌ Please generate QR code first")
            self.verify_status.setStyleSheet("color: #d63031;")
            return
            
        code = self.verify_code_entry.text().strip()
        
        if not code:
            self.verify_status.setText("❌ Please enter the 6-digit code")
            self.verify_status.setStyleSheet("color: #d63031;")
            return
            
        if self.totp_auth.verify_code(code):
            self.verify_status.setText("✅ Verified! Setup complete!")
            self.verify_status.setStyleSheet("color: #00b894;")
            self.verify_btn.setEnabled(False)
            self.verify_code_entry.setEnabled(False)
            self.totp_verified = True
            
            # Auto-advance after success
            QApplication.processEvents()
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(1500, self.go_next)
        else:
            self.verify_status.setText("❌ Invalid code. Please try again.")
            self.verify_status.setStyleSheet("color: #d63031;")
            self.verify_code_entry.clear()
            self.verify_code_entry.setFocus()
            
    def go_next(self):
        """Go to next step"""
        if self.current_step < 5:
            # Validate current step
            if self.validate_step():
                self.current_step += 1
                self.stacked_widget.setCurrentIndex(self.current_step)
                self.progress_bar.setValue(self.current_step + 1)
                
                # Update buttons
                self.back_btn.setEnabled(self.current_step > 0)
                if self.current_step == 5:
                    self.next_btn.setText("Finish")
        else:
            self.finish_setup()
            
    def go_back(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self.stacked_widget.setCurrentIndex(self.current_step)
            self.progress_bar.setValue(self.current_step + 1)
            
            # Update buttons
            self.back_btn.setEnabled(self.current_step > 0)
            self.next_btn.setText("Next →")
            
    def validate_step(self):
        """Validate current step"""
        # Step 2: TOTP validation
        if self.current_step == 2 and self.totp_enabled.isChecked():
            if not self.totp_auth:
                QMessageBox.warning(
                    self,
                    "Setup Required",
                    "Please click 'Generate QR Code' to set up Google Authenticator."
                )
                return False
                
            if not self.totp_verified:
                QMessageBox.warning(
                    self,
                    "Verification Required",
                    "Please verify your TOTP setup by entering the 6-digit code.\n\n"
                    "This ensures your authentication is working correctly!"
                )
                return False
                
        return True
        
    def finish_setup(self):
        """Complete setup"""
        # Save configuration
        self.config_data['work_interval_minutes'] = self.work_interval_spin.value()
        self.config_data['warning_before_minutes'] = self.warning_spin.value()
        self.config_data['auth_enabled'] = self.totp_enabled.isChecked()
        
        # Save to config file
        from config_manager import ConfigManager
        config_manager = ConfigManager()
        
        for key, value in self.config_data.items():
            config_manager.set(key, value)
        
        config_manager.save()
        
        QMessageBox.information(
            self,
            "Setup Complete",
            "BreakGuard has been configured successfully!\n\n"
            "The application will now start monitoring your work intervals."
        )
        
        self.close()
        
    def run(self):
        """Run the wizard"""
        self.show()


def run_setup_wizard():
    """Run the setup wizard"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    wizard = SetupWizard()
    wizard.run()
    
    return app.exec()


if __name__ == '__main__':
    run_setup_wizard()
