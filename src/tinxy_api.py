"""
Tinxy IoT API Integration
Controls smart devices during breaks (e.g., turn off monitor)
"""

import requests
from typing import Dict, Optional, Any

class TinxyAPI:
    """Tinxy smart device control"""
    
    BASE_URL = "https://cloud.tinxy.in/v2"
    
    def __init__(self, api_key: str = "", device_id: str = ""):
        """Initialize Tinxy API client
        
        Args:
            api_key: Tinxy API key from mobile app
            device_id: Device ID to control
        """
        self.api_key = api_key
        self.device_id = device_id
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def test_connection(self) -> bool:
        """Test API connection and credentials
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.api_key:
            return False
        
        try:
            response = self.session.get(f"{self.BASE_URL}/devices")
            return response.status_code == 200
        except Exception as e:
            print(f"Tinxy connection error: {e}")
            return False
    
    def get_devices(self) -> Optional[list]:
        """Get list of all devices
        
        Returns:
            List of devices or None on error
        """
        try:
            response = self.session.get(f"{self.BASE_URL}/devices")
            if response.status_code == 200:
                return response.json().get('devices', [])
        except Exception as e:
            print(f"Error getting devices: {e}")
        
        return None
    
    def get_device_status(self, device_id: str = None) -> Optional[Dict[str, Any]]:
        """Get status of a specific device
        
        Args:
            device_id: Device ID. If None, uses instance device_id.
            
        Returns:
            Device status dict or None
        """
        device_id = device_id or self.device_id
        
        if not device_id:
            return None
        
        try:
            response = self.session.get(f"{self.BASE_URL}/devices/{device_id}")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error getting device status: {e}")
        
        return None
    
    def turn_on(self, device_number: int = 1, device_id: str = None) -> bool:
        """Turn on a device
        
        Args:
            device_number: Device number (1-4 for 4-gang switches)
            device_id: Device ID. If None, uses instance device_id.
            
        Returns:
            True if successful, False otherwise
        """
        device_id = device_id or self.device_id
        
        if not device_id:
            return False
        
        try:
            payload = {
                "device": device_number,
                "state": 1
            }
            response = self.session.post(
                f"{self.BASE_URL}/devices/{device_id}/toggle",
                json=payload
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error turning on device: {e}")
            return False
    
    def turn_off(self, device_number: int = 1, device_id: str = None) -> bool:
        """Turn off a device
        
        Args:
            device_number: Device number (1-4 for 4-gang switches)
            device_id: Device ID. If None, uses instance device_id.
            
        Returns:
            True if successful, False otherwise
        """
        device_id = device_id or self.device_id
        
        if not device_id:
            return False
        
        try:
            payload = {
                "device": device_number,
                "state": 0
            }
            response = self.session.post(
                f"{self.BASE_URL}/devices/{device_id}/toggle",
                json=payload
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error turning off device: {e}")
            return False
    
    def toggle(self, device_number: int = 1, device_id: str = None) -> bool:
        """Toggle a device (on/off)
        
        Args:
            device_number: Device number (1-4 for 4-gang switches)
            device_id: Device ID. If None, uses instance device_id.
            
        Returns:
            True if successful, False otherwise
        """
        device_id = device_id or self.device_id
        
        if not device_id:
            return False
        
        try:
            payload = {
                "device": device_number
            }
            response = self.session.post(
                f"{self.BASE_URL}/devices/{device_id}/toggle",
                json=payload
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error toggling device: {e}")
            return False
    
    def set_brightness(self, brightness: int, device_number: int = 1, device_id: str = None) -> bool:
        """Set brightness for dimmable devices
        
        Args:
            brightness: Brightness level (0-100)
            device_number: Device number
            device_id: Device ID. If None, uses instance device_id.
            
        Returns:
            True if successful, False otherwise
        """
        device_id = device_id or self.device_id
        
        if not device_id:
            return False
        
        # Clamp brightness to valid range
        brightness = max(0, min(100, brightness))
        
        try:
            payload = {
                "device": device_number,
                "brightness": brightness
            }
            response = self.session.post(
                f"{self.BASE_URL}/devices/{device_id}/brightness",
                json=payload
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error setting brightness: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if Tinxy is properly configured
        
        Returns:
            True if API key and device ID are set, False otherwise
        """
        return bool(self.api_key and self.device_id)
    
    def update_credentials(self, api_key: str, device_id: str) -> None:
        """Update API credentials
        
        Args:
            api_key: New API key
            device_id: New device ID
        """
        self.api_key = api_key
        self.device_id = device_id
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}'
        })
