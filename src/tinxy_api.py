"""
Tinxy IoT API Integration
Controls smart devices during breaks (e.g., turn off monitor)
"""
from __future__ import annotations

import requests
import logging
import time
from typing import Dict, Optional, Any
from exceptions import TinxyAPIError, APIError

logger = logging.getLogger(__name__)

class TinxyAPI:
    """Tinxy smart device control"""
    
    BASE_URL = "https://cloud.tinxy.in/v2"
    DEFAULT_TIMEOUT = 5  # seconds
    MAX_RETRIES = 3
    RETRY_BACKOFF = 1  # seconds
    
    def __init__(self, api_key: str = "", device_id: str = "", timeout: int = None):
        """Initialize Tinxy API client
        
        Args:
            api_key: Tinxy API key from mobile app
            device_id: Device ID to control
            timeout: Request timeout in seconds (default: 5)
        """
        self.api_key = api_key
        self.device_id = device_id
        self.timeout = timeout or self.DEFAULT_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
    
    def _make_request_with_retry(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with retry logic
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional request arguments
            
        Returns:
            Response object or None on failure
        """
        # Add timeout to kwargs if not present
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        
        last_exception = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.request(method, url, **kwargs)
                
                # Don't retry on 4xx client errors (bad request, auth, etc.)
                if 400 <= response.status_code < 500:
                    logger.warning(f"Client error {response.status_code}: {response.text}")
                    return response
                
                # Return successful responses
                if response.status_code < 400:
                    return response
                
                # Log server errors and retry
                logger.warning(f"Server error {response.status_code} on attempt {attempt + 1}/{self.MAX_RETRIES}")
                
            except requests.exceptions.Timeout as e:
                last_exception = e
                logger.warning(f"Timeout on attempt {attempt + 1}/{self.MAX_RETRIES}: {e}")
                
            except requests.exceptions.ConnectionError as e:
                last_exception = e
                logger.warning(f"Connection error on attempt {attempt + 1}/{self.MAX_RETRIES}: {e}")
                
            except requests.exceptions.RequestException as e:
                last_exception = e
                logger.error(f"Request error on attempt {attempt + 1}/{self.MAX_RETRIES}: {e}")
                
            # Exponential backoff before retry
            if attempt < self.MAX_RETRIES - 1:
                sleep_time = self.RETRY_BACKOFF * (2 ** attempt)
                logger.debug(f"Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
        
        # All retries failed
        if last_exception:
            logger.error(f"All {self.MAX_RETRIES} retries failed: {last_exception}")
        return None
    
    def test_connection(self) -> bool:
        """Test API connection and credentials
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.api_key:
            logger.warning("No API key provided")
            return False
        
        response = self._make_request_with_retry('GET', f"{self.BASE_URL}/devices")
        
        if response and response.status_code == 200:
            # Validate response structure
            try:
                data = response.json()
                if 'devices' in data or 'status' in data:
                    return True
                logger.warning(f"Unexpected response format: {data}")
            except ValueError as e:
                logger.error(f"Invalid JSON response: {e}")
        
        return False
    
    def get_devices(self) -> Optional[list]:
        """Get list of all devices
        
        Returns:
            List of devices or None on error
        """
        response = self._make_request_with_retry('GET', f"{self.BASE_URL}/devices")
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                devices = data.get('devices', [])
                
                # Validate device structure
                if isinstance(devices, list):
                    return devices
                
                logger.warning(f"Unexpected devices format: {type(devices)}")
            except ValueError as e:
                logger.error(f"Invalid JSON response: {e}")
        
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
            logger.warning("No device ID provided")
            return None
        
        response = self._make_request_with_retry('GET', f"{self.BASE_URL}/devices/{device_id}")
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                
                # Validate response has device status
                if isinstance(data, dict) and ('status' in data or 'state' in data):
                    return data
                
                logger.warning(f"Unexpected device status format: {data}")
            except ValueError as e:
                logger.error(f"Invalid JSON response: {e}")
        
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
            logger.warning("No device ID provided")
            return False
        
        payload = {
            "device": device_number,
            "state": 1
        }
        
        response = self._make_request_with_retry(
            'POST',
            f"{self.BASE_URL}/devices/{device_id}/toggle",
            json=payload
        )
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                # Validate response indicates success
                if isinstance(data, dict) and data.get('status') in ['success', 'ok', True]:
                    logger.info(f"Device {device_id}:{device_number} turned ON")
                    return True
            except ValueError as e:
                logger.warning(f"Could not parse response: {e}")
                # If we got 200, assume success even if JSON parse fails
                return True
        
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
            logger.warning("No device ID provided")
            return False
        
        payload = {
            "device": device_number,
            "state": 0
        }
        
        response = self._make_request_with_retry(
            'POST',
            f"{self.BASE_URL}/devices/{device_id}/toggle",
            json=payload
        )
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                # Validate response indicates success
                if isinstance(data, dict) and data.get('status') in ['success', 'ok', True]:
                    logger.info(f"Device {device_id}:{device_number} turned OFF")
                    return True
            except ValueError as e:
                logger.warning(f"Could not parse response: {e}")
                # If we got 200, assume success even if JSON parse fails
                return True
        
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
