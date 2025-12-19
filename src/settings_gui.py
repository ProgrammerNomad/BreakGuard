"""
Settings GUI for BreakGuard
User-friendly settings interface
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config_manager import ConfigManager
from windows_startup import WindowsStartup

class SettingsWindow:
    def __init__(self, on_save=None):
        self.on_save = on_save
        self.config = ConfigManager()
        
        self.root = tk.Toplevel()
        self.root.title("BreakGuard Settings")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # Colors
        self.bg_color = "#f5f5f5"
        self.accent_color = "#00a8ff"
        self.text_color = "#333333"
        
        self.root.configure(bg=self.bg_color)
        
        # Main container with scrollbar
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(
            main_frame,
            text="⚙️ Settings",
            font=("Helvetica", 20, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=(0, 20))
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self._create_general_tab()
        self._create_security_tab()
        self._create_tinxy_tab()
        self._create_about_tab()
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(
            button_frame,
            text="Cancel",
            font=("Helvetica", 11),
            bg="#e0e0e0",
            fg=self.text_color,
            padx=20,
            pady=8,
            command=self.root.destroy,
            cursor="hand2",
            relief=tk.FLAT
        ).pack(side=tk.LEFT)
        
        tk.Button(
            button_frame,
            text="Save Settings",
            font=("Helvetica", 11, "bold"),
            bg=self.accent_color,
            fg="white",
            padx=20,
            pady=8,
            command=self._save_settings,
            cursor="hand2",
            relief=tk.FLAT
        ).pack(side=tk.RIGHT)
    
    def _create_general_tab(self):
        """Create general settings tab"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="General")
        
        container = tk.Frame(tab, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Work interval
        self._create_setting_group(
            container,
            "Work Interval",
            "How long to work before taking a break"
        )
        
        interval_frame = tk.Frame(container, bg="white")
        interval_frame.pack(fill=tk.X, pady=5)
        
        self.work_interval_var = tk.IntVar(
            value=self.config.get('work_interval_minutes', 60)
        )
        
        tk.Label(
            interval_frame,
            text="Minutes:",
            font=("Helvetica", 10),
            bg="white"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Spinbox(
            interval_frame,
            from_=15,
            to=180,
            textvariable=self.work_interval_var,
            font=("Helvetica", 10),
            width=10
        ).pack(side=tk.LEFT)
        
        # Warning time
        self._create_setting_group(
            container,
            "Warning Time",
            "How much notice before screen locks"
        )
        
        warning_frame = tk.Frame(container, bg="white")
        warning_frame.pack(fill=tk.X, pady=5)
        
        self.warning_var = tk.IntVar(
            value=self.config.get('warning_before_minutes', 5)
        )
        
        tk.Label(
            warning_frame,
            text="Minutes:",
            font=("Helvetica", 10),
            bg="white"
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Spinbox(
            warning_frame,
            from_=1,
            to=30,
            textvariable=self.warning_var,
            font=("Helvetica", 10),
            width=10
        ).pack(side=tk.LEFT)
        
        # Auto-start
        self._create_setting_group(
            container,
            "Startup",
            "Run BreakGuard when Windows starts"
        )
        
        self.auto_start_var = tk.BooleanVar(
            value=self.config.get('auto_start', True)
        )
        
        tk.Checkbutton(
            container,
            text="Start with Windows",
            variable=self.auto_start_var,
            font=("Helvetica", 10),
            bg="white"
        ).pack(anchor=tk.W, pady=5)
    
    def _create_security_tab(self):
        """Create security settings tab"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="Security")
        
        container = tk.Frame(tab, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # TOTP
        self._create_setting_group(
            container,
            "Google Authenticator (TOTP)",
            "Two-factor authentication for unlocking"
        )
        
        self.auth_enabled_var = tk.BooleanVar(
            value=self.config.get('auth_enabled', True)
        )
        
        tk.Checkbutton(
            container,
            text="Enable TOTP authentication",
            variable=self.auth_enabled_var,
            font=("Helvetica", 10),
            bg="white"
        ).pack(anchor=tk.W, pady=5)
        
        if not self.config.get('totp_secret'):
            tk.Label(
                container,
                text="⚠️ TOTP not configured. Run setup wizard to configure.",
                font=("Helvetica", 9),
                bg="white",
                fg="#ff6b6b"
            ).pack(anchor=tk.W, pady=5)
        
        tk.Button(
            container,
            text="Reconfigure TOTP",
            font=("Helvetica", 9),
            bg=self.accent_color,
            fg="white",
            padx=15,
            pady=5,
            command=self._reconfigure_totp,
            cursor="hand2",
            relief=tk.FLAT
        ).pack(anchor=tk.W, pady=5)
        
        # Face verification
        self._create_setting_group(
            container,
            "Face Verification",
            "Verify your identity using your camera"
        )
        
        self.face_enabled_var = tk.BooleanVar(
            value=self.config.get('face_verification', True)
        )
        
        tk.Checkbutton(
            container,
            text="Enable face verification",
            variable=self.face_enabled_var,
            font=("Helvetica", 10),
            bg="white"
        ).pack(anchor=tk.W, pady=5)
        
        tk.Button(
            container,
            text="Re-register Face",
            font=("Helvetica", 9),
            bg="#9c88ff",
            fg="white",
            padx=15,
            pady=5,
            command=self._reregister_face,
            cursor="hand2",
            relief=tk.FLAT
        ).pack(anchor=tk.W, pady=5)
    
    def _create_tinxy_tab(self):
        """Create Tinxy API settings tab"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="Tinxy API")
        
        container = tk.Frame(tab, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self._create_setting_group(
            container,
            "Tinxy Smart Switch",
            "Control monitor power via Tinxy device"
        )
        
        # API Key
        tk.Label(
            container,
            text="API Key:",
            font=("Helvetica", 10),
            bg="white"
        ).pack(anchor=tk.W, pady=(10, 2))
        
        self.tinxy_api_var = tk.StringVar(
            value=self.config.get('tinxy_api_key', '')
        )
        
        tk.Entry(
            container,
            textvariable=self.tinxy_api_var,
            font=("Helvetica", 10),
            width=50,
            show="*"
        ).pack(anchor=tk.W, pady=2)
        
        # Device ID
        tk.Label(
            container,
            text="Device ID:",
            font=("Helvetica", 10),
            bg="white"
        ).pack(anchor=tk.W, pady=(10, 2))
        
        self.tinxy_device_var = tk.StringVar(
            value=self.config.get('tinxy_device_id', '')
        )
        
        tk.Entry(
            container,
            textvariable=self.tinxy_device_var,
            font=("Helvetica", 10),
            width=50
        ).pack(anchor=tk.W, pady=2)
        
        # Device Number
        tk.Label(
            container,
            text="Device Number:",
            font=("Helvetica", 10),
            bg="white"
        ).pack(anchor=tk.W, pady=(10, 2))
        
        self.tinxy_number_var = tk.IntVar(
            value=self.config.get('tinxy_device_number', 1)
        )
        
        tk.Spinbox(
            container,
            from_=1,
            to=8,
            textvariable=self.tinxy_number_var,
            font=("Helvetica", 10),
            width=10
        ).pack(anchor=tk.W, pady=2)
        
        # Test button
        tk.Button(
            container,
            text="Test Connection",
            font=("Helvetica", 9),
            bg=self.accent_color,
            fg="white",
            padx=15,
            pady=5,
            command=self._test_tinxy,
            cursor="hand2",
            relief=tk.FLAT
        ).pack(anchor=tk.W, pady=15)
        
        # Help
        tk.Label(
            container,
            text="ℹ️ How to get API credentials:\n"
                 "1. Open Tinxy mobile app\n"
                 "2. Go to Settings → API Token\n"
                 "3. Copy the token and device ID",
            font=("Helvetica", 9),
            bg="white",
            fg="#666666",
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=10)
    
    def _create_about_tab(self):
        """Create about tab"""
        tab = tk.Frame(self.notebook, bg="white")
        self.notebook.add(tab, text="About")
        
        container = tk.Frame(tab, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        tk.Label(
            container,
            text="BreakGuard",
            font=("Helvetica", 24, "bold"),
            bg="white",
            fg=self.accent_color
        ).pack(pady=(20, 5))
        
        tk.Label(
            container,
            text="Health-Discipline Application",
            font=("Helvetica", 12),
            bg="white",
            fg="#666666"
        ).pack(pady=5)
        
        tk.Label(
            container,
            text="Version 1.0.0",
            font=("Helvetica", 10),
            bg="white",
            fg="#666666"
        ).pack(pady=20)
        
        tk.Label(
            container,
            text='"If willpower was enough, reminders would work.\n'
                 'BreakGuard exists because discipline needs structure."',
            font=("Helvetica", 10, "italic"),
            bg="white",
            fg=self.text_color,
            justify=tk.CENTER
        ).pack(pady=20)
        
        tk.Label(
            container,
            text="MIT License\n"
                 "© 2025 ProgrammerNomad",
            font=("Helvetica", 9),
            bg="white",
            fg="#666666",
            justify=tk.CENTER
        ).pack(pady=10)
        
        tk.Button(
            container,
            text="Visit GitHub Repository",
            font=("Helvetica", 10),
            bg=self.accent_color,
            fg="white",
            padx=20,
            pady=8,
            command=lambda: self._open_url("https://github.com/ProgrammerNomad/BreakGuard"),
            cursor="hand2",
            relief=tk.FLAT
        ).pack(pady=20)
    
    def _create_setting_group(self, parent, title, description):
        """Create a setting group with title and description"""
        tk.Label(
            parent,
            text=title,
            font=("Helvetica", 12, "bold"),
            bg="white",
            fg=self.text_color
        ).pack(anchor=tk.W, pady=(20, 2))
        
        tk.Label(
            parent,
            text=description,
            font=("Helvetica", 9),
            bg="white",
            fg="#666666"
        ).pack(anchor=tk.W, pady=(0, 10))
    
    def _reconfigure_totp(self):
        """Reconfigure TOTP"""
        from setup_wizard_gui import SetupWizard
        messagebox.showinfo(
            "Reconfigure TOTP",
            "This will launch the setup wizard.\nPlease configure TOTP in the security step."
        )
    
    def _reregister_face(self):
        """Re-register face"""
        from face_verification import FaceVerification
        import threading
        
        def register():
            face_verif = FaceVerification()
            success = face_verif.register_face()
            
            if success:
                messagebox.showinfo("Success", "Face re-registered successfully!")
            else:
                messagebox.showerror("Error", "Face registration failed.")
        
        threading.Thread(target=register, daemon=True).start()
    
    def _test_tinxy(self):
        """Test Tinxy API connection"""
        from tinxy_api import TinxyAPI
        
        api_key = self.tinxy_api_var.get()
        device_id = self.tinxy_device_var.get()
        device_num = self.tinxy_number_var.get()
        
        if not api_key or not device_id:
            messagebox.showwarning(
                "Missing Information",
                "Please enter both API key and device ID"
            )
            return
        
        try:
            tinxy = TinxyAPI(api_key, device_id, device_num)
            devices = tinxy.get_all_devices()
            
            if devices is not None:
                messagebox.showinfo(
                    "Success",
                    f"Connected successfully!\nFound {len(devices)} device(s)"
                )
            else:
                messagebox.showerror(
                    "Connection Failed",
                    "Could not connect to Tinxy API.\nCheck your credentials."
                )
        except Exception as e:
            messagebox.showerror("Error", f"Connection error:\n{str(e)}")
    
    def _open_url(self, url):
        """Open URL in browser"""
        import webbrowser
        webbrowser.open(url)
    
    def _save_settings(self):
        """Save settings"""
        # Update config
        self.config.set('work_interval_minutes', self.work_interval_var.get())
        self.config.set('warning_before_minutes', self.warning_var.get())
        self.config.set('auto_start', self.auto_start_var.get())
        self.config.set('auth_enabled', self.auth_enabled_var.get())
        self.config.set('face_verification', self.face_enabled_var.get())
        self.config.set('tinxy_api_key', self.tinxy_api_var.get())
        self.config.set('tinxy_device_id', self.tinxy_device_var.get())
        self.config.set('tinxy_device_number', self.tinxy_number_var.get())
        
        # Save to file
        if self.config.save_config():
            # Update Windows startup
            if self.auto_start_var.get():
                WindowsStartup.enable()
            else:
                WindowsStartup.disable()
            
            messagebox.showinfo(
                "Settings Saved",
                "Your settings have been saved successfully!\n\n"
                "Note: Timer will restart with new intervals on next break cycle."
            )
            
            if self.on_save:
                self.on_save()
            
            self.root.destroy()
        else:
            messagebox.showerror(
                "Save Failed",
                "Could not save settings. Please try again."
            )
    
    def show(self):
        """Show the settings window"""
        self.root.grab_set()  # Make modal
        self.root.wait_window()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    settings = SettingsWindow()
    settings.show()
