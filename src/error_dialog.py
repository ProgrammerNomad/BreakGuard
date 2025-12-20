"""
Reusable Error Dialog Component
User-friendly error messages with retry/report options
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from theme.theme import load_stylesheet
import logging

logger = logging.getLogger(__name__)


class ErrorDialog(QDialog):
    """User-friendly error dialog"""
    
    retry_requested = pyqtSignal()
    
    def __init__(self, title: str, message: str, details: str = None, 
                 allow_retry: bool = False, parent=None):
        """Initialize error dialog
        
        Args:
            title: Error title (e.g., "Connection Failed")
            message: User-friendly error message
            details: Technical details (optional, shown in expandable section)
            allow_retry: Whether to show retry button
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.setWindowTitle(f"BreakGuard - {title}")
        self.setMinimumSize(400, 250)
        self.setMaximumSize(600, 500)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
        
        self.setStyleSheet(load_stylesheet())
        self.allow_retry = allow_retry
        self.details = details
        
        self._setup_ui(title, message)
    
    def _setup_ui(self, title: str, message: str):
        """Setup error dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with icon
        header_layout = QHBoxLayout()
        icon_label = QLabel("❌")
        icon_label.setFont(QFont("Segoe UI", 32))
        header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setProperty("class", "h2")
        title_label.setStyleSheet("color: #dc3545; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Message
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setProperty("class", "body")
        layout.addWidget(msg_label)
        
        # Details section (expandable)
        if self.details:
            self.details_frame = QFrame()
            self.details_frame.setProperty("class", "card")
            self.details_frame.setVisible(False)
            details_layout = QVBoxLayout(self.details_frame)
            
            details_title = QLabel("Technical Details:")
            details_title.setProperty("class", "text-secondary")
            details_title.setStyleSheet("font-weight: bold;")
            details_layout.addWidget(details_title)
            
            self.details_text = QTextEdit()
            self.details_text.setReadOnly(True)
            self.details_text.setPlainText(self.details)
            self.details_text.setMaximumHeight(150)
            self.details_text.setProperty("class", "monospace")
            details_layout.addWidget(self.details_text)
            
            layout.addWidget(self.details_frame)
            
            # Toggle details button
            self.toggle_btn = QPushButton("Show Details")
            self.toggle_btn.setProperty("class", "secondary")
            self.toggle_btn.clicked.connect(self._toggle_details)
            layout.addWidget(self.toggle_btn)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        if self.allow_retry:
            retry_btn = QPushButton("&Retry")
            retry_btn.setMinimumWidth(100)
            retry_btn.setProperty("class", "primary-btn")
            retry_btn.setShortcut("Alt+R")
            retry_btn.clicked.connect(self._on_retry)
            btn_layout.addWidget(retry_btn)
        
        close_btn = QPushButton("&Close")
        close_btn.setMinimumWidth(100)
        close_btn.setProperty("class", "secondary-btn")
        close_btn.setShortcut("Alt+C")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def _toggle_details(self):
        """Toggle details visibility"""
        is_visible = self.details_frame.isVisible()
        self.details_frame.setVisible(not is_visible)
        self.toggle_btn.setText("Hide Details" if not is_visible else "Show Details")
        
        # Resize dialog
        if not is_visible:
            self.setMinimumHeight(400)
        else:
            self.setMinimumHeight(250)
    
    def _on_retry(self):
        """Handle retry button"""
        self.retry_requested.emit()
        self.accept()


def show_error(title: str, message: str, details: str = None, 
               allow_retry: bool = False, parent=None):
    """Show error dialog (convenience function)
    
    Args:
        title: Error title
        message: User-friendly message
        details: Technical details (optional)
        allow_retry: Whether to show retry button
        parent: Parent widget
        
    Returns:
        True if retry requested, False otherwise
    """
    dialog = ErrorDialog(title, message, details, allow_retry, parent)
    
    retry_requested = [False]
    
    def on_retry():
        retry_requested[0] = True
    
    dialog.retry_requested.connect(on_retry)
    dialog.exec()
    
    return retry_requested[0]


# Example usage
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Test error dialog
    show_error(
        "Connection Failed",
        "Could not connect to Tinxy API. Please check your internet connection and API credentials.",
        details="requests.exceptions.ConnectionError: HTTPSConnectionPool(host='cloud.tinxy.in', port=443): Max retries exceeded",
        allow_retry=True
    )
    
    sys.exit(0)
