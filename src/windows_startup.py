"""
Windows Startup Integration for BreakGuard
Auto-start with Windows using Registry
"""
import winreg
import os
import sys
from pathlib import Path

class WindowsStartup:
    """Manage Windows startup integration"""
    
    # Registry key for startup programs
    STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    APP_NAME = "BreakGuard"
    
    @staticmethod
    def get_executable_path() -> str:
        """Get the path to the current executable or script"""
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            return sys.executable
        else:
            # Running as Python script
            script_path = os.path.abspath(sys.argv[0])
            python_path = sys.executable
            return f'"{python_path}" "{script_path}"'
    
    @staticmethod
    def is_enabled() -> bool:
        """Check if BreakGuard is set to run at startup"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                WindowsStartup.STARTUP_KEY,
                0,
                winreg.KEY_READ
            )
            
            try:
                value, _ = winreg.QueryValueEx(key, WindowsStartup.APP_NAME)
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
                
        except Exception as e:
            print(f"Error checking startup status: {e}")
            return False
    
    @staticmethod
    def enable() -> bool:
        """Enable BreakGuard to run at Windows startup"""
        try:
            executable_path = WindowsStartup.get_executable_path()
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                WindowsStartup.STARTUP_KEY,
                0,
                winreg.KEY_SET_VALUE
            )
            
            winreg.SetValueEx(
                key,
                WindowsStartup.APP_NAME,
                0,
                winreg.REG_SZ,
                executable_path
            )
            
            winreg.CloseKey(key)
            print(f"✓ BreakGuard enabled at startup")
            print(f"  Path: {executable_path}")
            return True
            
        except Exception as e:
            print(f"Error enabling startup: {e}")
            return False
    
    @staticmethod
    def disable() -> bool:
        """Disable BreakGuard from running at Windows startup"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                WindowsStartup.STARTUP_KEY,
                0,
                winreg.KEY_SET_VALUE
            )
            
            try:
                winreg.DeleteValue(key, WindowsStartup.APP_NAME)
                print("✓ BreakGuard disabled from startup")
            except FileNotFoundError:
                print("BreakGuard was not in startup")
            
            winreg.CloseKey(key)
            return True
            
        except Exception as e:
            print(f"Error disabling startup: {e}")
            return False
    
    @staticmethod
    def get_status() -> dict:
        """Get detailed startup status"""
        is_enabled = WindowsStartup.is_enabled()
        
        status = {
            'enabled': is_enabled,
            'app_name': WindowsStartup.APP_NAME,
            'registry_key': WindowsStartup.STARTUP_KEY
        }
        
        if is_enabled:
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    WindowsStartup.STARTUP_KEY,
                    0,
                    winreg.KEY_READ
                )
                value, _ = winreg.QueryValueEx(key, WindowsStartup.APP_NAME)
                status['path'] = value
                winreg.CloseKey(key)
            except:
                pass
        
        return status

class TaskSchedulerStartup:
    """
    Alternative: Use Windows Task Scheduler for more robust startup
    This runs before user login and survives more boot scenarios
    """
    
    @staticmethod
    def create_startup_task() -> bool:
        """Create a Windows Task Scheduler task for startup"""
        try:
            import subprocess
            
            # Get executable path
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = os.path.abspath(sys.argv[0])
            
            # Create XML for task
            task_xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>BreakGuard Health Discipline Application</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>false</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{exe_path}</Command>
    </Exec>
  </Actions>
</Task>'''
            
            # Save XML to temp file
            temp_xml = Path("data") / "breakguard_task.xml"
            temp_xml.parent.mkdir(exist_ok=True)
            
            with open(temp_xml, 'w', encoding='utf-16') as f:
                f.write(task_xml)
            
            # Create task using schtasks
            result = subprocess.run(
                ['schtasks', '/Create', '/TN', 'BreakGuard', 
                 '/XML', str(temp_xml), '/F'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✓ Task Scheduler entry created")
                temp_xml.unlink()  # Clean up temp file
                return True
            else:
                print(f"Error creating task: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error creating Task Scheduler entry: {e}")
            return False
    
    @staticmethod
    def delete_startup_task() -> bool:
        """Delete the Windows Task Scheduler task"""
        try:
            import subprocess
            
            result = subprocess.run(
                ['schtasks', '/Delete', '/TN', 'BreakGuard', '/F'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✓ Task Scheduler entry deleted")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error deleting task: {e}")
            return False
    
    @staticmethod
    def is_task_enabled() -> bool:
        """Check if the task exists"""
        try:
            import subprocess
            
            result = subprocess.run(
                ['schtasks', '/Query', '/TN', 'BreakGuard'],
                capture_output=True,
                text=True
            )
            
            return result.returncode == 0
            
        except Exception as e:
            return False
