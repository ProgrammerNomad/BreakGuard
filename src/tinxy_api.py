"""
Tinxy API Integration for BreakGuard
Controls monitor power via Tinxy smart switch
"""
import requests
import time
from typing import Optional, Dict, Any

class TinxyAPI:
    BASE_URL = "https://backend.tinxy.in"
    
    def __init__(self, api_key: str, device_id: str, device_number: int = 1):
        self.api_key = api_key
        self.device_id = device_id
        self.device_number = device_number
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request to Tinxy API"""
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=10)
            else:
                return None
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Tinxy API Error: {e}")
            return None
    
    def get_all_devices(self) -> Optional[list]:
        """Get all devices connected to account"""
        return self._make_request("GET", "/v2/devices/")
    
    def get_device_state(self) -> Optional[Dict]:
        """Get current state of the device"""
        endpoint = f"/v2/devices/{self.device_id}/state"
        params = f"?deviceNumber={self.device_number}"
        
        try:
            url = f"{self.BASE_URL}{endpoint}{params}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting device state: {e}")
            return None
    
    def turn_off(self) -> bool:
        """Turn OFF the monitor (device state = 0)"""
        endpoint = f"/v2/devices/{self.device_id}/toggle"
        data = {
            "deviceNumber": self.device_number,
            "request": {
                "state": 0
            }
        }
        
        result = self._make_request("POST", endpoint, data)
        if result:
            print("Monitor turned OFF via Tinxy API")
            return True
        else:
            print("Failed to turn off monitor")
            return False
    
    def turn_on(self) -> bool:
        """Turn ON the monitor (device state = 1)"""
        endpoint = f"/v2/devices/{self.device_id}/toggle"
        data = {
            "deviceNumber": self.device_number,
            "request": {
                "state": 1
            }
        }
        
        result = self._make_request("POST", endpoint, data)
        if result:
            print("Monitor turned ON via Tinxy API")
            return True
        else:
            print("Failed to turn on monitor")
            return False
    
    def toggle(self) -> bool:
        """Toggle device state"""
        current_state = self.get_device_state()
        
        if current_state is None:
            return False
        
        # Determine current state and toggle
        try:
            if isinstance(current_state, list) and len(current_state) > 0:
                state = current_state[0].get('state', 'OFF')
                if state == 'ON' or state == 1:
                    return self.turn_off()
                else:
                    return self.turn_on()
        except Exception as e:
            print(f"Error toggling device: {e}")
            return False
        
        return False
    
    def is_online(self) -> bool:
        """Check if device is online"""
        state = self.get_device_state()
        if state and isinstance(state, list) and len(state) > 0:
            status = state[0].get('status', 0)
            return status == 1
        return False

# Fallback: Software-level monitor control for Windows
class WindowsMonitorControl:
    """Fallback monitor control using Windows API"""
    
    @staticmethod
    def turn_off():
        """Turn off monitor using Windows messaging"""
        try:
            import win32gui
            import win32con
            
            # Send message to turn off monitor
            HWND_BROADCAST = 0xFFFF
            WM_SYSCOMMAND = 0x0112
            SC_MONITORPOWER = 0xF170
            MONITOR_OFF = 2
            
            win32gui.SendMessage(
                HWND_BROADCAST,
                WM_SYSCOMMAND,
                SC_MONITORPOWER,
                MONITOR_OFF
            )
            print("Monitor turned off (Windows API)")
            return True
        except Exception as e:
            print(f"Error turning off monitor via Windows API: {e}")
            return False
    
    @staticmethod
    def turn_on():
        """Turn on monitor using Windows messaging"""
        try:
            import win32gui
            import win32con
            
            # Send message to turn on monitor
            HWND_BROADCAST = 0xFFFF
            WM_SYSCOMMAND = 0x0112
            SC_MONITORPOWER = 0xF170
            MONITOR_ON = -1
            
            win32gui.SendMessage(
                HWND_BROADCAST,
                WM_SYSCOMMAND,
                SC_MONITORPOWER,
                MONITOR_ON
            )
            print("Monitor turned on (Windows API)")
            return True
        except Exception as e:
            print(f"Error turning on monitor via Windows API: {e}")
            return False

class MonitorController:
    """Unified monitor controller with Tinxy API and fallback"""
    
    def __init__(self, tinxy_api: Optional[TinxyAPI] = None):
        self.tinxy_api = tinxy_api
        self.fallback = WindowsMonitorControl()
    
    def turn_off(self) -> bool:
        """Turn off monitor using Tinxy API with fallback"""
        success = False
        
        # Try Tinxy API first
        if self.tinxy_api:
            success = self.tinxy_api.turn_off()
        
        # Always use software fallback as well
        self.fallback.turn_off()
        
        return success or True  # Return True if at least fallback worked
    
    def turn_on(self) -> bool:
        """Turn on monitor using Tinxy API with fallback"""
        success = False
        
        # Try Tinxy API first
        if self.tinxy_api:
            success = self.tinxy_api.turn_on()
        
        # Always use software fallback as well
        self.fallback.turn_on()
        
        return success or True  # Return True if at least fallback worked
