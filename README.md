# BreakGuard

BreakGuard is a Windows 11 health-discipline application that enforces regular breaks during long working hours by locking the screen, turning off the monitor via API, and requiring secure two-step authentication to unlock.

It is designed for people who work 10–15+ hours continuously on computers and want a non-cheatable, habit-forming system to protect their health.

**Repository:** [https://github.com/ProgrammerNomad/BreakGuard](https://github.com/ProgrammerNomad/BreakGuard)

## Why BreakGuard?

Most reminders are easy to ignore.
BreakGuard forces you to take breaks.

- 🎨 **User-friendly GUI** - No command-line needed!
- ⏱️ Locks your screen after fixed intervals
- 🖥️ Turns off monitor via Tinxy API
- 🔐 Requires Google Authenticator + Face Verification to unlock
- 🔄 Survives reboot / power cut
- 🧠 Builds healthy work habits automatically

## Key Features

### Easy Setup Wizard

- Beautiful graphical setup wizard
- No technical knowledge required
- QR code displayed in-app for Google Authenticator
- Guided face registration with camera preview
- One-click Tinxy API configuration

### Time-Based Enforcement

- Hourly (or configurable) work intervals
- Warning notification before lock
- Forced fullscreen lock when time is over

### Secure Two-Step Unlock

**Google Authenticator (TOTP)**
- Offline support
- No internet required

**Face / Picture Verification**
- Uses system camera
- Offline face matching

### Monitor Control

- Integrates with Tinxy smart switch API (https://tinxyapi.pages.dev/)
- Turns monitor OFF via Tinxy device control
- Software-level backup monitor power off
- Monitor remains off until unlock is allowed

### Power-Safe Locking

- Auto-starts with Windows
- Lock screen appears even after reboot or power failure
- Runs before normal desktop usage

### Anti-Bypass Protection

- Fullscreen always-on-top lock
- Keyboard shortcut blocking (Alt+Tab, Alt+F4, etc.)
- Task Manager auto-close
- Limited emergency unlocks (optional)

### User-Friendly Interface

- System tray integration
- Graphical settings panel
- Visual timer and status indicators
- Accessible for non-technical users

## Designed For

- Developers
- Designers
- Remote workers
- Students

**Anyone suffering from:**
- Long sitting hours
- Eye strain
- Poor posture
- Burnout

## How It Works (Flow)

```
System Start / Resume
        ↓
BreakGuard Auto Launch
        ↓
Work Timer Running
        ↓
Warning Notification
        ↓
Monitor OFF (Tinxy API)
        ↓
Fullscreen Lock
        ↓
TOTP Verification
        ↓
Face Verification
        ↓
Unlock Allowed
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python |
| OS | Windows 11 |
| UI | Fullscreen (Tkinter / PyQt) |
| Auth | Google Authenticator (TOTP) |
| Face Verification | OpenCV |
| Monitor API | Tinxy REST API |
| API Calls | REST (HTTP) |
| Startup | Windows Registry |
| Packaging | PyInstaller |

## Configuration

All settings are managed via a simple config file:

```json
{
  "work_interval_minutes": 60,
  "warning_before_minutes": 5,
  "max_snooze": 1,
  "tinxy_api_key": "your_tinxy_bearer_token",
  "tinxy_device_id": "your_device_id",
  "tinxy_device_number": 1,
  "auth_enabled": true,
  "face_verification": true,
  "auto_start": true
}
```

### Tinxy API Setup

1. Install the Tinxy Mobile application
2. Login to the application
3. Click on the setting icon (top left on Android)
4. Getting Started

### For Non-Technical Users

We've made BreakGuard super easy to use! No command-line knowledge needed.

1. **Install Python** from [python.org](https://www.python.org/downloads/) (check "Add to PATH")
2. **Download BreakGuard** from GitHub
3. **Install dependencies**: Double-click `install.bat` (we'll create this)
4. **Run BreakGuard**: Double-click `run_breakguard.bat`
5. **Follow the Setup Wizard** - it's point-and-click easy!

📖 **Detailed guide for beginners**: See [QUICKSTART.md](QUICKSTART.md)

### For Developers

```bash
# Install dependencies
pip install -r requirements.txt

# Run setup wizard
python main.py --setup

# Start BreakGuard
python main.py
```

### What You'll See

1. **Setup Wizard** (first run):
   - Set your work/break schedule
   - Scan QR code with Google Authenticator app
   - Register your face (optional)
   - Configure Tinxy (optional)

2. **System Tray Icon**:
   - Right-click for controls
   - See time remaining
   - Access settings anytime

3. **Lock Screen** (at break time):
   - Fullscreen break notice
   - Enter 6-digit code from phone
   - Verify your face
   - Unlock and continue!

## Click on API Token
5. Click on Get Token
6. Copy and save the token in your config file
7. Get your device ID from the devices list

API Documentation: https://tinxyapi.pages.dev/

## Security Notes

- Works fully offline
- TOTP secrets stored encrypted locally
- Face data never leaves the system
- Designed for self-discipline, not military-grade OS security

> ⚠️ **Note:** Advanced users can bypass via Safe Mode or external boot.
> This is intentional — BreakGuard is about habit control, not system lockdown.

## Future Roadmap

- Daily / weekly break analytics
- Smartwatch step-based unlock
- Mobile companion app
- Guided stretch & eye-care prompts
- Cloud sync (optional)

## Project Philosophy

> "If willpower was enough, reminders would work.
> BreakGuard exists because discipline needs structure."

## License

MIT License — free to use, modify, and distribute.

## Contributing

Contributions are welcome:

- Feature ideas
- Security improvements
- UI/UX enhancements
- Documentation

Visit the repository at [github.com/ProgrammerNomad/BreakGuard](https://github.com/ProgrammerNomad/BreakGuard)

Open an issue or submit a pull request 🚀
