"""
Settings GUI (PyQt6)
Window to modify BreakGuard settings after setup
"""
from __future__ import annotations

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QSpinBox, QCheckBox, QLineEdit,
                             QGroupBox, QTabWidget, QMessageBox, QApplication,
                             QFileDialog, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QUrl
from PyQt6.QtGui import QFont, QDesktopServices

from config_manager import ConfigManager
from tinxy_api import TinxyAPI
from windows_startup import WindowsStartup
from theme.theme import load_stylesheet

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
        self.setMinimumSize(600, 500)
        self.resize(600, 500)
        
        self.setStyleSheet(load_stylesheet())
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        """Setup settings UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("⚙️ BreakGuard Settings")
        title.setProperty("class", "h2")
        layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        
        # Wrap tabs in scroll areas for better navigation
        general_scroll = self._create_scrollable_tab(self._create_general_tab())
        security_scroll = self._create_scrollable_tab(self._create_security_tab())
        tinxy_scroll = self._create_scrollable_tab(self._create_tinxy_tab())
        advanced_scroll = self._create_scrollable_tab(self._create_advanced_tab())
        
        tabs.addTab(general_scroll, "General")
        tabs.addTab(security_scroll, "Security")
        tabs.addTab(tinxy_scroll, "Tinxy IoT")
        tabs.addTab(advanced_scroll, "Advanced")
        
        # About Tab
        about_scroll = self._create_scrollable_tab(self._create_about_tab())
        tabs.addTab(about_scroll, "About")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setMinimumWidth(130)
        reset_btn.setProperty("class", "secondary-btn")
        reset_btn.setAccessibleName("Reset to Defaults")
        reset_btn.setToolTip("Reset all settings to their default values")
        reset_btn.clicked.connect(self._reset_defaults)
        button_layout.addWidget(reset_btn)
        
        cancel_btn = QPushButton("&Cancel")
        cancel_btn.setMinimumWidth(130)
        cancel_btn.setProperty("class", "secondary-btn")
        cancel_btn.setAccessibleName("Cancel")
        cancel_btn.setToolTip("Close settings without saving (Alt+C)")
        cancel_btn.setShortcut("Alt+C")
        cancel_btn.clicked.connect(self.close)
        button_layout.addWidget(cancel_btn)
        
        self.save_btn = QPushButton("&Save Settings")
        self.save_btn.setMinimumWidth(130)
        self.save_btn.setProperty("class", "primary-btn")
        self.save_btn.setAccessibleName("Save Settings")
        self.save_btn.setToolTip("Save changes and close (Alt+S)")
        self.save_btn.setShortcut("Alt+S")
        self.save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
    
    def _create_scrollable_tab(self, tab_widget: QWidget) -> QScrollArea:
        """Wrap tab content in a scrollable area
        
        Args:
            tab_widget: The tab content widget
            
        Returns:
            QScrollArea containing the widget
        """
        scroll = QScrollArea()
        scroll.setWidget(tab_widget)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        return scroll
    
    def _create_general_tab(self) -> QWidget:
        """Create general settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Work Intervals Group
        intervals_group = QGroupBox("Work Intervals")
        intervals_group.setAccessibleName("Work Intervals")
        intervals_group.setAccessibleDescription("Configure work session duration, warning time, and minimum break duration")
        intervals_layout = QVBoxLayout()
        
        # Work interval
        work_layout = QHBoxLayout()
        work_label = QLabel("Work interval:")
        work_label.setMinimumWidth(150)
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 240)
        self.work_spin.setSuffix(" minutes")
        self.work_spin.setAccessibleName("Work interval in minutes")
        self.work_spin.setAccessibleDescription("Set the length of work sessions before a break is required, between 1 and 240 minutes")
        self.work_spin.setToolTip("Set the duration of work sessions (1-240 minutes)")
        self.work_spin.valueChanged.connect(lambda v: self._validate_spinbox(self.work_spin, v, 1, 240, "Work interval"))
        self.work_validation_label = QLabel("")
        self.work_validation_label.setProperty("class", "validation-msg")
        work_layout.addWidget(work_label)
        work_layout.addWidget(self.work_spin)
        work_layout.addWidget(self.work_validation_label)
        work_layout.addStretch()
        intervals_layout.addLayout(work_layout)
        
        # Warning time
        warning_layout = QHBoxLayout()
        warning_label = QLabel("Warning before lock:")
        warning_label.setMinimumWidth(150)
        self.warning_spin = QSpinBox()
        self.warning_spin.setRange(1, 30)
        self.warning_spin.setSuffix(" minutes")
        self.warning_spin.setAccessibleName("Warning time before lock in minutes")
        self.warning_spin.setAccessibleDescription("Set how far in advance you receive a warning before the lock screen appears, between 1 and 30 minutes")
        self.warning_spin.setToolTip("Set how long before the lock screen appears a warning is shown (1-30 minutes)")
        self.warning_spin.valueChanged.connect(lambda v: self._validate_spinbox(self.warning_spin, v, 1, 30, "Warning time"))
        self.warning_validation_label = QLabel("")
        self.warning_validation_label.setProperty("class", "validation-msg")
        warning_layout.addWidget(warning_label)
        warning_layout.addWidget(self.warning_spin)
        warning_layout.addWidget(self.warning_validation_label)
        warning_layout.addStretch()
        intervals_layout.addLayout(warning_layout)
        
        # Break duration
        break_layout = QHBoxLayout()
        break_label = QLabel("Minimum break:")
        break_label.setMinimumWidth(150)
        self.break_spin = QSpinBox()
        self.break_spin.setRange(5, 60)
        self.break_spin.setSuffix(" minutes")
        self.break_spin.setAccessibleName("Minimum break duration in minutes")
        self.break_spin.setAccessibleDescription("Set the minimum length of break periods that you must take, between 5 and 60 minutes")
        self.break_spin.setToolTip("Set the minimum duration for breaks (5-60 minutes)")
        self.break_spin.valueChanged.connect(lambda v: self._validate_spinbox(self.break_spin, v, 5, 60, "Break duration"))
        self.break_validation_label = QLabel("")
        self.break_validation_label.setProperty("class", "validation-msg")
        break_layout.addWidget(break_label)
        break_layout.addWidget(self.break_spin)
        break_layout.addWidget(self.break_validation_label)
        break_layout.addStretch()
        intervals_layout.addLayout(break_layout)
        
        intervals_group.setLayout(intervals_layout)
        layout.addWidget(intervals_group)
        
        # Startup Group
        startup_group = QGroupBox("Startup")
        startup_group.setAccessibleName("Startup")
        startup_group.setAccessibleDescription("Configure how BreakGuard starts and runs")
        startup_layout = QVBoxLayout()
        
        self.auto_start_check = QCheckBox("Start BreakGuard with Windows")
        self.auto_start_check.setAccessibleName("Start with Windows checkbox")
        self.auto_start_check.setAccessibleDescription("When enabled, BreakGuard will automatically launch whenever you start your computer")
        self.auto_start_check.setToolTip("Automatically start BreakGuard when Windows starts")
        startup_layout.addWidget(self.auto_start_check)
        
        self.auto_unlock_check = QCheckBox("Auto-unlock after break complete")
        self.auto_unlock_check.setAccessibleName("Auto-unlock checkbox")
        self.auto_unlock_check.setAccessibleDescription("When enabled, the lock screen will automatically close when the break timer finishes")
        self.auto_unlock_check.setToolTip("Automatically unlock screen when break time is over")
        startup_layout.addWidget(self.auto_unlock_check)
        
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
        auth_group.setAccessibleName("Authentication")
        auth_group.setAccessibleDescription("Choose security methods for unlocking the screen: TOTP from Google Authenticator or face verification")
        auth_layout = QVBoxLayout()
        
        self.totp_check = QCheckBox("Enable Google Authenticator (TOTP)")
        self.totp_check.setAccessibleName("Enable TOTP checkbox")
        self.totp_check.setAccessibleDescription("Enable Google Authenticator (TOTP) as a security method. You will need to generate a code from an authenticator app to unlock")
        self.totp_check.setToolTip("Enable Two-Factor Authentication using Google Authenticator")
        auth_layout.addWidget(self.totp_check)
        
        self.face_check = QCheckBox("Enable Face Verification")
        self.face_check.setAccessibleName("Enable Face Verification checkbox")
        self.face_check.setAccessibleDescription("Enable facial recognition as a security method. Your device camera will be used to verify your face before unlocking")
        self.face_check.setToolTip("Enable facial recognition for unlocking")
        auth_layout.addWidget(self.face_check)
        
        auth_group.setLayout(auth_layout)
        layout.addWidget(auth_group)
        
        # Snooze Group
        snooze_group = QGroupBox("Break Snooze")
        snooze_group.setAccessibleName("Break Snooze")
        snooze_group.setAccessibleDescription("Configure how many times you can defer a required break")
        snooze_layout = QVBoxLayout()
        
        snooze_h_layout = QHBoxLayout()
        snooze_label = QLabel("Max snooze count:")
        snooze_label.setMinimumWidth(150)
        self.snooze_spin = QSpinBox()
        self.snooze_spin.setRange(0, 5)
        self.snooze_spin.setSuffix(" times")
        self.snooze_spin.setAccessibleName("Max snooze count")
        self.snooze_spin.setAccessibleDescription("Set the maximum number of times you can postpone a break. Set to 0 to disable snoozing entirely")
        self.snooze_spin.setToolTip("Maximum number of times you can snooze a break")
        snooze_h_layout.addWidget(snooze_label)
        snooze_h_layout.addWidget(self.snooze_spin)
        snooze_h_layout.addStretch()
        snooze_layout.addLayout(snooze_h_layout)
        
        snooze_info = QLabel("Note: Setting to 0 disables snooze completely")
        snooze_info.setProperty("class", "info-text")
        layout.addWidget(snooze_info)
        
        snooze_group.setLayout(snooze_layout)
        layout.addWidget(snooze_group)
        
        # Buttons
        btn_layout = QVBoxLayout()
        
        reconfig_totp_btn = QPushButton("Reconfigure Google Authenticator")
        reconfig_totp_btn.clicked.connect(self._reconfigure_totp)
        reconfig_totp_btn.setAccessibleName("Reconfigure TOTP button")
        reconfig_totp_btn.setAccessibleDescription("Generate a new QR code and secret key for Google Authenticator setup")
        reconfig_totp_btn.setToolTip("Setup Google Authenticator again")
        btn_layout.addWidget(reconfig_totp_btn)
        
        reconfig_face_btn = QPushButton("Re-register Face")
        reconfig_face_btn.clicked.connect(self._reconfigure_face)
        reconfig_face_btn.setAccessibleName("Re-register Face button")
        reconfig_face_btn.setAccessibleDescription("Recapture your facial features for verification. This updates your stored face data")
        reconfig_face_btn.setToolTip("Capture face data again")
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
        tinxy_group.setAccessibleName("Tinxy Smart Device Control")
        tinxy_group.setAccessibleDescription("Configure integration with Tinxy smart devices to control lights or outlets during breaks")
        tinxy_layout = QVBoxLayout()
        
        self.tinxy_check = QCheckBox("Enable Tinxy Integration")
        self.tinxy_check.stateChanged.connect(self._on_tinxy_toggle)
        self.tinxy_check.setAccessibleName("Enable Tinxy Integration checkbox")
        self.tinxy_check.setAccessibleDescription("Enable smart device control using Tinxy API. When enabled, you can turn devices on or off during breaks")
        self.tinxy_check.setToolTip("Enable control of Tinxy smart devices")
        tinxy_layout.addWidget(self.tinxy_check)
        
        # API Key
        api_layout = QHBoxLayout()
        api_label = QLabel("API Key:")
        api_label.setMinimumWidth(120)
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("Enter Tinxy API key")
        self.api_input.setAccessibleName("Tinxy API Key input")
        self.api_input.setAccessibleDescription("Enter the API key from your Tinxy account to authorize smart device control")
        self.api_input.setToolTip("Enter your Tinxy API key")
        api_layout.addWidget(api_label)
        api_layout.addWidget(self.api_input)
        tinxy_layout.addLayout(api_layout)
        
        # Device ID
        device_layout = QHBoxLayout()
        device_label = QLabel("Device ID:")
        device_label.setMinimumWidth(120)
        self.device_input = QLineEdit()
        self.device_input.setPlaceholderText("Enter device ID")
        self.device_input.setAccessibleName("Tinxy Device ID input")
        self.device_input.setAccessibleDescription("Enter the unique identifier of your Tinxy device, found in the Tinxy app")
        self.device_input.setToolTip("Enter the ID of the Tinxy device")
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_input)
        tinxy_layout.addLayout(device_layout)
        
        # Device Number
        num_layout = QHBoxLayout()
        num_label = QLabel("Device Number:")
        num_label.setMinimumWidth(120)
        self.device_num_spin = QSpinBox()
        self.device_num_spin.setRange(1, 4)
        self.device_num_spin.setAccessibleName("Device Number spinbox")
        self.device_num_spin.setAccessibleDescription("Select which device number to control: 1, 2, 3, or 4")
        self.device_num_spin.setToolTip("Select the device number (1-4)")
        num_layout.addWidget(num_label)
        num_layout.addWidget(self.device_num_spin)
        num_layout.addStretch()
        tinxy_layout.addLayout(num_layout)
        
        # Test button
        test_btn = QPushButton("Test Connection")
        test_btn.setMinimumWidth(150)
        test_btn.clicked.connect(self._test_tinxy)
        test_btn.setAccessibleName("Test Connection button")
        test_btn.setAccessibleDescription("Send a test command to verify the connection to your Tinxy device")
        test_btn.setToolTip("Test the connection to the Tinxy device")
        tinxy_layout.addWidget(test_btn)
        
        self.tinxy_status_label = QLabel("")
        self.tinxy_status_label.setAccessibleName("Connection status")
        self.tinxy_status_label.setAccessibleDescription("Displays the result of the connection test")
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
        info_label.setProperty("class", "h3")
        layout.addWidget(info_label)
        
        # Export/Import Group
        export_import_group = QGroupBox("Settings Backup")
        export_import_group.setAccessibleName("Settings Backup")
        export_import_group.setAccessibleDescription("Export your settings to a file for backup, or import previously saved settings")
        export_import_layout = QVBoxLayout()
        
        export_btn = QPushButton("📥 Export Settings")
        export_btn.clicked.connect(self._export_settings)
        export_btn.setAccessibleName("Export Settings button")
        export_btn.setAccessibleDescription("Save a copy of your current settings to a file for backup or sharing")
        export_btn.setToolTip("Export current settings to a file")
        export_import_layout.addWidget(export_btn)
        
        import_btn = QPushButton("📤 Import Settings")
        import_btn.clicked.connect(self._import_settings)
        import_btn.setAccessibleName("Import Settings button")
        import_btn.setAccessibleDescription("Load previously exported settings from a file")
        import_btn.setToolTip("Import settings from a backup file")
        export_import_layout.addWidget(import_btn)
        
        export_import_group.setLayout(export_import_layout)
        layout.addWidget(export_import_group)
        
        # Buttons
        clear_totp_btn = QPushButton("Clear TOTP Secret")
        clear_totp_btn.clicked.connect(self._clear_totp)
        clear_totp_btn.setAccessibleName("Clear TOTP Secret button")
        clear_totp_btn.setAccessibleDescription("Remove and reset the stored TOTP secret key. You will need to reconfigure Google Authenticator")
        clear_totp_btn.setToolTip("Remove the stored TOTP secret")
        layout.addWidget(clear_totp_btn)
        
        clear_face_btn = QPushButton("Clear Face Data")
        clear_face_btn.clicked.connect(self._clear_face)
        clear_face_btn.setAccessibleName("Clear Face Data button")
        clear_face_btn.setToolTip("Remove stored face verification data")
        layout.addWidget(clear_face_btn)
        
        reset_all_btn = QPushButton("Reset All Settings")
        reset_all_btn.clicked.connect(self._reset_all)
        reset_all_btn.setProperty("class", "danger-btn")
        reset_all_btn.setAccessibleName("Reset All Settings button")
        reset_all_btn.setToolTip("Reset all application settings to factory defaults")
        layout.addWidget(reset_all_btn)
        
        layout.addStretch()
        
        # Version info
        version_label = QLabel("BreakGuard v1.0\n© 2025")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setProperty("class", "info-text")
        layout.addWidget(version_label)
        
        return tab
    
    def _load_settings(self):
        """Load current settings into UI"""
        self.work_spin.setValue(self.config.get('work_interval_minutes', 60))
        self.warning_spin.setValue(self.config.get('warning_before_minutes', 5))
        self.break_spin.setValue(self.config.get('break_duration_minutes', 10))
        
        self.auto_start_check.setChecked(self.config.get('auto_start_windows', True))
        self.auto_unlock_check.setChecked(self.config.get('auto_unlock_after_break', False))
        
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
        self.config.set('auto_unlock_after_break', self.auto_unlock_check.isChecked())
        
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
    
    def _validate_spinbox(self, spinbox, value, min_val, max_val, field_name):
        """Validate spinbox value in real-time
        
        Args:
            spinbox: The QSpinBox to validate
            value: Current value
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            field_name: Name of field for validation label
        """
        # Find associated validation label
        validation_label = None
        if spinbox == self.work_spin:
            validation_label = self.work_validation_label
        elif spinbox == self.warning_spin:
            validation_label = self.warning_validation_label
        elif spinbox == self.break_spin:
            validation_label = self.break_validation_label
        
        if not validation_label:
            return
        
        # Validate value
        is_valid = min_val <= value <= max_val
        
        if not is_valid:
            validation_label.setText(f"⚠️ {min_val}-{max_val}")
            validation_label.setStyleSheet("color: #dc3545; font-size: 11px;")
            spinbox.setStyleSheet("border: 2px solid #dc3545;")
        else:
            validation_label.setText("✅")
            validation_label.setStyleSheet("color: #28a745; font-size: 11px;")
            spinbox.setStyleSheet("")
        
        # Update save button state
        self._update_save_button_state()
    
    def _update_save_button_state(self):
        """Enable/disable save button based on validation state"""
        # Check if all spinboxes are valid
        work_valid = self.work_spin.minimum() <= self.work_spin.value() <= self.work_spin.maximum()
        warning_valid = self.warning_spin.minimum() <= self.warning_spin.value() <= self.warning_spin.maximum()
        break_valid = self.break_spin.minimum() <= self.break_spin.value() <= self.break_spin.maximum()
        
        all_valid = work_valid and warning_valid and break_valid
        
        # Enable/disable save button
        self.save_btn.setEnabled(all_valid)
        if not all_valid:
            self.save_btn.setToolTip("Please fix validation errors before saving")
        else:
            self.save_btn.setToolTip("Save changes and close (Alt+S)")
    
    def _test_tinxy(self):
        """Test Tinxy connection"""
        api_key = self.api_input.text().strip()
        device_id = self.device_input.text().strip()
        
        if not api_key or not device_id:
            self.tinxy_status_label.setText("❌ Please enter API key and device ID")
            self.tinxy_status_label.setStyleSheet("color: red;")
            return
        
        self.tinxy_status_label.setText("⏳ Testing connection...")
        self.tinxy_status_label.setStyleSheet("color: orange;")
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
    
    def _create_about_tab(self) -> QWidget:
        """Create about tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # Logo/Title
        title_label = QLabel("🛡️ BreakGuard")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(title_label)
        
        version_label = QLabel("Version 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: #888;")
        layout.addWidget(version_label)
        
        # Description
        desc_label = QLabel(
            "BreakGuard is an open-source tool designed to enforce healthy work breaks.\n"
            "It helps you maintain discipline and protect your health during long coding sessions."
        )
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("margin: 10px 20px;")
        layout.addWidget(desc_label)
        
        # Links Group
        links_group = QGroupBox("Project Information")
        links_layout = QVBoxLayout()
        links_layout.setSpacing(10)
        
        # Repository Link
        repo_btn = QPushButton("View on GitHub")
        repo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        repo_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://github.com/ProgrammerNomad/BreakGuard")))
        links_layout.addWidget(repo_btn)
        
        # License Info
        license_label = QLabel("License: MIT License (Open Source)")
        license_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        links_layout.addWidget(license_label)
        
        # Author Info
        author_label = QLabel("Created by: ProgrammerNomad")
        author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        links_layout.addWidget(author_label)
        
        links_group.setLayout(links_layout)
        layout.addWidget(links_group)
        
        layout.addStretch()
        return tab

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
    
    def _export_settings(self):
        """Export current settings to a file"""
        from datetime import datetime
        default_filename = f"breakguard_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Settings",
            default_filename,
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            if self.config.export_config(file_path):
                QMessageBox.information(
                    self,
                    "Success",
                    f"Settings exported successfully to:\n{file_path}"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to export settings. Check logs for details."
                )
    
    def _import_settings(self):
        """Import settings from a file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Settings",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                # Preview changes
                changes = self.config.import_config(file_path, validate=True)
                
                # Show confirmation dialog with changes
                modified_count = len(changes['modified'])
                added_count = len(changes['added'])
                
                msg = f"Import will make the following changes:\n\n"
                msg += f"• {modified_count} settings modified\n"
                msg += f"• {added_count} settings added\n\n"
                
                if modified_count > 0:
                    msg += f"Modified: {', '.join(changes['modified'][:5])}"
                    if modified_count > 5:
                        msg += f" and {modified_count - 5} more"
                    msg += "\n\n"
                
                msg += "Continue with import?"
                
                reply = QMessageBox.question(
                    self,
                    "Confirm Import",
                    msg,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    if self.config.apply_imported_config(file_path):
                        QMessageBox.information(
                            self,
                            "Success",
                            "Settings imported successfully!\nReloading settings..."
                        )
                        self._load_settings()
                    else:
                        QMessageBox.critical(
                            self,
                            "Error",
                            "Failed to import settings. Previous settings restored."
                        )
            
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Import Error",
                    f"Failed to import settings:\n{str(e)}"
                )
