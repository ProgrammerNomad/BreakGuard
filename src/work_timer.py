"""
Work Timer System for BreakGuard
Tracks work time and triggers break enforcement
"""
import time
import threading
from datetime import datetime, timedelta
from typing import Callable, Optional
import json
from pathlib import Path

class WorkTimer:
    def __init__(self, 
                 work_interval_minutes: int = 60,
                 warning_before_minutes: int = 5,
                 on_warning: Optional[Callable] = None,
                 on_lock: Optional[Callable] = None):
        
        self.work_interval = work_interval_minutes * 60  # Convert to seconds
        self.warning_before = warning_before_minutes * 60
        self.on_warning = on_warning
        self.on_lock = on_lock
        
        self.running = False
        self.paused = False
        self.start_time = None
        self.elapsed_time = 0
        self.timer_thread = None
        
        self.state_file = Path("data/timer_state.json")
        
        # Load previous state if exists
        self._load_state()
    
    def _load_state(self):
        """Load timer state from file (survives reboot)"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                
                saved_time = datetime.fromisoformat(state.get('start_time', ''))
                elapsed = (datetime.now() - saved_time).total_seconds()
                
                # If time has passed, calculate if we need to lock immediately
                if elapsed >= self.work_interval:
                    print("Break time exceeded during shutdown - locking now")
                    if self.on_lock:
                        threading.Timer(2, self.on_lock).start()
                else:
                    self.elapsed_time = elapsed
                    print(f"Restored timer state: {elapsed:.0f}s elapsed")
                
            except Exception as e:
                print(f"Error loading timer state: {e}")
    
    def _save_state(self):
        """Save timer state to file"""
        try:
            self.state_file.parent.mkdir(exist_ok=True)
            state = {
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'work_interval': self.work_interval,
                'elapsed': self.elapsed_time
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Error saving timer state: {e}")
    
    def start(self):
        """Start the work timer"""
        if self.running:
            return
        
        self.running = True
        self.start_time = datetime.now()
        
        self.timer_thread = threading.Thread(target=self._run_timer, daemon=True)
        self.timer_thread.start()
        
        print(f"Work timer started - {self.work_interval // 60} minutes until break")
    
    def _run_timer(self):
        """Internal timer loop"""
        warning_triggered = False
        
        while self.running:
            if not self.paused:
                current_time = time.time()
                
                # Calculate time remaining
                time_remaining = self.work_interval - self.elapsed_time
                
                # Trigger warning
                if time_remaining <= self.warning_before and not warning_triggered:
                    warning_triggered = True
                    print(f"Warning: Break in {self.warning_before // 60} minutes")
                    if self.on_warning:
                        self.on_warning()
                
                # Trigger lock
                if time_remaining <= 0:
                    print("Work interval completed - triggering lock")
                    self.running = False
                    if self.on_lock:
                        self.on_lock()
                    break
                
                # Save state periodically
                if int(self.elapsed_time) % 60 == 0:  # Every minute
                    self._save_state()
                
                time.sleep(1)
                self.elapsed_time += 1
            else:
                time.sleep(1)
    
    def pause(self):
        """Pause the timer"""
        self.paused = True
        print("Timer paused")
    
    def resume(self):
        """Resume the timer"""
        self.paused = False
        print("Timer resumed")
    
    def stop(self):
        """Stop the timer"""
        self.running = False
        self._save_state()
        print("Timer stopped")
    
    def reset(self):
        """Reset the timer"""
        self.stop()
        self.elapsed_time = 0
        self.start_time = None
        
        # Clear saved state
        if self.state_file.exists():
            self.state_file.unlink()
        
        print("Timer reset")
    
    def get_time_remaining(self) -> int:
        """Get remaining time in seconds"""
        return max(0, self.work_interval - self.elapsed_time)
    
    def get_time_remaining_formatted(self) -> str:
        """Get remaining time as formatted string"""
        remaining = self.get_time_remaining()
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        seconds = remaining % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def get_elapsed_time(self) -> int:
        """Get elapsed time in seconds"""
        return int(self.elapsed_time)
    
    def get_progress_percentage(self) -> float:
        """Get progress as percentage (0-100)"""
        return (self.elapsed_time / self.work_interval) * 100 if self.work_interval > 0 else 0
