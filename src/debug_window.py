"""
Debug Window
Displays current application state for troubleshooting
"""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor

import json
from datetime import datetime
from pathlib import Path

from config_manager import ConfigManager
from theme.theme import load_stylesheet


class DebugWindow(QWidget):
    """Debug window showing current application state"""
    
    closed = pyqtSignal()
    
    def __init__(self, config: ConfigManager = None):
        """Initialize debug window
        
        Args:
            config: ConfigManager instance
        """
        super().__init__()
        
        self.config = config or ConfigManager()
        
        self.setWindowTitle("BreakGuard Debug Info")
        self.setMinimumSize(600, 400)
        self.resize(700, 500)
        
        self.setStyleSheet(load_stylesheet())
        self._setup_ui()
        
        # Auto-refresh every 1 second
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_state)
        self.refresh_timer.start(1000)
    
    def _setup_ui(self) -> None:
        """Setup debug window UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("🐛 BreakGuard Debug Information")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Info text
        info_label = QLabel("Use this window to inspect the current application state for troubleshooting.")
        info_label.setStyleSheet("color: #666666; font-size: 11px;")
        layout.addWidget(info_label)
        
        # State display
        self.state_text = QTextEdit()
        self.state_text.setReadOnly(True)
        self.state_text.setFont(QFont("Courier New", 10))
        self.state_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.state_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh Now")
        refresh_btn.clicked.connect(self._refresh_state)
        refresh_btn.setMaximumWidth(150)
        button_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton("💾 Copy to Clipboard")
        export_btn.clicked.connect(self._copy_to_clipboard)
        export_btn.setMaximumWidth(150)
        button_layout.addWidget(export_btn)
        
        clear_btn = QPushButton("🗑️ Clear Log")
        clear_btn.clicked.connect(self._clear_log)
        clear_btn.setMaximumWidth(150)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("&Close")
        close_btn.clicked.connect(self.close)
        close_btn.setMaximumWidth(100)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Initial refresh
        self._refresh_state()
    
    def _refresh_state(self) -> None:
        """Refresh the displayed state"""
        try:
            # Load current app state from file
            state_file = Path(__file__).parent.parent / 'data' / 'app_state.json'
            app_state = {}
            config_data = {}
            
            if state_file.exists():
                with open(state_file, 'r') as f:
                    app_state = json.load(f)
            
            # Load current config
            config_file = Path(__file__).parent.parent / 'config.json'
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
            
            # Format output
            output = f"""
╔════════════════════════════════════════════════════════════╗
║                  APPLICATION STATE                        ║
╚════════════════════════════════════════════════════════════╝

📅 TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            if config_data:
                output += f"  Work Interval: {config_data.get('work_interval_minutes', 'N/A')} minutes\n"
                output += f"  Warning Time: {config_data.get('warning_before_minutes', 'N/A')} minutes\n"
                output += f"  Break Duration: {config_data.get('break_duration_minutes', 'N/A')} minutes\n"
                output += f"  Snooze Limit: {config_data.get('snooze_limit', 'N/A')} times\n"
                output += f"  TOTP Enabled: {config_data.get('totp_enabled', 'N/A')}\n"
                output += f"  Face Verification: {config_data.get('face_recognition_enabled', 'N/A')}\n"
                output += f"  Config Version: {config_data.get('config_version', 'N/A')}\n"
            
            output += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏱️ APPLICATION STATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            if app_state:
                output += f"  Current State: {app_state.get('state', 'N/A')}\n"
                output += f"  Last Updated: {app_state.get('timestamp', 'N/A')}\n"
            else:
                output += "  No state file found (app state not yet saved)\n"
            
            output += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📂 DATA FILES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            
            data_dir = Path(__file__).parent.parent / 'data'
            if data_dir.exists():
                for file_path in data_dir.iterdir():
                    if file_path.is_file():
                        size = file_path.stat().st_size
                        output += f"  ✓ {file_path.name} ({size} bytes)\n"
            
            output += f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 LOG LOCATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {Path(__file__).parent.parent / 'data' / 'breakguard.log'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 TIPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • Check the log file for detailed error messages
  • Use "Copy to Clipboard" to share debug info
  • Auto-refreshes every 1 second
"""
            
            self.state_text.setPlainText(output)
            
            # Scroll to top
            cursor = self.state_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.state_text.setTextCursor(cursor)
        
        except Exception as e:
            self.state_text.setPlainText(f"Error reading state: {str(e)}")
    
    def _copy_to_clipboard(self) -> None:
        """Copy current state to clipboard"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.state_text.toPlainText())
    
    def _clear_log(self) -> None:
        """Clear the displayed log"""
        self.state_text.clear()
    
    def closeEvent(self, event) -> None:
        """Handle window close"""
        self.refresh_timer.stop()
        self.closed.emit()
        super().closeEvent(event)
