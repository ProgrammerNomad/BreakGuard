"""
Custom Exceptions for BreakGuard
Defines application-specific exceptions for better error handling
"""


class BreakGuardError(Exception):
    """Base exception for all BreakGuard errors"""
    pass


class ConfigError(BreakGuardError):
    """Configuration-related errors"""
    def __init__(self, message: str, config_key: str = None):
        self.config_key = config_key
        super().__init__(message)


class AuthError(BreakGuardError):
    """Authentication-related errors"""
    pass


class TOTPError(AuthError):
    """TOTP authentication errors"""
    pass


class FaceVerificationError(AuthError):
    """Face verification errors"""
    pass


class CameraError(BreakGuardError):
    """Camera access and operation errors"""
    def __init__(self, message: str, camera_index: int = None):
        self.camera_index = camera_index
        super().__init__(message)


class APIError(BreakGuardError):
    """External API errors"""
    def __init__(self, message: str, api_name: str = None, status_code: int = None):
        self.api_name = api_name
        self.status_code = status_code
        super().__init__(message)


class TinxyAPIError(APIError):
    """Tinxy API specific errors"""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message, api_name="Tinxy", status_code=status_code)


class ValidationError(BreakGuardError):
    """Data validation errors"""
    def __init__(self, message: str, field_name: str = None, invalid_value=None):
        self.field_name = field_name
        self.invalid_value = invalid_value
        super().__init__(message)


class StateError(BreakGuardError):
    """Invalid state transition errors"""
    def __init__(self, message: str, current_state: str = None, attempted_state: str = None):
        self.current_state = current_state
        self.attempted_state = attempted_state
        super().__init__(message)
