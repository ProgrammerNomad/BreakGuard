# BreakGuard Setup and Usage Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. First-Time Setup

Run the setup wizard to configure BreakGuard:

```bash
python main.py --setup
```

The setup wizard will guide you through:
- Work interval configuration
- Google Authenticator (TOTP) setup
- Face verification registration
- Tinxy API configuration (optional)

### 3. Run BreakGuard

```bash
python main.py
```

BreakGuard will:
- Start in the system tray
- Begin timing your work session
- Lock the screen when it's break time
- Require authentication to unlock

## Configuration

All settings are stored in `config.json`:

```json
{
  "work_interval_minutes": 60,
  "warning_before_minutes": 5,
  "max_snooze": 1,
  "tinxy_api_key": "",
  "tinxy_device_id": "",
  "tinxy_device_number": 1,
  "auth_enabled": true,
  "face_verification": true,
  "auto_start": true,
  "totp_secret": ""
}
```

### Key Settings

- `work_interval_minutes`: How long before enforcing a break (default: 60)
- `warning_before_minutes`: Warning notification before lock (default: 5)
- `auth_enabled`: Enable TOTP authentication (default: true)
- `face_verification`: Enable face verification (default: true)
- `auto_start`: Start with Windows (default: true)

## Google Authenticator Setup

1. Run setup wizard: `python main.py --setup`
2. A QR code will be saved to `data/totp_qr.png`
3. Open Google Authenticator on your phone
4. Scan the QR code
5. The app will show a 6-digit code that changes every 30 seconds
6. Use this code to unlock during breaks

**Manual Entry:** If you can't scan the QR code, the setup will display the secret key which you can enter manually in the app.

## Face Verification Setup

1. During setup, choose to enable face verification
2. Position your face in front of the camera
3. Press SPACE to capture
4. Your face data is saved locally (never leaves your computer)

## Tinxy API Setup

### Getting Your API Key

1. Install Tinxy Mobile app
2. Login to your account
3. Tap Settings icon (top left)
4. Tap "API Token"
5. Tap "Get Token"
6. Copy the token

### Getting Device ID

Run this Python script to list your devices:

```python
import requests

api_key = "YOUR_API_KEY_HERE"
headers = {"Authorization": f"Bearer {api_key}"}

response = requests.get("https://backend.tinxy.in/v2/devices/", headers=headers)
devices = response.json()

for device in devices:
    print(f"Name: {device['name']}")
    print(f"ID: {device['_id']}")
    print(f"Devices: {device['devices']}")
    print("---")
```

## System Tray Controls

Right-click the BreakGuard icon in the system tray:

- **Time Remaining**: Shows time until next break
- **Pause Timer**: Temporarily pause the timer
- **Resume Timer**: Resume a paused timer
- **Reset Timer**: Reset and restart the timer
- **Settings**: Open settings (coming soon)
- **Exit**: Close BreakGuard

## Windows Startup

BreakGuard automatically configures itself to start with Windows if `auto_start` is enabled in config.json.

To manually configure:

```python
from src.windows_startup import WindowsStartup

# Enable startup
WindowsStartup.enable()

# Disable startup
WindowsStartup.disable()

# Check status
print(WindowsStartup.is_enabled())
```

## Data Storage

BreakGuard stores data locally in the `data/` directory:

- `key.key`: Encryption key for sensitive data
- `secrets.enc`: Encrypted TOTP secret and API key
- `face_data.pkl`: Face verification encoding
- `reference_face.jpg`: Reference face image
- `totp_qr.png`: TOTP QR code
- `timer_state.json`: Timer state (survives reboot)

## Security Notes

- All data is stored locally and encrypted
- TOTP secrets are encrypted using Fernet (symmetric encryption)
- Face data never leaves your computer
- Tinxy API key is encrypted
- No internet connection required for TOTP or face verification

## Troubleshooting

### Camera Not Working

- Check if another application is using the camera
- Try a different camera index (0, 1, 2, etc.)
- Make sure you have webcam permissions

### TOTP Code Not Working

- Make sure your system clock is accurate
- TOTP codes expire every 30 seconds
- Check that you're using the correct secret in Google Authenticator

### Tinxy API Errors

- Verify your API key is correct
- Check device ID matches your device
- Ensure device number is correct (usually 1)
- Check internet connection

### Monitor Not Turning Off

- Tinxy API requires internet connection
- Software fallback may not work on all systems
- Check if your monitor supports DPMS

## Building Executable

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico main.py
```

The executable will be in the `dist/` folder.

## Uninstalling

1. Exit BreakGuard from system tray
2. Disable Windows startup:
   ```python
   from src.windows_startup import WindowsStartup
   WindowsStartup.disable()
   ```
3. Delete the BreakGuard folder

## Support

For issues, feature requests, or contributions, visit:
https://github.com/ProgrammerNomad/BreakGuard

## License

MIT License - See LICENSE file
