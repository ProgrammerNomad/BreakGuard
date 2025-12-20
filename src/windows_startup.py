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

try:
    import win32com.client
    from win32com.shell import shell, shellcon
    from win32com.propsys import propsys, pscon
    PYWIN32_AVAILABLE = True
except ImportError:
    PYWIN32_AVAILABLE = False

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

    def create_shortcut(self) -> bool:
        """Create Start Menu shortcut with AUMID and Icon
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_windows() or not PYWIN32_AVAILABLE:
            return False

        try:
            # Get Start Menu path
            start_menu = shell.SHGetFolderPath(0, shellcon.CSIDL_PROGRAMS, None, 0)
            shortcut_path = os.path.join(start_menu, "BreakGuard.lnk")
            
            # Paths
            main_py = Path(__file__).parent.parent / 'main.py'
            assets_dir = Path(__file__).parent.parent / 'assets'
            icon_path = assets_dir / 'logo.ico'
            
            # Target
            if getattr(sys, 'frozen', False):
                target = sys.executable
                args = ""
            else:
                target = sys.executable
                if 'python.exe' in target.lower():
                    target = target.lower().replace('python.exe', 'pythonw.exe')
                args = f'"{main_py}"'
            
            # Create shortcut
            wscript = win32com.client.Dispatch("WScript.Shell")
            shortcut = wscript.CreateShortcut(shortcut_path)
            shortcut.TargetPath = target
            shortcut.Arguments = args
            shortcut.WorkingDirectory = str(Path(__file__).parent.parent)
            if icon_path.exists():
                shortcut.IconLocation = str(icon_path)
            shortcut.Description = "BreakGuard - Your Health Guardian"
            shortcut.Save()
            
            # Set AUMID using Property Store
            store = propsys.SHGetPropertyStoreFromParsingName(
                shortcut_path, 
                None, 
                shellcon.GPS_READWRITE, 
                propsys.IID_IPropertyStore
            )
            key = pscon.PKEY_AppUserModel_ID
            propvar = propsys.PROPVARIANTType(self.app_name) # "BreakGuard"
            store.SetValue(key, propvar)
            store.Commit()
            
            return True
            
        except Exception as e:
            print(f"Error creating shortcut: {e}")
            return False
