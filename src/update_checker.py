"""
Update Checker Module
Checks for new versions from GitHub and notifies users
"""

import json
import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Tuple
from packaging import version

logger = logging.getLogger(__name__)


class UpdateChecker:
    """Checks for application updates from GitHub"""
    
    def __init__(self):
        self.version_file = Path(__file__).parent.parent / 'version.json'
        self.current_version = self._load_local_version()
        
    def _load_local_version(self) -> str:
        """Load current version from local version.json"""
        try:
            if self.version_file.exists():
                with open(self.version_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('version', '0.0.0')
            return '0.0.0'
        except Exception as e:
            logger.error(f"Failed to load local version: {e}")
            return '0.0.0'
    
    def check_for_updates(self, timeout: int = 5) -> Optional[Dict]:
        """
        Check for updates from GitHub
        
        Returns:
            Dict with update info if available, None otherwise
            {
                'available': bool,
                'current_version': str,
                'latest_version': str,
                'changelog': list,
                'download_url': str,
                'release_date': str
            }
        """
        try:
            # Load local version data
            with open(self.version_file, 'r', encoding='utf-8') as f:
                local_data = json.load(f)
            
            version_check_url = local_data.get('version_check_url')
            if not version_check_url:
                logger.warning("No version_check_url configured")
                return None
            
            # Fetch remote version info
            response = requests.get(version_check_url, timeout=timeout)
            response.raise_for_status()
            remote_data = response.json()
            
            current_ver = version.parse(self.current_version)
            latest_ver = version.parse(remote_data.get('version', '0.0.0'))
            
            update_available = latest_ver > current_ver
            
            return {
                'available': update_available,
                'current_version': self.current_version,
                'latest_version': remote_data.get('version', '0.0.0'),
                'changelog': remote_data.get('changelog', []),
                'download_url': remote_data.get('update_url', ''),
                'release_date': remote_data.get('release_date', '')
            }
            
        except requests.RequestException as e:
            logger.error(f"Network error checking for updates: {e}")
            return None
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return None
    
    def get_version_info(self) -> Dict:
        """Get current version information"""
        try:
            with open(self.version_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    'version': data.get('version', '0.0.0'),
                    'release_date': data.get('release_date', 'Unknown'),
                    'changelog': data.get('changelog', [])
                }
        except Exception as e:
            logger.error(f"Error loading version info: {e}")
            return {
                'version': '0.0.0',
                'release_date': 'Unknown',
                'changelog': []
            }
    
    def compare_versions(self, ver1: str, ver2: str) -> int:
        """
        Compare two version strings
        
        Returns:
            -1 if ver1 < ver2
             0 if ver1 == ver2
             1 if ver1 > ver2
        """
        try:
            v1 = version.parse(ver1)
            v2 = version.parse(ver2)
            
            if v1 < v2:
                return -1
            elif v1 > v2:
                return 1
            else:
                return 0
        except Exception as e:
            logger.error(f"Error comparing versions: {e}")
            return 0
