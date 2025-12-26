"""
TOTP Authentication Module
Handles authenticator app setup and verification
"""
from __future__ import annotations

import pyotp
import qrcode
from io import BytesIO
from PIL import Image
from pathlib import Path
import json
import base64
import os
import logging
from typing import Optional
from exceptions import TOTPError, ConfigError

logger = logging.getLogger(__name__)

# Try to import Windows DPAPI
try:
    import win32crypt
    import pywintypes
    DPAPI_AVAILABLE = True
except ImportError:
    DPAPI_AVAILABLE = False
    logger.warning("win32crypt not available - falling back to Fernet encryption")

class TOTPAuth:
    """TOTP (Time-based One-Time Password) authentication handler
    Compatible with Google Authenticator, Microsoft Authenticator, Authy, and other TOTP apps
    """
    
    def __init__(self, data_dir: str | Path = None):
        """Initialize TOTP authentication
        
        Args:
            data_dir: Directory to store encrypted TOTP secret
        """
        if data_dir is None:
            from path_utils import get_data_dir
            data_dir = get_data_dir()
        
        self.data_dir: Path = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.secret_file = self.data_dir / 'totp_secret.enc'
        self.key_file = self.data_dir / '.key'
        
        # Use DPAPI if available, otherwise fallback to Fernet
        self.use_dpapi = DPAPI_AVAILABLE
        if not self.use_dpapi:
            from cryptography.fernet import Fernet
            self._encryption_key = self._get_or_create_key()
        
        self._secret = None
    
    def _get_or_create_key(self) -> bytes:
        """Get or create Fernet encryption key (fallback when DPAPI unavailable)
        
        Returns:
            Encryption key bytes
        """
        from cryptography.fernet import Fernet
        
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # Hide the key file on Windows
            try:
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(str(self.key_file), 2)  # FILE_ATTRIBUTE_HIDDEN
            except:
                pass
            return key
    
    def generate_secret(self) -> str:
        """Generate new TOTP secret
        
        Returns:
            Base32 encoded secret string
        """
        self._secret = pyotp.random_base32()
        return self._secret
    
    def save_secret(self, secret: str = None) -> bool:
        """Encrypt and save TOTP secret using Windows DPAPI or Fernet
        
        Args:
            secret: TOTP secret to save. If None, uses last generated secret.
            
        Returns:
            True if successful, False otherwise
        """
        if secret is None:
            secret = self._secret
        
        if not secret:
            return False
        
        try:
            if self.use_dpapi:
                # Use Windows DPAPI for encryption
                encrypted = win32crypt.CryptProtectData(
                    secret.encode(),
                    'BreakGuard TOTP Secret',  # Description
                    None,  # Optional entropy
                    None,  # Reserved
                    None,  # Prompt struct
                    0      # Flags
                )
            else:
                # Fallback to Fernet encryption
                from cryptography.fernet import Fernet
                fernet = Fernet(self._encryption_key)
                encrypted = fernet.encrypt(secret.encode())
            
            with open(self.secret_file, 'wb') as f:
                f.write(encrypted)
            
            self._secret = secret
            logger.info(f"TOTP secret saved using {'DPAPI' if self.use_dpapi else 'Fernet'}")
            return True
        except (IOError, OSError) as e:
            logger.error(f"Error saving TOTP secret: {e}", exc_info=True)
            return False
    
    def load_secret(self) -> Optional[str]:
        """Load and decrypt TOTP secret using Windows DPAPI or Fernet
        
        Returns:
            Decrypted secret string or None if not found
        """
        if not self.secret_file.exists():
            return None
        
        try:
            with open(self.secret_file, 'rb') as f:
                encrypted = f.read()
            
            if self.use_dpapi:
                # Use Windows DPAPI for decryption
                description, decrypted = win32crypt.CryptUnprotectData(
                    encrypted,
                    None,  # Optional entropy
                    None,  # Reserved
                    None,  # Prompt struct
                    0      # Flags
                )
                self._secret = decrypted.decode()
            else:
                # Fallback to Fernet decryption
                from cryptography.fernet import Fernet
                fernet = Fernet(self._encryption_key)
                self._secret = fernet.decrypt(encrypted).decode()
            
            logger.info(f"TOTP secret loaded using {'DPAPI' if self.use_dpapi else 'Fernet'}")
            return self._secret
        except Exception as e:
            if self.use_dpapi and isinstance(e, pywintypes.error) and e.args[0] == 13:
                logger.error("TOTP secret file is corrupted or from another machine/user. Please delete 'data/totp_secret.enc' and run setup again.")
            else:
                logger.error(f"Error loading secret: {e}", exc_info=True)
            return None
    
    def generate_qr_code(self, secret: str = None, name: str = "BreakGuard", issuer: str = "BreakGuard") -> Image.Image:
        """Generate QR code for authenticator apps
        
        Args:
            secret: TOTP secret. If None, uses loaded/generated secret.
            name: Account name to show in authenticator app
            issuer: Issuer name
            
        Returns:
            PIL Image object of QR code
        """
        if secret is None:
            secret = self._secret or self.load_secret()
        
        if not secret:
            raise ValueError("No secret available. Generate or load a secret first.")
        
        # Create TOTP provisioning URI
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=name, issuer_name=issuer)
        
        # Generate QR code
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
    
    def get_qr_code_bytes(self, secret: str = None, name: str = "BreakGuard", issuer: str = "BreakGuard") -> bytes:
        """Generate QR code as PNG bytes
        
        Args:
            secret: TOTP secret
            name: Account name
            issuer: Issuer name
            
        Returns:
            PNG image bytes
        """
        img = self.generate_qr_code(secret, name, issuer)
        
        # Convert to bytes
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()
    
    def verify_code(self, code: str, secret: str = None) -> bool:
        """Verify TOTP code
        
        Args:
            code: 6-digit code from authenticator app
            secret: TOTP secret. If None, uses loaded secret.
            
        Returns:
            True if code is valid, False otherwise
        """
        if secret is None:
            secret = self._secret or self.load_secret()
        
        if not secret:
            return False
        
        try:
            totp = pyotp.TOTP(secret)
            # Verify with 1 window of tolerance (30 seconds before/after)
            return totp.verify(code, valid_window=1)
        except Exception as e:
            print(f"Error verifying code: {e}")
            return False
    
    def get_current_code(self, secret: str = None) -> str:
        """Get current TOTP code (for testing/debugging)
        
        Args:
            secret: TOTP secret. If None, uses loaded secret.
            
        Returns:
            Current 6-digit code
        """
        if secret is None:
            secret = self._secret or self.load_secret()
        
        if not secret:
            return None
        
        totp = pyotp.TOTP(secret)
        return totp.now()
    
    def is_configured(self) -> bool:
        """Check if TOTP is configured
        
        Returns:
            True if secret exists, False otherwise
        """
        return self.secret_file.exists()
    
    def get_secret_for_backup(self) -> str:
        """Get secret for user backup (show once during setup)
        
        Returns:
            Current secret or None
        """
        return self._secret or self.load_secret()
