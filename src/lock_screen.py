"""
Fullscreen Lock Screen for BreakGuard
Always-on-top lock with TOTP and Face verification
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Callable, Optional
from datetime import datetime

class LockScreen:
    def __init__(self, 
                 totp_auth,
                 face_verification,
                 on_unlock: Optional[Callable] = None,
                 auth_enabled: bool = True,
                 face_enabled: bool = True):
        
        self.totp_auth = totp_auth
        self.face_verification = face_verification
        self.on_unlock = on_unlock
        self.auth_enabled = auth_enabled
        self.face_enabled = face_enabled
        
        self.root = None
        self.is_locked = False
        self.unlock_attempts = 0
        self.max_attempts = 5
        
        # Create UI
        self._create_ui()
    
    def _create_ui(self):
        """Create the lock screen UI"""
        self.root = tk.Tk()
        self.root.title("BreakGuard - Break Time")
        
        # Make fullscreen and always on top
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        
        # Disable Alt+F4
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_attempt)
        
        # Dark theme colors
        bg_color = "#1a1a1a"
        fg_color = "#ffffff"
        accent_color = "#00a8ff"
        error_color = "#ff4757"
        
        self.root.configure(bg=bg_color)
        
        # Main container
        main_frame = tk.Frame(self.root, bg=bg_color)
        main_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        title = tk.Label(
            main_frame,
            text="⏸ BREAK TIME",
            font=("Helvetica", 48, "bold"),
            bg=bg_color,
            fg=accent_color
        )
        title.pack(pady=20)
        
        # Message
        message = tk.Label(
            main_frame,
            text="Time to take a break and rest your eyes",
            font=("Helvetica", 18),
            bg=bg_color,
            fg=fg_color
        )
        message.pack(pady=10)
        
        # Current time
        self.time_label = tk.Label(
            main_frame,
            text="",
            font=("Helvetica", 24, "bold"),
            bg=bg_color,
            fg=fg_color
        )
        self.time_label.pack(pady=20)
        
        # Separator
        separator = tk.Frame(main_frame, height=2, bg=accent_color)
        separator.pack(fill=tk.X, padx=50, pady=20)
        
        # Authentication section
        auth_frame = tk.Frame(main_frame, bg=bg_color)
        auth_frame.pack(pady=20)
        
        if self.auth_enabled:
            # TOTP Section
            totp_label = tk.Label(
                auth_frame,
                text="Enter Google Authenticator Code:",
                font=("Helvetica", 14),
                bg=bg_color,
                fg=fg_color
            )
            totp_label.pack(pady=5)
            
            self.totp_entry = tk.Entry(
                auth_frame,
                font=("Helvetica", 24),
                width=10,
                justify=tk.CENTER,
                bg="#2d2d2d",
                fg=fg_color,
                insertbackground=fg_color
            )
            self.totp_entry.pack(pady=10)
            self.totp_entry.focus()
            
            # Bind Enter key
            self.totp_entry.bind('<Return>', lambda e: self._verify_totp())
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg=bg_color)
        buttons_frame.pack(pady=20)
        
        if self.auth_enabled:
            verify_btn = tk.Button(
                buttons_frame,
                text="Verify Code",
                font=("Helvetica", 14, "bold"),
                bg=accent_color,
                fg="#ffffff",
                padx=30,
                pady=10,
                command=self._verify_totp,
                cursor="hand2"
            )
            verify_btn.pack(side=tk.LEFT, padx=10)
        
        if self.face_enabled:
            face_btn = tk.Button(
                buttons_frame,
                text="Verify Face",
                font=("Helvetica", 14, "bold"),
                bg="#9c88ff",
                fg="#ffffff",
                padx=30,
                pady=10,
                command=self._start_face_verification,
                cursor="hand2"
            )
            face_btn.pack(side=tk.LEFT, padx=10)
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="",
            font=("Helvetica", 12),
            bg=bg_color,
            fg=error_color
        )
        self.status_label.pack(pady=10)
        
        # Attempts counter
        self.attempts_label = tk.Label(
            main_frame,
            text="",
            font=("Helvetica", 10),
            bg=bg_color,
            fg=fg_color
        )
        self.attempts_label.pack(pady=5)
        
        # Instructions
        instructions = tk.Label(
            main_frame,
            text="Complete verification to unlock and continue working",
            font=("Helvetica", 10),
            bg=bg_color,
            fg="#888888"
        )
        instructions.pack(pady=20)
        
        # Prevent keyboard shortcuts
        self._block_shortcuts()
        
        # Start time update loop
        self._update_time()
    
    def _block_shortcuts(self):
        """Block common keyboard shortcuts"""
        shortcuts = [
            '<Alt-F4>',
            '<Control-Alt-Delete>',
            '<Alt-Tab>',
            '<Control-Escape>',
            '<Super_L>',
            '<Super_R>',
            '<F1>', '<F2>', '<F3>', '<F4>', '<F5>', '<F6>',
            '<F7>', '<F8>', '<F9>', '<F10>', '<F11>', '<F12>'
        ]
        
        for shortcut in shortcuts:
            self.root.bind(shortcut, lambda e: "break")
    
    def _update_time(self):
        """Update current time display"""
        if self.root and self.is_locked:
            current_time = datetime.now().strftime("%I:%M:%S %p")
            self.time_label.config(text=current_time)
            self.root.after(1000, self._update_time)
    
    def _on_close_attempt(self):
        """Handle window close attempts"""
        self.status_label.config(
            text="You must complete verification to unlock",
            fg="#ff4757"
        )
    
    def _verify_totp(self):
        """Verify TOTP code"""
        if not self.auth_enabled:
            self._proceed_to_face_or_unlock()
            return
        
        code = self.totp_entry.get().strip()
        
        if not code:
            self.status_label.config(text="Please enter a code", fg="#ff4757")
            return
        
        if self.totp_auth.verify_code(code):
            self.status_label.config(text="✓ Code verified!", fg="#2ed573")
            self.totp_entry.config(state=tk.DISABLED)
            
            # Proceed to face verification or unlock
            self.root.after(500, self._proceed_to_face_or_unlock)
        else:
            self.unlock_attempts += 1
            remaining = self.max_attempts - self.unlock_attempts
            
            self.status_label.config(
                text=f"✗ Invalid code. Try again.",
                fg="#ff4757"
            )
            
            self.attempts_label.config(
                text=f"Attempts remaining: {remaining}"
            )
            
            self.totp_entry.delete(0, tk.END)
            
            if self.unlock_attempts >= self.max_attempts:
                self.status_label.config(
                    text="Maximum attempts reached. Take a longer break.",
                    fg="#ff4757"
                )
                self.totp_entry.config(state=tk.DISABLED)
    
    def _proceed_to_face_or_unlock(self):
        """Proceed to face verification or unlock directly"""
        if self.face_enabled and self.face_verification.is_registered():
            self.status_label.config(
                text="Please complete face verification",
                fg="#00a8ff"
            )
        else:
            self._unlock()
    
    def _start_face_verification(self):
        """Start face verification in a separate thread"""
        self.status_label.config(text="Starting camera...", fg="#00a8ff")
        
        # Run face verification in background thread
        threading.Thread(
            target=self._verify_face_thread,
            daemon=True
        ).start()
    
    def _verify_face_thread(self):
        """Face verification in background thread"""
        # Temporarily hide window for camera access
        self.root.withdraw()
        
        try:
            is_verified, similarity = self.face_verification.verify_face()
            
            # Show window again
            self.root.deiconify()
            self.root.lift()
            self.root.attributes('-topmost', True)
            
            if is_verified:
                self.status_label.config(
                    text=f"✓ Face verified! ({similarity:.1%} match)",
                    fg="#2ed573"
                )
                self.root.after(1000, self._unlock)
            else:
                self.unlock_attempts += 1
                remaining = self.max_attempts - self.unlock_attempts
                
                self.status_label.config(
                    text=f"✗ Face verification failed",
                    fg="#ff4757"
                )
                
                self.attempts_label.config(
                    text=f"Attempts remaining: {remaining}"
                )
                
                if self.unlock_attempts >= self.max_attempts:
                    self.status_label.config(
                        text="Maximum attempts reached. Take a longer break.",
                        fg="#ff4757"
                    )
        except Exception as e:
            self.root.deiconify()
            self.root.lift()
            self.status_label.config(
                text=f"Error: {str(e)}",
                fg="#ff4757"
            )
    
    def _unlock(self):
        """Unlock and close the lock screen"""
        self.is_locked = False
        
        if self.on_unlock:
            self.on_unlock()
        
        self.root.quit()
        self.root.destroy()
    
    def show(self):
        """Show the lock screen"""
        self.is_locked = True
        
        # Try to close Task Manager if it's running
        self._close_task_manager()
        
        self.root.mainloop()
    
    def _close_task_manager(self):
        """Attempt to close Task Manager"""
        try:
            import subprocess
            subprocess.run(
                ['taskkill', '/F', '/IM', 'taskmgr.exe'],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
        except:
            pass

# Simplified version for testing
class SimpleLockScreen:
    """Simplified lock screen for testing without authentication"""
    
    def __init__(self, on_unlock: Optional[Callable] = None):
        self.on_unlock = on_unlock
        self.root = None
    
    def show(self):
        """Show simple lock screen"""
        self.root = tk.Tk()
        self.root.title("BreakGuard - Break Time")
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        
        bg_color = "#1a1a1a"
        
        self.root.configure(bg=bg_color)
        
        frame = tk.Frame(self.root, bg=bg_color)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        title = tk.Label(
            frame,
            text="⏸ BREAK TIME",
            font=("Helvetica", 48, "bold"),
            bg=bg_color,
            fg="#00a8ff"
        )
        title.pack(pady=20)
        
        message = tk.Label(
            frame,
            text="Take a break and rest your eyes",
            font=("Helvetica", 18),
            bg=bg_color,
            fg="#ffffff"
        )
        message.pack(pady=20)
        
        unlock_btn = tk.Button(
            frame,
            text="Unlock (Test Mode)",
            font=("Helvetica", 14),
            command=self._unlock,
            padx=30,
            pady=10
        )
        unlock_btn.pack(pady=20)
        
        self.root.mainloop()
    
    def _unlock(self):
        if self.on_unlock:
            self.on_unlock()
        self.root.quit()
        self.root.destroy()
