"""
Warning Dialog (PyQt6)
Custom warning window shown before lock screen
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta

class WarningDialog(QDialog):
    """Warning dialog shown before break"""
    
    snooze_requested = pyqtSignal()
    
    def __init__(self, minutes_remaining: int, work_duration: int, can_snooze: bool = True):
        """Initialize warning dialog
        
        Args:
            minutes_remaining: Minutes until lock
            work_duration: Minutes worked so far
            can_snooze: Whether snooze is allowed
        """
        super().__init__()
        
        self.setWindowTitle("Break Time Approaching")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(400, 350)
        
        # Styling
        self.setStyleSheet("""
            QDialog {
                background-color: #fff3cd;
                border: 2px solid #ffeeba;
                border-radius: 10px;
            }
            QLabel {
                color: #856404;
            }
            QPushButton {
                background-color: #ffc107;
                color: #000;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ffca2c;
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #999;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        icon_label = QLabel("⚠️")
        icon_label.setFont(QFont("Segoe UI", 24))
        header_layout.addWidget(icon_label)
        
        title_label = QLabel("Break Time Approaching")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Message
        msg_label = QLabel(f"Your screen will lock in {minutes_remaining} minutes.")
        msg_label.setFont(QFont("Segoe UI", 12))
        layout.addWidget(msg_label)
        
        # Info
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.5);
                border-radius: 5px;
            }
            QLabel {
                color: #856404;
                background-color: transparent;
                border: none;
                font-family: "Segoe UI";
                font-size: 14px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(10, 10, 10, 10)
        info_layout.setSpacing(5)
        
        next_break = datetime.now() + timedelta(minutes=minutes_remaining)
        
        info_layout.addWidget(QLabel(f"Time worked: {work_duration} minutes"))
        info_layout.addWidget(QLabel(f"Next break at: {next_break.strftime('%I:%M %p')}"))
        info_layout.addWidget(QLabel("Save your work now!"))
        
        layout.addWidget(info_frame)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.snooze_btn = QPushButton("Snooze 5 min")
        self.snooze_btn.clicked.connect(self._on_snooze)
        if not can_snooze:
            self.snooze_btn.setEnabled(False)
            self.snooze_btn.setToolTip("Max snooze limit reached")
        
        btn_layout.addWidget(self.snooze_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setStyleSheet("background-color: #28a745; color: white;")
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        
        # Auto-close timer (close if user doesn't respond before lock)
        self.close_timer = QTimer()
        self.close_timer.timeout.connect(self.accept)
        self.close_timer.start(minutes_remaining * 60 * 1000)
    
    def _on_snooze(self):
        """Handle snooze button"""
        self.snooze_requested.emit()
        self.accept()

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    dialog = WarningDialog(5, 60, True)
    dialog.show()
    sys.exit(app.exec())
