"""
Data Migration Helper
Handles upgrading user data between versions
"""

import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class DataMigration:
    """Handles data migration between BreakGuard versions"""
    
    def __init__(self):
        self.app_dir = Path(__file__).parent.parent
        self.data_dir = self.app_dir / 'data'
        self.config_file = self.app_dir / 'config.json'
        self.version_file = self.app_dir / 'version.json'
        
    def get_current_version(self) -> str:
        """Get current installed version"""
        try:
            if self.version_file.exists():
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('version', '0.0.0')
            return '0.0.0'
        except Exception as e:
            logger.error(f"Failed to get current version: {e}")
            return '0.0.0'
    
    def backup_user_data(self, backup_dir: Path) -> bool:
        """
        Backup user data to specified directory
        
        Args:
            backup_dir: Directory to store backup
            
        Returns:
            True if successful, False otherwise
        """
        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup files
            files_to_backup = [
                self.data_dir / 'app_state.json',
                self.data_dir / 'face_encodings.json',
                self.data_dir / 'totp_secret.enc',
                self.config_file,
            ]
            
            backed_up = []
            for file in files_to_backup:
                if file.exists():
                    dest = backup_dir / file.name
                    shutil.copy2(file, dest)
                    backed_up.append(file.name)
                    logger.info(f"Backed up: {file.name}")
            
            # Create backup manifest
            manifest = {
                'version': self.get_current_version(),
                'files': backed_up,
                'timestamp': str(Path(backup_dir).stat().st_mtime)
            }
            
            with open(backup_dir / 'backup_manifest.json', 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"Backup completed: {len(backed_up)} files")
            return True
            
        except Exception as e:
            logger.error(f"Failed to backup user data: {e}")
            return False
    
    def restore_user_data(self, backup_dir: Path) -> bool:
        """
        Restore user data from backup directory
        
        Args:
            backup_dir: Directory containing backup
            
        Returns:
            True if successful, False otherwise
        """
        try:
            manifest_file = backup_dir / 'backup_manifest.json'
            if not manifest_file.exists():
                logger.error("Backup manifest not found")
                return False
            
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Restore files
            restored = []
            for filename in manifest.get('files', []):
                source = backup_dir / filename
                
                if filename == 'config.json':
                    dest = self.config_file
                else:
                    dest = self.data_dir / filename
                
                if source.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, dest)
                    restored.append(filename)
                    logger.info(f"Restored: {filename}")
            
            logger.info(f"Restore completed: {len(restored)} files")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore user data: {e}")
            return False
    
    def migrate_data(self, from_version: str, to_version: str) -> bool:
        """
        Migrate data from one version to another
        
        Args:
            from_version: Source version
            to_version: Target version
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Migrating data from {from_version} to {to_version}")
            
            # Version-specific migrations
            migrations = [
                # Example: ('1.0.0', '1.1.0', self._migrate_1_0_to_1_1),
                # Add future migrations here
            ]
            
            for source_ver, target_ver, migration_func in migrations:
                if from_version == source_ver and to_version >= target_ver:
                    logger.info(f"Running migration: {source_ver} -> {target_ver}")
                    if not migration_func():
                        logger.error(f"Migration failed: {source_ver} -> {target_ver}")
                        return False
            
            logger.info("Data migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate data: {e}")
            return False
    
    def verify_data_integrity(self) -> Dict[str, bool]:
        """
        Verify integrity of user data files
        
        Returns:
            Dict mapping file names to validity status
        """
        results = {}
        
        # Check config file
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                results['config.json'] = True
            else:
                results['config.json'] = False
        except Exception:
            results['config.json'] = False
        
        # Check app state
        try:
            state_file = self.data_dir / 'app_state.json'
            if state_file.exists():
                with open(state_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                results['app_state.json'] = True
            else:
                results['app_state.json'] = False
        except Exception:
            results['app_state.json'] = False
        
        # Check face encodings
        try:
            face_file = self.data_dir / 'face_encodings.json'
            if face_file.exists():
                with open(face_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                results['face_encodings.json'] = True
            else:
                results['face_encodings.json'] = False
        except Exception:
            results['face_encodings.json'] = False
        
        # Check TOTP secret
        totp_file = self.data_dir / 'totp_secret.enc'
        results['totp_secret.enc'] = totp_file.exists()
        
        return results
    
    def get_migration_path(self) -> List[str]:
        """
        Get list of migrations needed for current data
        
        Returns:
            List of migration descriptions
        """
        migrations_needed = []
        current = self.get_current_version()
        
        # Check what migrations would be needed
        # Add logic here based on detected data version
        
        return migrations_needed
    
    # Example migration function
    def _migrate_1_0_to_1_1(self) -> bool:
        """
        Example migration from v1.0 to v1.1
        
        Returns:
            True if successful
        """
        try:
            # Load config
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Add new settings with defaults
            if 'new_setting' not in config:
                config['new_setting'] = True
            
            # Save updated config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"Migration 1.0->1.1 failed: {e}")
            return False
