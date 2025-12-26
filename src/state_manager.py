"""
Application State Management
Centralized state machine for BreakGuard
"""
from __future__ import annotations

from enum import Enum, auto
from typing import Optional, Callable
import logging
import json
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class AppState(Enum):
    """Application states"""
    IDLE = auto()           # Timer not running
    WORKING = auto()        # Work session in progress
    WARNING = auto()        # Warning dialog shown
    LOCKED = auto()         # Lock screen active (break time)
    PAUSED = auto()         # Timer manually paused
    SETUP = auto()          # Setup wizard running


class StateTransitionError(Exception):
    """Raised when an invalid state transition is attempted"""
    pass


class StateManager:
    """Manages application state and valid transitions"""
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        AppState.IDLE: [AppState.WORKING, AppState.SETUP],
        AppState.WORKING: [AppState.WARNING, AppState.PAUSED, AppState.IDLE],
        AppState.WARNING: [AppState.LOCKED, AppState.WORKING, AppState.IDLE],
        AppState.LOCKED: [AppState.IDLE, AppState.WORKING],
        AppState.PAUSED: [AppState.WORKING, AppState.IDLE],
        AppState.SETUP: [AppState.IDLE, AppState.WORKING]
    }
    
    def __init__(self, initial_state: AppState = AppState.IDLE, auto_persist: bool = True, state_file: Optional[str] = None):
        """Initialize state manager
        
        Args:
            initial_state: Starting application state
            auto_persist: Automatically save state on transitions
            state_file: Path to state file (default: data/app_state.json)
        """
        self._current_state = initial_state
        self._previous_state: Optional[AppState] = None
        self._state_callbacks: dict[AppState, list[Callable]] = {
            state: [] for state in AppState
        }
        self._auto_persist = auto_persist
        
        # Use AppData location for state file
        if state_file is None:
            from path_utils import get_data_dir
            state_file = str(get_data_dir() / "app_state.json")
        self._state_file = state_file
        
        self._additional_data: dict = {}  # Store extra state data (timers, counters, etc.)
        logger.info(f"State manager initialized with state: {initial_state.name}")
    
    @property
    def current_state(self) -> AppState:
        """Get current application state"""
        return self._current_state
    
    @property
    def previous_state(self) -> Optional[AppState]:
        """Get previous application state"""
        return self._previous_state
    
    def can_transition_to(self, new_state: AppState) -> bool:
        """Check if transition to new state is valid
        
        Args:
            new_state: Target state
            
        Returns:
            True if transition is valid
        """
        return new_state in self.VALID_TRANSITIONS.get(self._current_state, [])
    
    def transition_to(self, new_state: AppState, force: bool = False) -> bool:
        """Transition to new state
        
        Args:
            new_state: Target state
            force: Force transition even if invalid
            
        Returns:
            True if transition successful
            
        Raises:
            StateTransitionError: If transition is invalid and not forced
        """
        if not force and not self.can_transition_to(new_state):
            error_msg = f"Invalid state transition: {self._current_state.name} -> {new_state.name}"
            logger.error(error_msg)
            raise StateTransitionError(error_msg)
        
        old_state = self._current_state
        self._previous_state = old_state
        self._current_state = new_state
        
        logger.info(f"State transition: {old_state.name} -> {new_state.name}")
        
        # Auto-persist state if enabled
        if self._auto_persist:
            self.save_state()
        
        # Trigger callbacks for new state
        self._trigger_callbacks(new_state)
        
        return True
    
    def register_callback(self, state: AppState, callback: Callable):
        """Register callback to be called when entering a state
        
        Args:
            state: State to watch
            callback: Function to call when state is entered
        """
        if callback not in self._state_callbacks[state]:
            self._state_callbacks[state].append(callback)
            logger.debug(f"Registered callback for state: {state.name}")
    
    def unregister_callback(self, state: AppState, callback: Callable):
        """Unregister callback for a state
        
        Args:
            state: State to unwatch
            callback: Function to remove
        """
        if callback in self._state_callbacks[state]:
            self._state_callbacks[state].remove(callback)
            logger.debug(f"Unregistered callback for state: {state.name}")
    
    def _trigger_callbacks(self, state: AppState):
        """Trigger all callbacks for a state
        
        Args:
            state: State that was entered
        """
        for callback in self._state_callbacks[state]:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in state callback for {state.name}: {e}", exc_info=True)
    
    def is_state(self, state: AppState) -> bool:
        """Check if current state matches given state
        
        Args:
            state: State to check
            
        Returns:
            True if current state matches
        """
        return self._current_state == state
    
    def is_working(self) -> bool:
        """Check if in working state"""
        return self._current_state == AppState.WORKING
    
    def is_locked(self) -> bool:
        """Check if in locked state"""
        return self._current_state == AppState.LOCKED
    
    def is_paused(self) -> bool:
        """Check if in paused state"""
        return self._current_state == AppState.PAUSED
    
    def get_state_name(self) -> str:
        """Get human-readable name of current state"""
        return self._current_state.name
    
    def set_data(self, key: str, value: Any):
        """Store additional state data
        
        Args:
            key: Data key
            value: Data value (must be JSON serializable)
        """
        self._additional_data[key] = value
        if self._auto_persist:
            self.save_state()
    
    def get_data(self, key: str, default=None):
        """Retrieve additional state data
        
        Args:
            key: Data key
            default: Default value if key not found
            
        Returns:
            Stored value or default
        """
        return self._additional_data.get(key, default)
    
    def save_state(self) -> bool:
        """Save current state to file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure data directory exists
            Path(self._state_file).parent.mkdir(parents=True, exist_ok=True)
            
            state_data = {
                "current_state": self._current_state.name,
                "previous_state": self._previous_state.name if self._previous_state else None,
                "timestamp": datetime.now().isoformat(),
                "additional_data": self._additional_data
            }
            
            with open(self._state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            logger.debug(f"State saved to {self._state_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save state: {e}", exc_info=True)
            return False
    
    def load_state(self) -> bool:
        """Load state from file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not Path(self._state_file).exists():
                logger.info("No saved state file found")
                return False
            
            with open(self._state_file, 'r') as f:
                state_data = json.load(f)
            
            # Restore state
            current_state_name = state_data.get("current_state")
            if current_state_name:
                self._current_state = AppState[current_state_name]
            
            previous_state_name = state_data.get("previous_state")
            if previous_state_name:
                self._previous_state = AppState[previous_state_name]
            
            # Restore additional data
            self._additional_data = state_data.get("additional_data", {})
            
            timestamp = state_data.get("timestamp", "unknown")
            logger.info(f"State loaded from {self._state_file} (saved at {timestamp})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load state: {e}", exc_info=True)
            return False
    
    def clear_state(self) -> bool:
        """Clear saved state file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if Path(self._state_file).exists():
                Path(self._state_file).unlink()
                logger.info(f"State file deleted: {self._state_file}")
            self._additional_data.clear()
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear state: {e}", exc_info=True)
            return False
    
    def __repr__(self) -> str:
        return f"StateManager(current={self._current_state.name}, previous={self._previous_state.name if self._previous_state else 'None'})"


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    # Create state manager
    state_mgr = StateManager()
    
    # Register callbacks
    def on_working():
        print("Entered WORKING state - start timer")
    
    def on_locked():
        print("Entered LOCKED state - show lock screen")
    
    state_mgr.register_callback(AppState.WORKING, on_working)
    state_mgr.register_callback(AppState.LOCKED, on_locked)
    
    # Test transitions
    print(f"Initial: {state_mgr}")
    
    state_mgr.transition_to(AppState.WORKING)
    print(f"After work start: {state_mgr}")
    
    state_mgr.transition_to(AppState.WARNING)
    print(f"After warning: {state_mgr}")
    
    state_mgr.transition_to(AppState.LOCKED)
    print(f"After lock: {state_mgr}")
    
    state_mgr.transition_to(AppState.IDLE)
    print(f"After unlock: {state_mgr}")
    
    # Test invalid transition
    try:
        state_mgr.transition_to(AppState.LOCKED)  # Can't go directly from IDLE to LOCKED
    except StateTransitionError as e:
        print(f"Caught expected error: {e}")
