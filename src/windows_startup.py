"""
Windows Startup Integration
Adds BreakGuard to Windows startup registry
"""

import os
import sys
from pathlib import Path

try:
    import winreg
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

class WindowsStartup:
    """Manages Windows startup registry entries"""
    
    def __init__(self):
        """Initialize Windows startup manager"""
        self.app_name = "BreakGuard"
        self.registry_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    def is_windows(self) -> bool:
        """Check if running on Windows
        
        Returns:
            True if Windows, False otherwise
        """
        return WINDOWS_AVAILABLE and sys.platform == 'win32'
    
    def get_executable_path(self) -> str:
        """Get path to BreakGuard executable
        
        Returns:
            Full path to main.py with python executable
        """
        # Get main.py path
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_path = sys.executable
        else:
            # Running as Python script
            main_py = Path(__file__).parent.parent / 'main.py'
            python_exe = sys.executable
            # Use pythonw.exe to avoid console window
            if 'python.exe' in python_exe.lower():
                python_exe = python_exe.lower().replace('python.exe', 'pythonw.exe')
            app_path = f'"{python_exe}" "{main_py}"'
        
        return app_path
    
    def add_to_startup(self) -> bool:
        """Add BreakGuard to Windows startup
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_windows():
            print("Not running on Windows")
            return False
        
        try:
            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.registry_path,
                0,
                winreg.KEY_SET_VALUE
            )
            
            # Set the value
            app_path = self.get_executable_path()
            winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, app_path)
            
            # Close the key
            winreg.CloseKey(key)
            
            return True
        except Exception as e:
            print(f"Error adding to startup: {e}")
            return False
    
    def remove_from_startup(self) -> bool:
        """Remove BreakGuard from Windows startup
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_windows():
            print("Not running on Windows")
            return False
        
        try:
            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.registry_path,
                0,
                winreg.KEY_SET_VALUE
            )
            
            # Delete the value
            winreg.DeleteValue(key, self.app_name)
            
            # Close the key
            winreg.CloseKey(key)
            
            return True
        except FileNotFoundError:
            # Already not in startup
            return True
        except Exception as e:
            print(f"Error removing from startup: {e}")
            return False
    
    def is_in_startup(self) -> bool:
        """Check if BreakGuard is in Windows startup
        
        Returns:
            True if in startup, False otherwise
        """
        if not self.is_windows():
            return False
        
        try:
            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.registry_path,
                0,
                winreg.KEY_READ
            )
            
            # Try to read the value
            value, _ = winreg.QueryValueEx(key, self.app_name)
            
            # Close the key
            winreg.CloseKey(key)
            
            return bool(value)
        except FileNotFoundError:
            return False
        except Exception as e:
            print(f"Error checking startup: {e}")
            return False
    
    def toggle_startup(self, enable: bool) -> bool:
        """Enable or disable startup
        
        Args:
            enable: True to enable, False to disable
            
        Returns:
            True if successful, False otherwise
        """
        if enable:
            return self.add_to_startup()
        else:
            return self.remove_from_startup()
