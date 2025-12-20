"""
Configuration Manager for BreakGuard
Handles reading/writing config.json and default settings
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

class ConfigManager:
    """Manages application configuration"""
    
    DEFAULT_CONFIG = {
        "work_interval_minutes": 60,
        "warning_before_minutes": 5,
        "break_duration_minutes": 5,
        "totp_enabled": True,
        "face_verification_enabled": True,
        "tinxy_enabled": False,
        "tinxy_api_key": "",
        "tinxy_device_id": "",
        "tinxy_device_number": 1,
        "auto_start_windows": True,
        "max_snooze_count": 1,
        "setup_completed": False
    }
    
    def __init__(self, config_path: str = None):
        """Initialize config manager
        
        Args:
            config_path: Path to config.json file. If None, uses default location.
        """
        if config_path is None:
            # Get path relative to main.py
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / 'config.json'
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**self.DEFAULT_CONFIG, **config}
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self) -> bool:
        """Save current configuration to file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create parent directory if it doesn't exist
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value
        
        Args:
            key: Configuration key
            value: New value
        """
        self.config[key] = value
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple configuration values
        
        Args:
            updates: Dictionary of key-value pairs to update
        """
        self.config.update(updates)
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to default values"""
        self.config = self.DEFAULT_CONFIG.copy()
    
    def is_first_run(self) -> bool:
        """Check if this is the first run (setup not completed)
        
        Returns:
            True if setup needed, False otherwise
        """
        return not self.config.get('setup_completed', False)
    
    def mark_setup_complete(self) -> bool:
        """Mark setup as completed and save
        
        Returns:
            True if successful, False otherwise
        """
        self.config['setup_completed'] = True
        return self.save_config()
    
    def get_work_interval_seconds(self) -> int:
        """Get work interval in seconds
        
        Returns:
            Work interval in seconds
        """
        return self.config.get('work_interval_minutes', 60) * 60
    
    def get_warning_time_seconds(self) -> int:
        """Get warning time in seconds
        
        Returns:
            Warning time in seconds
        """
        return self.config.get('warning_before_minutes', 5) * 60
    
    def get_break_duration_seconds(self) -> int:
        """Get break duration in seconds
        
        Returns:
            Break duration in seconds
        """
        return self.config.get('break_duration_minutes', 10) * 60
    
    def is_totp_enabled(self) -> bool:
        """Check if TOTP authentication is enabled"""
        return self.config.get('totp_enabled', True)
    
    def is_face_verification_enabled(self) -> bool:
        """Check if face verification is enabled"""
        return self.config.get('face_verification_enabled', True)
    
    def is_tinxy_enabled(self) -> bool:
        """Check if Tinxy IoT control is enabled"""
        return self.config.get('tinxy_enabled', False)
    
    def get_tinxy_credentials(self) -> Dict[str, Any]:
        """Get Tinxy API credentials
        
        Returns:
            Dictionary with api_key, device_id, device_number
        """
        return {
            'api_key': self.config.get('tinxy_api_key', ''),
            'device_id': self.config.get('tinxy_device_id', ''),
            'device_number': self.config.get('tinxy_device_number', 1)
        }
    
    def __repr__(self) -> str:
        """String representation"""
        return f"ConfigManager(config_path='{self.config_path}')"
