"""
Low-Level Keyboard Blocker
Uses Windows API hooks to block system shortcuts (Alt+Tab, Win+D, etc.)
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes
import threading
import atexit
import logging

logger = logging.getLogger(__name__)

# Windows API Constants
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105

# Virtual Key Codes
VK_TAB = 0x09
VK_ESCAPE = 0x1B
VK_LWIN = 0x5B
VK_RWIN = 0x5C
VK_DELETE = 0x2E
VK_F4 = 0x73

# Structure for keyboard hook
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", wintypes.ULONG)
    ]

# Function pointer type
HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

class KeyboardBlocker:
    """Blocks system keyboard shortcuts using low-level Windows hooks"""
    
    def __init__(self):
        self.hook_id = None
        self.hook_proc = HOOKPROC(self._hook_callback)
        self.is_blocking = False
        self.thread = None
        
        # Load user32.dll
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
    
    def start(self):
        """Start blocking keys in a separate thread"""
        if self.is_blocking:
            return
            
        self.is_blocking = True
        self.thread = threading.Thread(target=self._install_hook, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop blocking keys"""
        if not self.is_blocking:
            return
            
        self.is_blocking = False
        if self.hook_id:
            # Post a dummy message to wake up the message loop in the thread
            # so it can process the unhook
            self.user32.PostThreadMessageW(self.thread.ident, 0, 0, 0)
    
    def _install_hook(self):
        """Install the hook and run message loop"""
        # Get module handle
        h_mod = self.kernel32.GetModuleHandleW(None)
        
        # Set hook
        self.hook_id = self.user32.SetWindowsHookExW(
            WH_KEYBOARD_LL,
            self.hook_proc,
            h_mod,
            0
        )
        
        if not self.hook_id:
            logger.error(f"Failed to install keyboard hook: {ctypes.get_last_error()}")
            return
        
        # Message loop
        msg = wintypes.MSG()
        while self.is_blocking:
            # PeekMessage is non-blocking if no message, but we need to keep the loop alive
            # GetMessage blocks until a message arrives
            if self.user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageW(ctypes.byref(msg))
        
        # Unhook
        self.user32.UnhookWindowsHookEx(self.hook_id)
        self.hook_id = None
    
    def _hook_callback(self, nCode, wParam, lParam):
        """Callback function for keyboard events"""
        if nCode >= 0 and self.is_blocking:
            # Get key data
            kb_struct = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            vk_code = kb_struct.vkCode
            
            # Check for keys to block
            
            # Block Windows Keys (Start Menu, Win+D, Win+L, etc.)
            if vk_code in (VK_LWIN, VK_RWIN):
                return 1  # Block
            
            # Check modifier keys state
            alt_pressed = (self.user32.GetAsyncKeyState(0x12) & 0x8000) != 0
            ctrl_pressed = (self.user32.GetAsyncKeyState(0x11) & 0x8000) != 0
            
            # Block Alt+Tab
            if vk_code == VK_TAB and alt_pressed:
                return 1
            
            # Block Alt+Esc
            if vk_code == VK_ESCAPE and alt_pressed:
                return 1
            
            # Block Ctrl+Esc (Start Menu)
            if vk_code == VK_ESCAPE and ctrl_pressed:
                return 1
            
            # Block Alt+F4
            if vk_code == VK_F4 and alt_pressed:
                return 1
                
            # Attempt to block Task Manager (Ctrl+Shift+Esc)
            # Note: Ctrl+Alt+Del is protected by kernel and cannot be blocked
            shift_pressed = (self.user32.GetAsyncKeyState(0x10) & 0x8000) != 0
            if vk_code == VK_ESCAPE and ctrl_pressed and shift_pressed:
                return 1
        
        # Pass to next hook
        return self.user32.CallNextHookEx(self.hook_id, nCode, wParam, lParam)

if __name__ == "__main__":
    # Test the blocker
    import time
    logging.basicConfig(level=logging.INFO)
    logger.info("Blocking keys for 10 seconds...")
    blocker = KeyboardBlocker()
    blocker.start()
    try:
        time.sleep(10)
    finally:
        blocker.stop()
    logger.info("Unblocked")
