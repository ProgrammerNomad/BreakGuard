"""
Setup Wizard GUI for BreakGuard
User-friendly first-time setup for non-technical users
"""
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
from pathlib import Path

class SetupWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BreakGuard Setup Wizard")
        self.root.geometry("700x550")
        self.root.resizable(False, False)
        
        # Colors
        self.bg_color = "#f5f5f5"
        self.accent_color = "#00a8ff"
        self.text_color = "#333333"
        
        self.root.configure(bg=self.bg_color)
        
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
        
        # Steps
        self.steps = [
            self._create_welcome_step,
            self._create_interval_step,
            self._create_totp_step,
            self._create_face_step,
            self._create_tinxy_step,
            self._create_completion_step
        ]
        
        # Main container
        self.container = tk.Frame(self.root, bg=self.bg_color)
        self.container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Progress bar at top
        self._create_progress_bar()
        
        # Content frame
        self.content_frame = tk.Frame(self.container, bg=self.bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Navigation buttons
        self._create_navigation()
        
        # Show first step
        self._show_step(0)
    
    def _create_progress_bar(self):
        """Create progress indicator"""
        progress_frame = tk.Frame(self.container, bg=self.bg_color)
        progress_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.progress = ttk.Progressbar(
            progress_frame,
            length=640,
            mode='determinate',
            maximum=len(self.steps)
        )
        self.progress.pack()
        self.progress['value'] = 1
    
    def _create_navigation(self):
        """Create navigation buttons"""
        nav_frame = tk.Frame(self.container, bg=self.bg_color)
        nav_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.back_btn = tk.Button(
            nav_frame,
            text="← Back",
            font=("Helvetica", 11),
            bg="#e0e0e0",
            fg=self.text_color,
            padx=20,
            pady=8,
            command=self._go_back,
            cursor="hand2",
            relief=tk.FLAT
        )
        self.back_btn.pack(side=tk.LEFT)
        
        self.next_btn = tk.Button(
            nav_frame,
            text="Next →",
            font=("Helvetica", 11, "bold"),
            bg=self.accent_color,
            fg="white",
            padx=20,
            pady=8,
            command=self._go_next,
            cursor="hand2",
            relief=tk.FLAT
        )
        self.next_btn.pack(side=tk.RIGHT)
    
    def _show_step(self, step_num):
        """Show a specific step"""
        # Clear content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Update progress
        self.progress['value'] = step_num + 1
        
        # Update buttons
        if step_num == 0:
            self.back_btn.config(state=tk.DISABLED)
        else:
            self.back_btn.config(state=tk.NORMAL)
        
        if step_num == len(self.steps) - 1:
            self.next_btn.config(text="Finish")
        else:
            self.next_btn.config(text="Next →")
        
        # Show step content
        self.steps[step_num]()
    
    def _go_next(self):
        """Go to next step"""
        if self.current_step < len(self.steps) - 1:
            # Validate current step
            if self._validate_step(self.current_step):
                self.current_step += 1
                self._show_step(self.current_step)
        else:
            # Finish setup
            self._finish_setup()
    
    def _go_back(self):
        """Go to previous step"""
        if self.current_step > 0:
            self.current_step -= 1
            self._show_step(self.current_step)
    
    def _validate_step(self, step_num):
        """Validate step before proceeding"""
        # Step 2 is TOTP setup
        if step_num == 2 and self.totp_enabled_var.get():
            if not hasattr(self, 'totp_auth') or self.totp_auth is None:
                messagebox.showwarning(
                    "Setup Required",
                    "Please click 'Generate QR Code' to set up Google Authenticator."
                )
                return False
            
            if not hasattr(self, 'totp_verified') or not self.totp_verified:
                messagebox.showwarning(
                    "Verification Required",
                    "Please verify your TOTP setup by entering the 6-digit code from Google Authenticator app.\n\n"
                    "This ensures your authentication is working correctly!"
                )
                return False
        
        return True
    
    def _create_welcome_step(self):
        """Welcome screen"""
        tk.Label(
            self.content_frame,
            text="Welcome to BreakGuard! 👋",
            font=("Helvetica", 24, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=(40, 20))
        
        tk.Label(
            self.content_frame,
            text="Take control of your health with automated break enforcement",
            font=("Helvetica", 12),
            bg=self.bg_color,
            fg="#666666"
        ).pack(pady=(0, 30))
        
        # Features list
        features = [
            "⏱️ Automatic break reminders based on your schedule",
            "🔒 Secure two-step authentication (Google Authenticator + Face)",
            "🖥️ Smart monitor control via Tinxy API",
            "🔄 Survives system restarts and power failures",
            "🚀 Auto-starts with Windows"
        ]
        
        for feature in features:
            tk.Label(
                self.content_frame,
                text=feature,
                font=("Helvetica", 11),
                bg=self.bg_color,
                fg=self.text_color,
                anchor=tk.W
            ).pack(anchor=tk.W, pady=5, padx=50)
        
        tk.Label(
            self.content_frame,
            text="\nThis wizard will guide you through the setup process.\nIt only takes 2-3 minutes!",
            font=("Helvetica", 10),
            bg=self.bg_color,
            fg="#666666",
            justify=tk.CENTER
        ).pack(pady=(30, 0))
    
    def _create_interval_step(self):
        """Configure work intervals"""
        tk.Label(
            self.content_frame,
            text="Configure Your Work Schedule",
            font=("Helvetica", 18, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=(20, 10))
        
        tk.Label(
            self.content_frame,
            text="Set how long you want to work before taking a break",
            font=("Helvetica", 10),
            bg=self.bg_color,
            fg="#666666"
        ).pack(pady=(0, 30))
        
        # Work interval
        interval_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        interval_frame.pack(pady=10)
        
        tk.Label(
            interval_frame,
            text="Work interval (minutes):",
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.work_interval_var = tk.IntVar(value=60)
        work_spinbox = tk.Spinbox(
            interval_frame,
            from_=15,
            to=180,
            textvariable=self.work_interval_var,
            font=("Helvetica", 11),
            width=10
        )
        work_spinbox.pack(side=tk.LEFT)
        
        # Warning time
        warning_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        warning_frame.pack(pady=10)
        
        tk.Label(
            warning_frame,
            text="Warning before lock (minutes):",
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.warning_var = tk.IntVar(value=5)
        warning_spinbox = tk.Spinbox(
            warning_frame,
            from_=1,
            to=30,
            textvariable=self.warning_var,
            font=("Helvetica", 11),
            width=10
        )
        warning_spinbox.pack(side=tk.LEFT)
        
        # Recommendations
        tk.Label(
            self.content_frame,
            text="\n💡 Recommended Settings:",
            font=("Helvetica", 10, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=(30, 5))
        
        recommendations = [
            "• 60 minutes: Standard (20-20-20 rule compliant)",
            "• 90 minutes: Extended focus sessions",
            "• 30 minutes: Frequent breaks for eye health"
        ]
        
        for rec in recommendations:
            tk.Label(
                self.content_frame,
                text=rec,
                font=("Helvetica", 9),
                bg=self.bg_color,
                fg="#666666",
                anchor=tk.W
            ).pack(anchor=tk.W, padx=80)
    
    def _create_totp_step(self):
        """Setup Google Authenticator"""
        tk.Label(
            self.content_frame,
            text="Setup Google Authenticator 🔐",
            font=("Helvetica", 18, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=(20, 10))
        
        tk.Label(
            self.content_frame,
            text="Secure your breaks with two-factor authentication",
            font=("Helvetica", 10),
            bg=self.bg_color,
            fg="#666666"
        ).pack(pady=(0, 20))
        
        # Enable TOTP checkbox
        self.totp_enabled_var = tk.BooleanVar(value=True)
        totp_check = tk.Checkbutton(
            self.content_frame,
            text="Enable Google Authenticator",
            variable=self.totp_enabled_var,
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.text_color,
            command=self._toggle_totp_setup
        )
        totp_check.pack(pady=10)
        
        # TOTP setup frame
        self.totp_setup_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        self.totp_setup_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Generate TOTP button
        self.generate_totp_btn = tk.Button(
            self.totp_setup_frame,
            text="Generate QR Code",
            font=("Helvetica", 11, "bold"),
            bg=self.accent_color,
            fg="white",
            padx=20,
            pady=10,
            command=self._generate_totp,
            cursor="hand2",
            relief=tk.FLAT
        )
        self.generate_totp_btn.pack(pady=10)
        
        # QR code display area with border for visibility
        qr_container = tk.Frame(
            self.totp_setup_frame,
            bg="white",
            relief=tk.SOLID,
            borderwidth=2,
            width=360,
            height=360
        )
        qr_container.pack(pady=10)
        qr_container.pack_propagate(False)  # Prevent resizing
        
        self.qr_label = tk.Label(qr_container, bg="white")
        self.qr_label.pack(expand=True)
        
        # Instructions
        self.totp_instructions = tk.Label(
            self.totp_setup_frame,
            text="",
            font=("Helvetica", 9),
            bg=self.bg_color,
            fg="#666666",
            justify=tk.LEFT
        )
        self.totp_instructions.pack(pady=10)
        
        # Verification section (initially hidden)
        self.verify_frame = tk.Frame(self.totp_setup_frame, bg=self.bg_color)
        
        tk.Label(
            self.verify_frame,
            text="🔐 Verify Setup - Enter code from your app:",
            font=("Helvetica", 11, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=(20, 5))
        
        verify_input_frame = tk.Frame(self.verify_frame, bg=self.bg_color)
        verify_input_frame.pack(pady=10)
        
        self.verify_code_entry = tk.Entry(
            verify_input_frame,
            font=("Helvetica", 18),
            width=10,
            justify=tk.CENTER
        )
        self.verify_code_entry.pack(side=tk.LEFT, padx=5)
        
        self.verify_btn = tk.Button(
            verify_input_frame,
            text="Verify",
            font=("Helvetica", 11, "bold"),
            bg=self.accent_color,
            fg="white",
            padx=20,
            pady=8,
            command=self._verify_totp_code,
            cursor="hand2",
            relief=tk.FLAT
        )
        self.verify_btn.pack(side=tk.LEFT, padx=5)
        
        self.verify_status = tk.Label(
            self.verify_frame,
            text="",
            font=("Helvetica", 10),
            bg=self.bg_color
        )
        self.verify_status.pack(pady=5)
        
        tk.Label(
            self.verify_frame,
            text="💡 The code changes every 30 seconds",
            font=("Helvetica", 8),
            bg=self.bg_color,
            fg="#666666"
        ).pack(pady=2)
    
    def _toggle_totp_setup(self):
        """Toggle TOTP setup visibility"""
        if self.totp_enabled_var.get():
            self.totp_setup_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        else:
            self.totp_setup_frame.pack_forget()
    
    def _generate_totp(self):
        """Generate TOTP QR code"""
        from totp_auth import TOTPAuth
        
        self.generate_totp_btn.config(state=tk.DISABLED, text="Generating...")
        
        def generate():
            self.totp_auth = TOTPAuth()
            qr_img = self.totp_auth.generate_qr_code()

            base_size = 280
            canvas_size = 320
            qr_img = qr_img.convert("RGB").resize(
                (base_size, base_size),
                Image.Resampling.NEAREST
            )
            canvas = Image.new("RGB", (canvas_size, canvas_size), "white")
            offset = (canvas_size - base_size) // 2
            canvas.paste(qr_img, (offset, offset))
            
            photo = ImageTk.PhotoImage(canvas)
            self.root.after(0, lambda: self._display_qr_code(photo))
        
        threading.Thread(target=generate, daemon=True).start()
    
    def _display_qr_code(self, photo):
        """Display QR code"""
        self.qr_label.config(image=photo)
        self.qr_label.image = photo  # Keep reference
        self.generate_totp_btn.config(state=tk.NORMAL, text="Regenerate QR Code")
        
        instructions = """
✓ QR Code Generated!

1. Install Google Authenticator on your phone
2. Open the app and tap the '+' button
3. Select 'Scan a QR code'
4. Point your camera at the code above
5. A 6-digit code will appear in the app

Secret Key (for manual entry if QR scan fails):
{}

Save this secret key somewhere safe!
        """.format(self.totp_auth.get_secret() if self.totp_auth else "")
        
        self.totp_instructions.config(text=instructions)
        self.config_data['totp_secret'] = self.totp_auth.get_secret()
        
        # Show verification section
        self.verify_frame.pack(fill=tk.BOTH, pady=20)
        self.totp_verified = False
    
    def _verify_totp_code(self):
        """Verify the TOTP code entered by user"""
        if not self.totp_auth:
            self.verify_status.config(
                text="❌ Please generate QR code first",
                fg="#ff4757"
            )
            return
        
        code = self.verify_code_entry.get().strip()
        
        if not code:
            self.verify_status.config(
                text="❌ Please enter the 6-digit code",
                fg="#ff4757"
            )
            return
        
        # Verify the code
        if self.totp_auth.verify_code(code):
            self.verify_status.config(
                text="✅ Verified! Google Authenticator is connected correctly!",
                fg="#2ed573"
            )
            self.verify_btn.config(state=tk.DISABLED, bg="#2ed573")
            self.verify_code_entry.config(state=tk.DISABLED)
            self.totp_verified = True
            
            # Auto-advance after 1.5 seconds
            self.root.after(1500, lambda: self._go_next() if self.current_step == 2 else None)
        else:
            self.verify_status.config(
                text="❌ Invalid code. Make sure you scanned the correct QR code.",
                fg="#ff4757"
            )
            self.verify_code_entry.delete(0, tk.END)
            self.totp_verified = False
    
    def _create_face_step(self):
        """Setup face verification"""
        tk.Label(
            self.content_frame,
            text="Setup Face Verification 👤",
            font=("Helvetica", 18, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=(20, 10))
        
        tk.Label(
            self.content_frame,
            text="Add an extra layer of security with face recognition",
            font=("Helvetica", 10),
            bg=self.bg_color,
            fg="#666666"
        ).pack(pady=(0, 20))
        
        # Enable face verification checkbox
        self.face_enabled_var = tk.BooleanVar(value=True)
        face_check = tk.Checkbutton(
            self.content_frame,
            text="Enable Face Verification",
            variable=self.face_enabled_var,
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.text_color,
            command=self._toggle_face_setup
        )
        face_check.pack(pady=10)
        
        # Face setup frame
        self.face_setup_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        self.face_setup_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        tk.Label(
            self.face_setup_frame,
            text="📸 We'll take a photo of your face for verification",
            font=("Helvetica", 10),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=10)
        
        # Register face button
        self.register_face_btn = tk.Button(
            self.face_setup_frame,
            text="Capture My Face",
            font=("Helvetica", 11, "bold"),
            bg="#9c88ff",
            fg="white",
            padx=20,
            pady=10,
            command=self._register_face,
            cursor="hand2",
            relief=tk.FLAT
        )
        self.register_face_btn.pack(pady=10)
        
        self.face_status = tk.Label(
            self.face_setup_frame,
            text="",
            font=("Helvetica", 10),
            bg=self.bg_color,
            fg=self.text_color
        )
        self.face_status.pack(pady=10)
        
        # Privacy note
        tk.Label(
            self.face_setup_frame,
            text="🔒 Your face data stays on your computer and is never uploaded",
            font=("Helvetica", 9),
            bg=self.bg_color,
            fg="#666666"
        ).pack(pady=(20, 0))
    
    def _toggle_face_setup(self):
        """Toggle face setup visibility"""
        if self.face_enabled_var.get():
            self.face_setup_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        else:
            self.face_setup_frame.pack_forget()
    
    def _register_face(self):
        """Register face"""
        from face_verification import FaceVerification
        
        self.register_face_btn.config(state=tk.DISABLED, text="Opening camera...")
        
        def register():
            self.face_verif = FaceVerification()
            success = self.face_verif.register_face()
            
            # Update UI
            if success:
                self.root.after(0, lambda: self.face_status.config(
                    text="✓ Face registered successfully!",
                    fg="#2ed573"
                ))
            else:
                self.root.after(0, lambda: self.face_status.config(
                    text="✗ Face registration failed. Try again.",
                    fg="#ff4757"
                ))
                self.root.after(0, lambda: self.register_face_btn.config(
                    state=tk.NORMAL,
                    text="Capture My Face"
                ))
        
        threading.Thread(target=register, daemon=True).start()
    
    def _create_tinxy_step(self):
        """Setup Tinxy API (optional)"""
        tk.Label(
            self.content_frame,
            text="Tinxy Smart Switch (Optional) 🔌",
            font=("Helvetica", 18, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=(20, 10))
        
        tk.Label(
            self.content_frame,
            text="Control your monitor power via Tinxy smart switch",
            font=("Helvetica", 10),
            bg=self.bg_color,
            fg="#666666"
        ).pack(pady=(0, 20))
        
        # Enable Tinxy checkbox
        self.tinxy_enabled_var = tk.BooleanVar(value=False)
        tinxy_check = tk.Checkbutton(
            self.content_frame,
            text="I have a Tinxy device",
            variable=self.tinxy_enabled_var,
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.text_color,
            command=self._toggle_tinxy_setup
        )
        tinxy_check.pack(pady=10)
        
        # Tinxy setup frame
        self.tinxy_setup_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        
        # API Key
        api_frame = tk.Frame(self.tinxy_setup_frame, bg=self.bg_color)
        api_frame.pack(fill=tk.X, pady=5, padx=50)
        
        tk.Label(
            api_frame,
            text="API Key:",
            font=("Helvetica", 10),
            bg=self.bg_color,
            width=15,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        self.tinxy_api_entry = tk.Entry(
            api_frame,
            font=("Helvetica", 10),
            width=40,
            show="*"
        )
        self.tinxy_api_entry.pack(side=tk.LEFT, padx=5)
        
        # Device ID
        device_frame = tk.Frame(self.tinxy_setup_frame, bg=self.bg_color)
        device_frame.pack(fill=tk.X, pady=5, padx=50)
        
        tk.Label(
            device_frame,
            text="Device ID:",
            font=("Helvetica", 10),
            bg=self.bg_color,
            width=15,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        self.tinxy_device_entry = tk.Entry(
            device_frame,
            font=("Helvetica", 10),
            width=40
        )
        self.tinxy_device_entry.pack(side=tk.LEFT, padx=5)
        
        # Device Number
        number_frame = tk.Frame(self.tinxy_setup_frame, bg=self.bg_color)
        number_frame.pack(fill=tk.X, pady=5, padx=50)
        
        tk.Label(
            number_frame,
            text="Device Number:",
            font=("Helvetica", 10),
            bg=self.bg_color,
            width=15,
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        self.tinxy_number_var = tk.IntVar(value=1)
        tk.Spinbox(
            number_frame,
            from_=1,
            to=8,
            textvariable=self.tinxy_number_var,
            font=("Helvetica", 10),
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Help text
        tk.Label(
            self.tinxy_setup_frame,
            text="\n📱 To get your API key:\n"
                 "1. Open Tinxy app\n"
                 "2. Go to Settings → API Token\n"
                 "3. Copy the token",
            font=("Helvetica", 9),
            bg=self.bg_color,
            fg="#666666",
            justify=tk.LEFT
        ).pack(pady=10)
        
        tk.Label(
            self.content_frame,
            text="Don't have Tinxy? No problem! We'll use software-based monitor control.",
            font=("Helvetica", 9),
            bg=self.bg_color,
            fg="#666666"
        ).pack(pady=(20, 0))
    
    def _toggle_tinxy_setup(self):
        """Toggle Tinxy setup visibility"""
        if self.tinxy_enabled_var.get():
            self.tinxy_setup_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        else:
            self.tinxy_setup_frame.pack_forget()
    
    def _create_completion_step(self):
        """Completion screen"""
        tk.Label(
            self.content_frame,
            text="🎉 Setup Complete!",
            font=("Helvetica", 24, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        ).pack(pady=(40, 20))
        
        tk.Label(
            self.content_frame,
            text="BreakGuard is ready to help you stay healthy!",
            font=("Helvetica", 12),
            bg=self.bg_color,
            fg="#666666"
        ).pack(pady=(0, 30))
        
        # Summary
        summary_frame = tk.Frame(self.content_frame, bg="white", relief=tk.SOLID, borderwidth=1)
        summary_frame.pack(pady=20, padx=40, fill=tk.X)
        
        tk.Label(
            summary_frame,
            text="Your Configuration:",
            font=("Helvetica", 12, "bold"),
            bg="white",
            fg=self.text_color
        ).pack(pady=(10, 5))
        
        config_text = f"""
Work Interval: {self.work_interval_var.get()} minutes
Warning: {self.warning_var.get()} minutes before lock
TOTP: {'Enabled' if self.totp_enabled_var.get() else 'Disabled'}
Face Verification: {'Enabled' if self.face_enabled_var.get() else 'Disabled'}
Tinxy API: {'Configured' if self.tinxy_enabled_var.get() else 'Not configured'}
        """
        
        tk.Label(
            summary_frame,
            text=config_text,
            font=("Helvetica", 10),
            bg="white",
            fg=self.text_color,
            justify=tk.LEFT
        ).pack(pady=10, padx=20)
        
        tk.Label(
            self.content_frame,
            text="BreakGuard will start automatically with Windows.\nYou can change settings anytime from the system tray.",
            font=("Helvetica", 9),
            bg=self.bg_color,
            fg="#666666",
            justify=tk.CENTER
        ).pack(pady=(20, 0))
    
    def _finish_setup(self):
        """Save configuration and finish"""
        from config_manager import ConfigManager
        
        # Update config data
        self.config_data['work_interval_minutes'] = self.work_interval_var.get()
        self.config_data['warning_before_minutes'] = self.warning_var.get()
        self.config_data['auth_enabled'] = self.totp_enabled_var.get()
        self.config_data['face_verification'] = self.face_enabled_var.get()
        
        if self.tinxy_enabled_var.get():
            self.config_data['tinxy_api_key'] = self.tinxy_api_entry.get()
            self.config_data['tinxy_device_id'] = self.tinxy_device_entry.get()
            self.config_data['tinxy_device_number'] = self.tinxy_number_var.get()
        
        # Save configuration
        config = ConfigManager()
        for key, value in self.config_data.items():
            config.set(key, value)
        config.save_config()
        
        messagebox.showinfo(
            "Setup Complete",
            "BreakGuard has been configured successfully!\n\n"
            "The application will now start and run in the background.\n"
            "Look for the BreakGuard icon in your system tray."
        )
        
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the setup wizard"""
        self.root.mainloop()

if __name__ == "__main__":
    wizard = SetupWizard()
    wizard.run()
