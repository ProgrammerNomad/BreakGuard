"""
Configuration Manager for BreakGuard
Handles reading/writing config.json and default settings
"""
from __future__ import annotations

import json
import os
import logging
import shutil
from pathlib import Path
from typing import Any, Dict
from datetime import datetime
from exceptions import ConfigError, ValidationError

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages application configuration"""
    
    # Validation rules for configuration values
    VALIDATION_RULES = {
        'work_interval_minutes': {'min': 15, 'max': 240, 'type': int},
        'warning_before_minutes': {'min': 1, 'max': 30, 'type': int},
        'break_duration_minutes': {'min': 1, 'max': 60, 'type': int},
        'snooze_limit': {'min': 0, 'max': 10, 'type': int},
        'face_recognition_tolerance': {'min': 0.0, 'max': 1.0, 'type': float},
        'max_authentication_attempts': {'min': 1, 'max': 10, 'type': int},
    }
    
    DEFAULT_CONFIG = {
        "config_version": 1,
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
    
    def __init__(self, config_path: str | Path = None):
        """Initialize config manager
        
        Args:
            config_path: Path to config.json file. If None, uses default location.
        """
        if config_path is None:
            # Get path relative to main.py
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / 'config.json'
        
        self.config_path: Path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                    # Check for config migration
                    config_version = config.get('config_version', 0)
                    if config_version < self.DEFAULT_CONFIG['config_version']:
                        logger.info(f"Migrating config from version {config_version} to {self.DEFAULT_CONFIG['config_version']}")
                        config = self._migrate_config(config, config_version)
                    
                    # Merge with defaults to ensure all keys exist
                    return {**self.DEFAULT_CONFIG, **config}
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading config from {self.config_path}: {e}", exc_info=True)
                raise ConfigError(f"Failed to load configuration: {e}", config_key=str(self.config_path))
            except Exception as e:
                logger.error(f"Unexpected error loading config: {e}", exc_info=True)
                return self.DEFAULT_CONFIG.copy()
        else:
            logger.info("Config file not found, using defaults")
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
            logger.info("Configuration saved successfully")
            return True
        except (IOError, OSError) as e:
            logger.error(f"Error saving config to {self.config_path}: {e}", exc_info=True)
            raise ConfigError(f"Failed to save configuration: {e}", config_key=str(self.config_path))
        except Exception as e:
            logger.error(f"Unexpected error saving config: {e}", exc_info=True)
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
            
        Raises:
            ValidationError: If value is invalid
        """
        # Validate value if rules exist
        if key in self.VALIDATION_RULES:
            self.validate_value(key, value)
        
        self.config[key] = value
    
    def validate_value(self, key: str, value: Any) -> bool:
        """Validate configuration value against rules
        
        Args:
            key: Configuration key
            value: Value to validate
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If value is invalid
        """
        if key not in self.VALIDATION_RULES:
            return True  # No validation rules for this key
        
        rules = self.VALIDATION_RULES[key]
        
        # Type check
        expected_type = rules.get('type')
        if expected_type and not isinstance(value, expected_type):
            raise ValidationError(
                f"{key} must be of type {expected_type.__name__}, got {type(value).__name__}",
                field_name=key,
                invalid_value=value
            )
        
        # Range check
        if 'min' in rules and value < rules['min']:
            raise ValidationError(
                f"{key} must be at least {rules['min']}, got {value}",
                field_name=key,
                invalid_value=value
            )
        
        if 'max' in rules and value > rules['max']:
            raise ValidationError(
                f"{key} must be at most {rules['max']}, got {value}",
                field_name=key,
                invalid_value=value
            )
        
        logger.debug(f"Validated {key}={value}")
        return True
    
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
    
    def export_config(self, export_path: str) -> bool:
        """Export configuration to a file
        
        Args:
            export_path: Path where to export the configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            export_data = {
                'version': '1.0',
                'exported_at': datetime.now().isoformat(),
                'config': self.config.copy()
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=4)
            
            logger.info(f"Configuration exported to {export_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export config: {e}", exc_info=True)
            return False
    
    def import_config(self, import_path: str, validate: bool = True) -> Dict[str, Any]:
        """Import configuration from a file
        
        Args:
            import_path: Path to the configuration file to import
            validate: Whether to validate imported values
            
        Returns:
            Dictionary with changes summary: {'added': [], 'modified': [], 'unchanged': []}
            
        Raises:
            ConfigError: If import fails
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Check if it's an exported config (with metadata)
            if 'config' in import_data:
                imported_config = import_data['config']
                version = import_data.get('version', 'unknown')
                exported_at = import_data.get('exported_at', 'unknown')
                logger.info(f"Importing config version {version} from {exported_at}")
            else:
                # Treat as raw config
                imported_config = import_data
            
            # Validate imported config
            if validate:
                for key, value in imported_config.items():
                    if key in self.VALIDATION_RULES:
                        self.validate_value(key, value)
            
            # Track changes
            changes = {'added': [], 'modified': [], 'unchanged': []}
            
            for key, new_value in imported_config.items():
                old_value = self.config.get(key)
                if old_value is None:
                    changes['added'].append(key)
                elif old_value != new_value:
                    changes['modified'].append(key)
                else:
                    changes['unchanged'].append(key)
            
            logger.info(f"Import summary: {len(changes['modified'])} modified, {len(changes['added'])} added")
            return changes
            
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in import file: {e}", config_key=import_path)
        except Exception as e:
            logger.error(f"Failed to import config: {e}", exc_info=True)
            raise ConfigError(f"Failed to import configuration: {e}", config_key=import_path)
    
    def apply_imported_config(self, import_path: str) -> bool:
        """Import and apply configuration from a file
        
        Args:
            import_path: Path to the configuration file to import
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create backup of current config
            backup_path = self.config_path.with_suffix('.json.backup')
            shutil.copy2(self.config_path, backup_path)
            logger.info(f"Created backup at {backup_path}")
            
            # Import config
            with open(import_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            if 'config' in import_data:
                imported_config = import_data['config']
            else:
                imported_config = import_data
            
            # Update config
            self.config.update(imported_config)
            
            # Save
            if self.save_config():
                logger.info("Imported configuration applied successfully")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to apply imported config: {e}", exc_info=True)
            # Restore backup
            if backup_path.exists():
                shutil.copy2(backup_path, self.config_path)
                logger.info("Restored config from backup")
            return False
    
    def _migrate_config(self, config: Dict[str, Any], from_version: int) -> Dict[str, Any]:
        """Migrate configuration from old version to current
        
        Args:
            config: Old configuration dictionary
            from_version: Version number to migrate from
            
        Returns:
            Migrated configuration dictionary
        """
        # Backup old config before migration
        backup_path = self.config_path.with_suffix(f'.v{from_version}.bak')
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Backed up old config to {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to backup config: {e}")
        
        # Apply migrations sequentially
        migrated = config.copy()
        
        # Migration from v0 to v1
        if from_version < 1:
            logger.info("Applying migration v0 -> v1")
            # Add new fields introduced in v1
            migrated['config_version'] = 1
            # No breaking changes in v1, just version tracking
        
        # Future migrations would go here
        # if from_version < 2:
        #     logger.info("Applying migration v1 -> v2")
        #     # Add migration logic for v2
        
        logger.info(f"Config migration complete: v{from_version} -> v{migrated.get('config_version', 1)}")
        return migrated
    
    def __repr__(self) -> str:
        """String representation"""
        return f"ConfigManager(config_path='{self.config_path}')"
