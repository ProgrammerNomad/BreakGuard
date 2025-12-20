"""
Warning Dialog (PyQt6)
Custom warning window shown before lock screen
"""

from __future__ import annotations
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta
from theme.theme import load_stylesheet

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
        self.setMinimumSize(400, 350)
        self.setMaximumSize(600, 500)
        
        self.setStyleSheet(load_stylesheet())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        icon_label = QLabel("⚠️")
        icon_label.setFont(QFont("Segoe UI", 24))
        header_layout.addWidget(icon_label)
        
        title_label = QLabel("Break Time Approaching")
        title_label.setProperty("class", "h2")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Message
        msg_label = QLabel(f"Your screen will lock in {minutes_remaining} minutes.")
        msg_label.setProperty("class", "body")
        layout.addWidget(msg_label)
        
        # Info
        info_frame = QFrame()
        info_frame.setProperty("class", "card")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(15, 15, 15, 15)
        info_layout.setSpacing(5)
        
        next_break = datetime.now() + timedelta(minutes=minutes_remaining)
        
        info_layout.addWidget(QLabel(f"Time worked: {work_duration} minutes"))
        info_layout.addWidget(QLabel(f"Next break at: {next_break.strftime('%I:%M %p')}"))
        
        save_label = QLabel("Save your work now!")
        save_label.setProperty("class", "text-danger")
        save_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        info_layout.addWidget(save_label)
        
        layout.addWidget(info_frame)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.snooze_btn = QPushButton("&Snooze 5 min")
        self.snooze_btn.setMinimumWidth(100)
        self.snooze_btn.setProperty("class", "secondary-btn")
        self.snooze_btn.setAccessibleName("Snooze 5 minutes button")
        self.snooze_btn.setToolTip("Delay the break by 5 minutes (Alt+S)")
        self.snooze_btn.setShortcut("Alt+S")
        self.snooze_btn.clicked.connect(self._on_snooze)
        if not can_snooze:
            self.snooze_btn.setEnabled(False)
            self.snooze_btn.setToolTip("Max snooze limit reached")
        
        btn_layout.addWidget(self.snooze_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.setMinimumWidth(100)
        ok_btn.setProperty("class", "primary-btn")
        ok_btn.setAccessibleName("OK button")
        ok_btn.setToolTip("Acknowledge warning")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        
        # Auto-close timer (close if user doesn't respond before lock)
        self.close_timer = QTimer()
        self.close_timer.timeout.connect(self.accept)
        self.close_timer.start(minutes_remaining * 60 * 1000)
        
        # Fade-in animation
        self.setWindowOpacity(0)
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(400)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_animation.start()
    
    def _on_snooze(self):
        """Handle snooze button"""
        self.snooze_requested.emit()
        self._fade_out_and_close()
    
    def accept(self):
        """Override accept to add fade-out animation"""
        self._fade_out_and_close()
    
    def _fade_out_and_close(self):
        """Fade out and close dialog"""
        fade_out = QPropertyAnimation(self, b"windowOpacity")
        fade_out.setDuration(300)
        fade_out.setStartValue(1)
        fade_out.setEndValue(0)
        fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
        fade_out.finished.connect(lambda: super(WarningDialog, self).accept())
        fade_out.start()
        self.fade_out_animation = fade_out  # Keep reference

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    dialog = WarningDialog(5, 60, True)
    dialog.show()
    sys.exit(app.exec())
