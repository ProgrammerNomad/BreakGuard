"""
Configuration Manager for BreakGuard
Handles loading, saving, and encrypting configuration data
"""
import json
import os
from pathlib import Path
from cryptography.fernet import Fernet
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        self.key_file = self.data_dir / "key.key"
        self.encrypted_secrets = self.data_dir / "secrets.enc"
        
        self._ensure_encryption_key()
        self.config = self._load_config()
    
    def _ensure_encryption_key(self):
        """Generate or load encryption key for sensitive data"""
        if not self.key_file.exists():
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        
        with open(self.key_file, 'rb') as f:
            self.encryption_key = f.read()
        
        self.cipher = Fernet(self.encryption_key)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_path.exists():
            return self._get_default_config()
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Load encrypted secrets if they exist
            if self.encrypted_secrets.exists():
                config = self._load_secrets(config)
            
            return config
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "work_interval_minutes": 60,
            "warning_before_minutes": 5,
            "max_snooze": 1,
            "tinxy_api_key": "",
            "tinxy_device_id": "",
            "tinxy_device_number": 1,
            "auth_enabled": True,
            "face_verification": True,
            "auto_start": True,
            "totp_secret": ""
        }
    
    def _load_secrets(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load encrypted secrets"""
        try:
            with open(self.encrypted_secrets, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            secrets = json.loads(decrypted_data.decode())
            
            # Merge secrets into config
            config.update(secrets)
            return config
        except Exception as e:
            print(f"Error loading secrets: {e}")
            return config
    
    def save_config(self):
        """Save configuration to file"""
        try:
            # Separate sensitive data
            public_config = self.config.copy()
            secrets = {}
            
            sensitive_keys = ['tinxy_api_key', 'totp_secret']
            for key in sensitive_keys:
                if key in public_config:
                    secrets[key] = public_config[key]
                    public_config[key] = ""
            
            # Save public config
            with open(self.config_path, 'w') as f:
                json.dump(public_config, f, indent=2)
            
            # Encrypt and save secrets
            if secrets:
                encrypted_data = self.cipher.encrypt(
                    json.dumps(secrets).encode()
                )
                with open(self.encrypted_secrets, 'wb') as f:
                    f.write(encrypted_data)
            
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self.config.copy()
