# BreakGuard Project Structure

```
BreakGuard/
│
├── main.py                    # Main application entry point
├── config.json                # User configuration file
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── SETUP.md                   # Setup and usage guide
│
├── src/                       # Source code
│   ├── config_manager.py      # Configuration management
│   ├── tinxy_api.py          # Tinxy API integration
│   ├── work_timer.py         # Work timer system
│   ├── totp_auth.py          # TOTP authentication
│   ├── face_verification.py  # Face verification
│   ├── lock_screen.py        # Lock screen UI
│   └── windows_startup.py    # Windows startup integration
│
└── data/                      # Runtime data (created automatically)
    ├── key.key               # Encryption key
    ├── secrets.enc           # Encrypted secrets
    ├── face_data.pkl         # Face encoding
    ├── reference_face.jpg    # Reference face image
    ├── totp_qr.png          # TOTP QR code
    └── timer_state.json      # Timer state
```

## Module Overview

### main.py
- Application entry point
- Orchestrates all components
- System tray integration
- Setup wizard

### config_manager.py
- Loads and saves configuration
- Encrypts sensitive data (API keys, TOTP secrets)
- Manages config.json

### tinxy_api.py
- Tinxy REST API client
- Monitor ON/OFF control
- Device state management
- Windows API fallback

### work_timer.py
- Tracks work time
- Triggers warnings
- Triggers lock events
- Persists state across reboots

### totp_auth.py
- Google Authenticator compatible TOTP
- QR code generation
- Code verification
- Setup wizard

### face_verification.py
- Face detection using OpenCV
- Face encoding and matching
- Camera capture
- Offline verification

### lock_screen.py
- Fullscreen lock UI
- TOTP code entry
- Face verification integration
- Anti-bypass protection

### windows_startup.py
- Registry-based startup
- Task Scheduler integration
- Auto-start configuration

## Data Flow

```
main.py
  ├─> ConfigManager ────> config.json
  ├─> TinxyAPI ──────────> Tinxy Backend API
  ├─> WorkTimer
  │     ├─> on_warning ──> Notification
  │     └─> on_lock ─────> LockScreen
  ├─> TOTPAuth
  │     └─> verify ──────> Google Authenticator
  └─> FaceVerification
        └─> verify ──────> OpenCV
```

## Component Interactions

1. **Startup**
   - main.py loads ConfigManager
   - Initializes all components
   - Starts WorkTimer
   - Creates system tray icon

2. **Work Session**
   - WorkTimer counts down
   - Saves state periodically
   - Shows warning notification

3. **Break Time**
   - WorkTimer triggers on_lock
   - TinxyAPI turns off monitor
   - LockScreen appears fullscreen

4. **Unlock Process**
   - User enters TOTP code
   - TOTPAuth verifies code
   - User verifies face (optional)
   - FaceVerification checks match
   - Monitor turns back on
   - Timer resets and restarts

## Security Architecture

```
Sensitive Data:
  ├─> TOTP Secret
  │     └─> Encrypted with Fernet
  │         └─> Stored in data/secrets.enc
  │
  ├─> Tinxy API Key  
  │     └─> Encrypted with Fernet
  │         └─> Stored in data/secrets.enc
  │
  └─> Face Encoding
        └─> Pickled numpy array
            └─> Stored in data/face_data.pkl

Encryption Key:
  └─> data/key.key (generated once)
```

## Execution Modes

### Normal Mode
```bash
python main.py
```
- Runs with existing configuration
- Starts work timer
- System tray interface

### Setup Mode
```bash
python main.py --setup
```
- Interactive setup wizard
- Configure all features
- Test authentication

## Future Enhancements

### Planned Features
- Settings GUI
- Break analytics dashboard
- Multiple work profiles
- Cloud backup (optional)
- Mobile app companion
- Smartwatch integration
- Guided stretching exercises

### Potential Modules
- `analytics.py` - Track break history and patterns
- `settings_ui.py` - GUI for configuration
- `cloud_sync.py` - Optional cloud backup
- `exercises.py` - Guided break activities
- `notifications.py` - Advanced notification system
