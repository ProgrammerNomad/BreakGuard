"""
Path utilities for BreakGuard
Handles cross-platform paths for config, data, and logs
"""

import os
import sys
from pathlib import Path


def get_app_data_dir() -> Path:
    """
    Get the application data directory (user-writable location)
    
    Returns:
        Path to BreakGuard's data directory in user's AppData
    """
    if sys.platform == 'win32':
        # Windows: Use LocalAppData
        appdata = os.getenv('LOCALAPPDATA', os.getenv('APPDATA'))
        if appdata:
            return Path(appdata) / 'BreakGuard'
    elif sys.platform == 'darwin':
        # macOS
        return Path.home() / 'Library' / 'Application Support' / 'BreakGuard'
    else:
        # Linux/Unix
        xdg_config = os.getenv('XDG_CONFIG_HOME')
        if xdg_config:
            return Path(xdg_config) / 'breakguard'
        return Path.home() / '.config' / 'breakguard'
    
    # Fallback
    return Path.home() / '.breakguard'


def get_config_file() -> Path:
    """Get path to config.json file"""
    return get_app_data_dir() / 'config.json'


def get_data_dir() -> Path:
    """Get path to data directory"""
    data_dir = get_app_data_dir() / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_logs_dir() -> Path:
    """Get path to logs directory"""
    logs_dir = get_app_data_dir() / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def get_assets_dir() -> Path:
    """
    Get path to assets directory (read-only, in installation folder)
    
    Returns:
        Path to assets directory
    """
    # For PyInstaller bundled app
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        if hasattr(sys, '_MEIPASS'):
            # One-file mode
            return Path(sys._MEIPASS) / 'assets'
        else:
            # One-folder mode
            return Path(sys.executable).parent / '_internal' / 'assets'
    else:
        # Running from source
        return Path(__file__).parent.parent / 'assets'


def get_app_dir() -> Path:
    """
    Get the application installation directory
    
    Returns:
        Path to app directory (may not be writable)
    """
    if getattr(sys, 'frozen', False):
        # Running in PyInstaller bundle
        return Path(sys.executable).parent
    else:
        # Running from source
        return Path(__file__).parent.parent


def ensure_app_data_dirs():
    """Ensure all necessary app data directories exist"""
    app_data = get_app_data_dir()
    app_data.mkdir(parents=True, exist_ok=True)
    
    get_data_dir()  # Creates data dir
    get_logs_dir()  # Creates logs dir
    
    return app_data
