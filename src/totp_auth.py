"""
TOTP (Time-Based One-Time Password) Authentication for BreakGuard
Google Authenticator compatible
"""
import pyotp
import qrcode
from io import BytesIO
from PIL import Image
from typing import Optional, Tuple

class TOTPAuth:
    def __init__(self, secret: Optional[str] = None):
        """
        Initialize TOTP authentication
        Args:
            secret: Base32 encoded secret. If None, generates a new one.
        """
        if secret:
            self.secret = secret
        else:
            self.secret = pyotp.random_base32()
        
        self.totp = pyotp.TOTP(self.secret)
        self.app_name = "BreakGuard"
        self.user_email = "user@breakguard.local"
    
    def get_secret(self) -> str:
        """Get the TOTP secret for storage"""
        return self.secret
    
    def get_provisioning_uri(self) -> str:
        """Get provisioning URI for QR code generation"""
        return self.totp.provisioning_uri(
            name=self.user_email,
            issuer_name=self.app_name
        )
    
    def generate_qr_code(self) -> Image.Image:
        """
        Generate QR code for Google Authenticator setup
        Returns PIL Image object
        """
        uri = self.get_provisioning_uri()
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        return img
    
    def save_qr_code(self, filepath: str = "data/totp_qr.png"):
        """Save QR code to file"""
        img = self.generate_qr_code()
        img.save(filepath)
        print(f"QR code saved to {filepath}")
        return filepath
    
    def get_current_code(self) -> str:
        """Get current TOTP code (for testing/debugging only)"""
        return self.totp.now()
    
    def verify_code(self, code: str) -> bool:
        """
        Verify TOTP code
        Args:
            code: 6-digit code from authenticator app
        Returns:
            True if valid, False otherwise
        """
        try:
            # Remove spaces and validate format
            code = code.strip().replace(" ", "")
            
            if not code.isdigit() or len(code) != 6:
                return False
            
            # Verify with window of ±1 interval (30 seconds each)
            # This allows for slight clock drift
            return self.totp.verify(code, valid_window=1)
        except Exception as e:
            print(f"Error verifying TOTP code: {e}")
            return False
    
    def get_setup_instructions(self) -> str:
        """Get setup instructions for the user"""
        return f"""
BreakGuard TOTP Setup Instructions:

1. Install Google Authenticator app on your phone
   - Android: https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2
   - iOS: https://apps.apple.com/app/google-authenticator/id388497605

2. Open Google Authenticator app

3. Tap '+' to add a new account

4. Scan the QR code saved at: data/totp_qr.png
   OR
   Manually enter this secret: {self.secret}

5. The app will show a 6-digit code that changes every 30 seconds

6. Use this code to unlock BreakGuard during breaks

Secret Key: {self.secret}
(Keep this safe - you'll need it to restore access if you lose your phone)
"""
    
    def get_time_remaining(self) -> int:
        """Get seconds remaining until current code expires"""
        import time
        return 30 - int(time.time()) % 30
    
    @staticmethod
    def format_secret_for_display(secret: str) -> str:
        """Format secret in groups of 4 for easier reading"""
        return ' '.join([secret[i:i+4] for i in range(0, len(secret), 4)])

class TOTPSetup:
    """Helper class for initial TOTP setup"""
    
    @staticmethod
    def first_time_setup() -> Tuple[TOTPAuth, str]:
        """
        Perform first-time TOTP setup
        Returns: (TOTPAuth instance, path to QR code)
        """
        print("=== BreakGuard TOTP Setup ===\n")
        
        # Generate new TOTP instance
        totp_auth = TOTPAuth()
        
        # Save QR code
        qr_path = totp_auth.save_qr_code()
        
        # Display instructions
        print(totp_auth.get_setup_instructions())
        
        # Display formatted secret
        formatted_secret = TOTPAuth.format_secret_for_display(totp_auth.get_secret())
        print(f"\nFormatted Secret (for manual entry): {formatted_secret}")
        
        return totp_auth, qr_path
    
    @staticmethod
    def verify_setup(totp_auth: TOTPAuth) -> bool:
        """
        Interactive verification to ensure TOTP is set up correctly
        """
        print("\n=== Verify TOTP Setup ===")
        print("Enter the 6-digit code from your Google Authenticator app:")
        
        max_attempts = 3
        for attempt in range(max_attempts):
            code = input(f"Code (attempt {attempt + 1}/{max_attempts}): ").strip()
            
            if totp_auth.verify_code(code):
                print("✓ Verification successful! TOTP is configured correctly.")
                return True
            else:
                remaining = max_attempts - attempt - 1
                if remaining > 0:
                    print(f"✗ Invalid code. {remaining} attempts remaining.")
                    print(f"Code expires in {totp_auth.get_time_remaining()} seconds.")
                else:
                    print("✗ Verification failed. Please check your setup.")
        
        return False
