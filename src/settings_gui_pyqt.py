"""
Settings GUI (PyQt6)
Window to modify BreakGuard settings after setup
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QSpinBox, QCheckBox, QLineEdit,
                             QGroupBox, QTabWidget, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from config_manager import ConfigManager
from tinxy_api import TinxyAPI
from windows_startup import WindowsStartup

class SettingsWindow(QWidget):
    """Settings window for BreakGuard configuration"""
    
    settings_saved = pyqtSignal()
    
    def __init__(self, config: ConfigManager = None):
        """Initialize settings window
        
        Args:
            config: ConfigManager instance
        """
        super().__init__()
        
        self.config = config or ConfigManager()
        
        self.setWindowTitle("BreakGuard Settings")
        self.setFixedSize(600, 500)
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Setup settings UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("⚙️ BreakGuard Settings")
        title_font = QFont("Segoe UI", 18, QFont.Weight.Bold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._create_general_tab(), "General")
        tabs.addTab(self._create_security_tab(), "Security")
        tabs.addTab(self._create_tinxy_tab(), "Tinxy IoT")
        tabs.addTab(self._create_advanced_tab(), "Advanced")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setMinimumWidth(130)
        reset_btn.clicked.connect(self._reset_defaults)
        button_layout.addWidget(reset_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumWidth(130)
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Settings")
        save_btn.setMinimumWidth(130)
        save_btn.clicked.connect(self._save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14a19f;
            }
        """)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def _create_general_tab(self) -> QWidget:
        """Create general settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Work Intervals Group
        intervals_group = QGroupBox("Work Intervals")
        intervals_layout = QVBoxLayout()
        
        # Work interval
        work_layout = QHBoxLayout()
        work_label = QLabel("Work interval:")
        work_label.setMinimumWidth(150)
        self.work_spin = QSpinBox()
        self.work_spin.setRange(15, 240)
        self.work_spin.setSuffix(" minutes")
        work_layout.addWidget(work_label)
        work_layout.addWidget(self.work_spin)
        work_layout.addStretch()
        intervals_layout.addLayout(work_layout)
        
        # Warning time
        warning_layout = QHBoxLayout()
        warning_label = QLabel("Warning before lock:")
        warning_label.setMinimumWidth(150)
        self.warning_spin = QSpinBox()
        self.warning_spin.setRange(1, 30)
        self.warning_spin.setSuffix(" minutes")
        warning_layout.addWidget(warning_label)
        warning_layout.addWidget(self.warning_spin)
        warning_layout.addStretch()
        intervals_layout.addLayout(warning_layout)
        
        # Break duration
        break_layout = QHBoxLayout()
        break_label = QLabel("Minimum break:")
        break_label.setMinimumWidth(150)
        self.break_spin = QSpinBox()
        self.break_spin.setRange(5, 60)
        self.break_spin.setSuffix(" minutes")
        break_layout.addWidget(break_label)
        break_layout.addWidget(self.break_spin)
        break_layout.addStretch()
        intervals_layout.addLayout(break_layout)
        
        intervals_group.setLayout(intervals_layout)
        layout.addWidget(intervals_group)
        
        # Startup Group
        startup_group = QGroupBox("Startup")
        startup_layout = QVBoxLayout()
        
        self.auto_start_check = QCheckBox("Start BreakGuard with Windows")
        startup_layout.addWidget(self.auto_start_check)
        
        startup_group.setLayout(startup_layout)
        layout.addWidget(startup_group)
        
        layout.addStretch()
        return tab
    
    def _create_security_tab(self) -> QWidget:
        """Create security settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Authentication Group
        auth_group = QGroupBox("Authentication")
        auth_layout = QVBoxLayout()
        
        self.totp_check = QCheckBox("Enable Google Authenticator (TOTP)")
        auth_layout.addWidget(self.totp_check)
        
        self.face_check = QCheckBox("Enable Face Verification")
        auth_layout.addWidget(self.face_check)
        
        auth_group.setLayout(auth_layout)
        layout.addWidget(auth_group)
        
        # Snooze Group
        snooze_group = QGroupBox("Break Snooze")
        snooze_layout = QVBoxLayout()
        
        snooze_h_layout = QHBoxLayout()
        snooze_label = QLabel("Max snooze count:")
        snooze_label.setMinimumWidth(150)
        self.snooze_spin = QSpinBox()
        self.snooze_spin.setRange(0, 5)
        self.snooze_spin.setSuffix(" times")
        snooze_h_layout.addWidget(snooze_label)
        snooze_h_layout.addWidget(self.snooze_spin)
        snooze_h_layout.addStretch()
        snooze_layout.addLayout(snooze_h_layout)
        
        snooze_info = QLabel("Note: Setting to 0 disables snooze completely")
        snooze_info.setStyleSheet("color: #666666; font-size: 11px;")
        snooze_layout.addWidget(snooze_info)
        
        snooze_group.setLayout(snooze_layout)
        layout.addWidget(snooze_group)
        
        # Buttons
        btn_layout = QVBoxLayout()
        
        reconfig_totp_btn = QPushButton("Reconfigure Google Authenticator")
        reconfig_totp_btn.clicked.connect(self._reconfigure_totp)
        btn_layout.addWidget(reconfig_totp_btn)
        
        reconfig_face_btn = QPushButton("Re-register Face")
        reconfig_face_btn.clicked.connect(self._reconfigure_face)
        btn_layout.addWidget(reconfig_face_btn)
        
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        return tab
    
    def _create_tinxy_tab(self) -> QWidget:
        """Create Tinxy IoT settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Tinxy Group
        tinxy_group = QGroupBox("Tinxy Smart Device Control")
        tinxy_layout = QVBoxLayout()
        
        self.tinxy_check = QCheckBox("Enable Tinxy Integration")
        self.tinxy_check.stateChanged.connect(self._on_tinxy_toggle)
        tinxy_layout.addWidget(self.tinxy_check)
        
        # API Key
        api_layout = QHBoxLayout()
        api_label = QLabel("API Key:")
        api_label.setMinimumWidth(120)
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("Enter Tinxy API key")
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_input)
        tinxy_layout.addLayout(api_layout)
        
        # Device ID
        device_layout = QHBoxLayout()
        device_label = QLabel("Device ID:")
        device_label.setMinimumWidth(120)
        self.device_input = QLineEdit()
        self.device_input.setPlaceholderText("Enter device ID")
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_input)
        tinxy_layout.addLayout(device_layout)
        
        # Device Number
        num_layout = QHBoxLayout()
        num_label = QLabel("Device Number:")
        num_label.setMinimumWidth(120)
        self.device_num_spin = QSpinBox()
        self.device_num_spin.setRange(1, 4)
        num_layout.addWidget(num_label)
        num_layout.addWidget(self.device_num_spin)
        num_layout.addStretch()
        tinxy_layout.addLayout(num_layout)
        
        # Test button
        test_btn = QPushButton("Test Connection")
        test_btn.setMinimumWidth(150)
        test_btn.clicked.connect(self._test_tinxy)
        tinxy_layout.addWidget(test_btn)
        
        self.tinxy_status_label = QLabel("")
        tinxy_layout.addWidget(self.tinxy_status_label)
        
        tinxy_group.setLayout(tinxy_layout)
        layout.addWidget(tinxy_group)
        
        layout.addStretch()
        return tab
    
    def _create_advanced_tab(self) -> QWidget:
        """Create advanced settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Info
        info_label = QLabel("Advanced Settings")
        info_font = QFont("Segoe UI", 12, QFont.Weight.Bold)
        info_label.setFont(info_font)
        layout.addWidget(info_label)
        
        # Buttons
        clear_totp_btn = QPushButton("Clear TOTP Secret")
        clear_totp_btn.clicked.connect(self._clear_totp)
        layout.addWidget(clear_totp_btn)
        
        clear_face_btn = QPushButton("Clear Face Data")
        clear_face_btn.clicked.connect(self._clear_face)
        layout.addWidget(clear_face_btn)
        
        reset_all_btn = QPushButton("Reset All Settings")
        reset_all_btn.clicked.connect(self._reset_all)
        reset_all_btn.setStyleSheet("QPushButton { color: red; }")
        layout.addWidget(reset_all_btn)
        
        layout.addStretch()
        
        # Version info
        version_label = QLabel("BreakGuard v1.0\n© 2025")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(version_label)
        
        return tab
    
    def _load_settings(self):
        """Load current settings into UI"""
        self.work_spin.setValue(self.config.get('work_interval_minutes', 60))
        self.warning_spin.setValue(self.config.get('warning_before_minutes', 5))
        self.break_spin.setValue(self.config.get('break_duration_minutes', 10))
        
        self.auto_start_check.setChecked(self.config.get('auto_start_windows', True))
        
        self.totp_check.setChecked(self.config.get('totp_enabled', True))
        self.face_check.setChecked(self.config.get('face_verification_enabled', True))
        self.snooze_spin.setValue(self.config.get('max_snooze_count', 1))
        
        self.tinxy_check.setChecked(self.config.get('tinxy_enabled', False))
        self.api_input.setText(self.config.get('tinxy_api_key', ''))
        self.device_input.setText(self.config.get('tinxy_device_id', ''))
        self.device_num_spin.setValue(self.config.get('tinxy_device_number', 1))
        
        self._on_tinxy_toggle(self.tinxy_check.isChecked())
    
    def _save_settings(self):
        """Save settings"""
        self.config.set('work_interval_minutes', self.work_spin.value())
        self.config.set('warning_before_minutes', self.warning_spin.value())
        self.config.set('break_duration_minutes', self.break_spin.value())
        
        self.config.set('auto_start_windows', self.auto_start_check.isChecked())
        
        self.config.set('totp_enabled', self.totp_check.isChecked())
        self.config.set('face_verification_enabled', self.face_check.isChecked())
        self.config.set('max_snooze_count', self.snooze_spin.value())
        
        self.config.set('tinxy_enabled', self.tinxy_check.isChecked())
        self.config.set('tinxy_api_key', self.api_input.text())
        self.config.set('tinxy_device_id', self.device_input.text())
        self.config.set('tinxy_device_number', self.device_num_spin.value())
        
        if self.config.save_config():
            # Update Windows startup
            startup = WindowsStartup()
            startup.toggle_startup(self.auto_start_check.isChecked())
            
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.settings_saved.emit()
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Failed to save settings.")
    
    def _on_tinxy_toggle(self, checked):
        """Handle Tinxy checkbox toggle"""
        self.api_input.setEnabled(checked)
        self.device_input.setEnabled(checked)
        self.device_num_spin.setEnabled(checked)
    
    def _test_tinxy(self):
        """Test Tinxy connection"""
        api_key = self.api_input.text().strip()
        device_id = self.device_input.text().strip()
        
        if not api_key or not device_id:
            self.tinxy_status_label.setText("❌ Please enter API key and device ID")
            self.tinxy_status_label.setStyleSheet("color: red;")
            return
        
        self.tinxy_status_label.setText("Testing...")
        QApplication.processEvents()
        
        tinxy = TinxyAPI(api_key, device_id)
        if tinxy.test_connection():
            self.tinxy_status_label.setText("✅ Connected successfully!")
            self.tinxy_status_label.setStyleSheet("color: green;")
        else:
            self.tinxy_status_label.setText("❌ Connection failed")
            self.tinxy_status_label.setStyleSheet("color: red;")
    
    def _reset_defaults(self):
        """Reset to default settings"""
        reply = QMessageBox.question(
            self, "Reset Settings",
            "Reset all settings to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config.reset_to_defaults()
            self._load_settings()
    
    def _reconfigure_totp(self):
        """Open TOTP reconfiguration"""
        QMessageBox.information(self, "Info", "Please run Setup Wizard again from system tray menu.")
    
    def _reconfigure_face(self):
        """Open face reconfiguration"""
        QMessageBox.information(self, "Info", "Please run Setup Wizard again from system tray menu.")
    
    def _clear_totp(self):
        """Clear TOTP secret"""
        reply = QMessageBox.warning(
            self, "Clear TOTP",
            "This will remove your Google Authenticator setup. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            from totp_auth import TOTPAuth
            totp = TOTPAuth()
            # Would need implementation to clear
            QMessageBox.information(self, "Info", "TOTP cleared. Run setup again.")
    
    def _clear_face(self):
        """Clear face data"""
        reply = QMessageBox.warning(
            self, "Clear Face Data",
            "This will remove all registered faces. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            from face_verification import FaceVerification
            face = FaceVerification()
            face.clear_registered_faces()
            QMessageBox.information(self, "Info", "Face data cleared. Run setup again.")
    
    def _reset_all(self):
        """Reset everything"""
        reply = QMessageBox.critical(
            self, "Reset All",
            "This will DELETE ALL settings and data. Are you sure?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config.reset_to_defaults()
            self.config.save_config()
            QMessageBox.information(self, "Info", "All settings reset. Please run setup again.")
            self.close()
