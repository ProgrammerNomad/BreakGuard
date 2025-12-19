# 🛡️ BreakGuard - Your Health Guardian

**Enforce healthy work breaks with unbreakable discipline.**

BreakGuard is a Windows application that forces you to take regular breaks during long working hours. It locks your screen, controls your monitor via IoT, and requires secure two-factor authentication to unlock — making it impossible to skip breaks.

Perfect for developers, designers, remote workers, and anyone who works 10+ hours continuously and struggles with self-discipline.

**Repository:** [https://github.com/ProgrammerNomad/BreakGuard](https://github.com/ProgrammerNomad/BreakGuard)

---

## 🎯 Why BreakGuard?

**The Problem:** You know breaks are important, but willpower fails when deadlines loom. Notifications get dismissed. Timers get ignored. Your health suffers.

**The Solution:** BreakGuard doesn't ask — it enforces.

### ✨ Key Features

- 🎨 **Beautiful Modern UI** - PyQt6 interface with Material Design
- ⏱️ **Automatic Lock** - Screen locks after your configured work interval
- 🔐 **Two-Factor Unlock** - Google Authenticator (6-digit OTP) + Face verification
- 🖥️ **Monitor Control** - Turns off monitor via Tinxy IoT API
- 🔄 **Survives Reboots** - Auto-starts with Windows, enforces breaks even after restart
- 🚫 **Anti-Bypass** - Blocks Alt+Tab, Alt+F4, Task Manager during lock
- 🧠 **Builds Habits** - Consistent enforcement creates lasting behavior change
- 📊 **Configurable** - Set your own work/break intervals

## 🚀 How It Works

```
1. Install & Setup (one-time)
   ├─ Run setup wizard
   ├─ Set work interval (e.g., 60 minutes)
   ├─ Scan QR with Google Authenticator
   ├─ Register your face (optional)
   └─ Configure Tinxy IoT (optional)

2. BreakGuard Runs in Background
   ├─ System tray icon shows status
   ├─ Timer counts down work interval
   └─ Auto-starts with Windows

3. Break Time Arrives
   ├─ Warning notification (5 mins before)
   ├─ Monitor turns off (via Tinxy)
   ├─ Fullscreen lock appears
   └─ No way to skip or dismiss

4. Unlock Process
   ├─ Enter 6-digit code from Google Authenticator
   ├─ Face verification via camera
   └─ Unlock granted, work timer restarts
```

---

## 💪 Who Needs This?

### Perfect For:
- 💻 **Software Developers** - Long coding sessions
- 🎨 **Designers** - Hours in Photoshop/Figma
- 📊 **Data Analysts** - Extended spreadsheet work
- 📝 **Writers & Content Creators** - Marathon writing sessions
- 🎓 **Students** - Study marathons
- 🏠 **Remote Workers** - No office structure

### You Need BreakGuard If You:
- ✅ Work 8-15+ hours continuously
- ✅ Ignore break reminders regularly
- ✅ Suffer from eye strain or back pain
- ✅ Skip meals or bathroom breaks
- ✅ Feel guilty taking breaks
- ✅ Have poor self-discipline for health habits

## 🔒 Security & Authentication

### Two-Factor Unlock System

**Step 1: Google Authenticator (TOTP)**
- Industry-standard Time-based One-Time Password
- Works 100% offline (no internet needed)
- 6-digit code changes every 30 seconds
- Same tech banks use for 2FA

**Step 2: Face Verification**
- Uses your webcam
- Offline face matching (OpenCV)
- Data never leaves your computer
- Optional but recommended

### Anti-Bypass Features

- 🚫 **Keyboard blocking** - Alt+Tab, Alt+F4, Win+D disabled
- 🚫 **Task Manager auto-close** - Can't kill the process easily
- 🚫 **Fullscreen always-on-top** - Covers all windows
- 🚫 **Monitor control** - Physical screen turns off via IoT
- ⚡ **Survives restart** - Lock persists after reboot

> **Note:** BreakGuard is designed for self-discipline, not military-grade security. Advanced users can bypass via Safe Mode or external boot — this is intentional. The goal is habit formation, not imprisonment.

## 🎮 Monitor Control (Tinxy IoT)

BreakGuard integrates with **Tinxy** smart switches to physically control your monitor power.

### What is Tinxy?
- IoT smart switch platform (https://tinxyapi.pages.dev/)
- Controls devices via REST API
- Plug your monitor into Tinxy switch
- BreakGuard turns it OFF during breaks
- Monitor stays off until unlock complete

### Setup Tinxy (Optional)
1. Get Tinxy smart switch from https://tinxy.in/
2. Install Tinxy mobile app
3. Add your monitor switch to app
4. Get API token from app settings
5. Enter in BreakGuard setup wizard

> **Tinxy is optional** - BreakGuard works fine without it using software monitor control

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|----------|
| Language | Python 3.10+ | Core application |
| UI Framework | PyQt6 | Modern graphical interface |
| Authentication | pyotp | Google Authenticator (TOTP) |
| Face Recognition | OpenCV + face_recognition | Face verification |
| IoT Control | Tinxy REST API | Monitor power control |
| Startup | Windows Registry | Auto-start on boot |
| Screen Lock | PyQt6 Fullscreen | Unbreakable lock screen |
| Config | JSON | User settings storage |

### Project Structure
```
BreakGuard/
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── config.json                # User configuration
├── install.bat                # Windows installer
├── run_breakguard.bat         # Quick launcher
├── src/
│   ├── setup_wizard_gui_pyqt.py    # Setup wizard (PyQt6)
│   ├── lock_screen_pyqt.py         # Lock screen (PyQt6)
│   ├── settings_gui_pyqt.py        # Settings panel (PyQt6)
│   ├── totp_auth.py                # Google Authenticator logic
│   ├── face_verification.py        # Face recognition
│   ├── tinxy_api.py                # Tinxy IoT integration
│   ├── work_timer.py               # Break timer logic
│   ├── windows_startup.py          # Auto-start registry
│   └── config_manager.py           # Config file handler
└── data/
    ├── face_encodings.json        # Stored face data
    └── totp_secret.enc            # Encrypted TOTP secret
```

## 💾 Installation

### For Non-Technical Users (Easy Way)

1. **Install Python 3.10 or higher**
   - Download from [python.org](https://www.python.org/downloads/)
   - ⚠️ **IMPORTANT:** Check "Add Python to PATH" during installation

2. **Download BreakGuard**
   - Clone or download ZIP from GitHub
   - Extract to `C:\BreakGuard` or anywhere you like

3. **Install Dependencies**
   - Double-click `install.bat`
   - Wait for installation to complete
   - Close the window when done

4. **Run Setup Wizard**
   ```bash
   python main.py --setup
   ```
   - Follow the graphical wizard
   - Set work interval (e.g., 60 minutes)
   - Scan QR code with Google Authenticator app
   - Register face (recommended)
   - Configure Tinxy (optional)

5. **Start BreakGuard**
   - Double-click `run_breakguard.bat`
   - OR run: `python main.py`
   - System tray icon appears
   - Timer starts automatically

### For Developers (Command Line)

```bash
# Clone repository
git clone https://github.com/ProgrammerNomad/BreakGuard.git
cd BreakGuard

# Create virtual environment (optional)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run setup wizard
python main.py --setup

# Start application
python main.py
```

### Dependencies
The following packages will be installed:
- `PyQt6` - Modern GUI framework
- `pyotp` - Google Authenticator
- `qrcode` - QR code generation
- `opencv-python` - Face recognition
- `face-recognition` - Face matching
- `pillow` - Image processing
- `requests` - Tinxy API calls
- `cryptography` - Secure storage

## ⚙️ Configuration

All settings are stored in `config.json`:

```json
{
  "work_interval_minutes": 60,
  "warning_before_minutes": 5,
  "break_duration_minutes": 10,
  "totp_enabled": true,
  "face_verification_enabled": true,
  "tinxy_enabled": false,
  "tinxy_api_key": "",
  "tinxy_device_id": "",
  "tinxy_device_number": 1,
  "auto_start_windows": true,
  "max_snooze_count": 1
}
```

### Settings Explained

| Setting | Default | Description |
|---------|---------|-------------|
| `work_interval_minutes` | 60 | Work time before break (1-240 min) |
| `warning_before_minutes` | 5 | Warning notification before lock |
| `break_duration_minutes` | 10 | Minimum break time |
| `totp_enabled` | true | Require Google Authenticator |
| `face_verification_enabled` | true | Require face verification |
| `tinxy_enabled` | false | Use Tinxy monitor control |
| `auto_start_windows` | true | Auto-start with Windows |
| `max_snooze_count` | 1 | Number of snoozes allowed |

### Tinxy API Setup (Optional)

1. Buy Tinxy smart switch: https://tinxy.in/
2. Install Tinxy mobile app
3. Add device to app
4. Go to Settings → API Token
5. Copy your API token
6. Note your device ID from devices list
7. Enter in BreakGuard setup wizard

**Tinxy API Documentation:** https://tinxyapi.pages.dev/

## 🎮 Usage Guide

### Daily Workflow

1. **Start BreakGuard**
   - Run `run_breakguard.bat` or `python main.py`
   - System tray icon appears (🛡️)
   - Timer starts counting down

2. **During Work**
   - Hover over tray icon to see time remaining
   - Right-click icon for menu:
     - 📊 View Status
     - ⚙️ Settings
     - ⏸️ Pause (temporary)
     - 🚪 Exit

3. **Warning Notification**
   - 5 minutes before break: Warning popup
   - "Break in 5 minutes - save your work!"
   - Option to snooze once (if enabled)

4. **Break Time - Lock Screen Appears**
   - 🔒 Fullscreen lock takes over
   - 🖥️ Monitor turns off (if Tinxy enabled)
   - ⏳ Timer shows break countdown
   - ⛔ Can't Alt+Tab, can't close

5. **Unlock Process**
   - **Step 1:** Enter 6-digit code from Google Authenticator app
   - **Step 2:** Face verification via webcam
   - ✅ If both pass: Unlock granted
   - ❌ If either fails: Stays locked, try again

6. **After Unlock**
   - Work timer resets and restarts
   - Back to normal desktop
   - Cycle repeats

### System Tray Menu

```
🛡️ BreakGuard
  ├─ 🟢 Status: Active (42 mins remaining)
  ├─ ⏸️ Pause Timer
  ├─ ⚙️ Settings
  ├─ 🔄 Run Setup Again
  ├─ 📄 View Logs
  └─ 🚪 Exit BreakGuard
```

### Google Authenticator Setup

1. **First Time (Setup Wizard)**
   - BreakGuard shows QR code on screen
   - Open Google Authenticator app on phone
   - Tap "+" button
   - Select "Scan QR code"
   - Point camera at BreakGuard QR code
   - Account "BreakGuard" added to app

2. **During Lock Screen**
   - Open Google Authenticator app
   - Find "BreakGuard" entry
   - See 6-digit code (changes every 30 seconds)
   - Enter code in lock screen

**Tip:** Write down the secret key shown during setup in case you lose your phone!

### Face Registration

1. **During Setup Wizard**
   - Click "Register Face"
   - Camera preview appears
   - Position face in frame
   - Look straight at camera
   - Click "Capture" (5-10 photos recommended)
   - System saves your face encoding

2. **During Lock Screen**
   - After entering TOTP code
   - Camera activates automatically
   - Look at camera for 2-3 seconds
   - System matches face
   - Unlock granted if match successful

**Privacy:** Face data is stored locally in encrypted format, never uploaded anywhere.

## 🔧 Troubleshooting

### Installation Issues

**Problem:** `pip install` fails
- **Solution:** Make sure Python is added to PATH
- **Solution:** Run as Administrator
- **Solution:** Try: `python -m pip install -r requirements.txt`

**Problem:** "Python not recognized"
- **Solution:** Reinstall Python, check "Add to PATH"
- **Solution:** Restart terminal/computer after install

### Setup Wizard Issues

**Problem:** QR code not showing
- **Solution:** Install pillow: `pip install pillow`
- **Solution:** Check console for errors
- **Solution:** Manually enter secret key in Google Authenticator

**Problem:** Camera not working
- **Solution:** Grant camera permissions in Windows Settings
- **Solution:** Close other apps using camera (Zoom, Teams, etc.)
- **Solution:** Try different USB camera
- **Solution:** Skip face verification (TOTP still works)

**Problem:** 6 OTP input boxes not showing
- **Solution:** This is a known PyQt6 styling issue
- **Solution:** Clear Python cache: Delete `src/__pycache__` folder
- **Solution:** Restart application
- **Solution:** See PYQT6_IMPLEMENTATION.md for details

### Lock Screen Issues

**Problem:** Can't unlock even with correct code
- **Solution:** Check code hasn't expired (30 sec window)
- **Solution:** Sync phone time with internet
- **Solution:** Try next code that appears
- **Solution:** Check caps lock is off

**Problem:** Face verification keeps failing
- **Solution:** Ensure good lighting
- **Solution:** Remove glasses/hat if not worn during registration
- **Solution:** Re-register face in better lighting
- **Solution:** Disable face verification temporarily in config.json

**Problem:** Lock screen won't appear
- **Solution:** Check BreakGuard is running (system tray icon)
- **Solution:** Check work interval in config.json
- **Solution:** View logs for errors
- **Solution:** Restart BreakGuard

### Tinxy Issues

**Problem:** Monitor not turning off
- **Solution:** Verify Tinxy API token is correct
- **Solution:** Check device ID in config.json
- **Solution:** Test Tinxy in their app first
- **Solution:** Check internet connection
- **Solution:** BreakGuard works without Tinxy (software-only lock)

### Auto-Start Issues

**Problem:** BreakGuard doesn't start with Windows
- **Solution:** Run setup wizard again
- **Solution:** Manually add to Task Scheduler
- **Solution:** Check `auto_start_windows` in config.json
- **Solution:** Run app as Administrator once

### Emergency Bypass

If you're truly stuck and need to bypass:

1. **Restart in Safe Mode** (F8 during boot)
2. **Boot from USB** with another OS
3. **Edit config.json** from another account
4. **Delete BreakGuard folder** (defeats the purpose!)

> **Remember:** The goal is building discipline. If you bypass too often, BreakGuard won't help you.

## 📊 Project Roadmap

### ✅ Completed (v1.0)
- [x] PyQt6 modern UI
- [x] Google Authenticator (TOTP)
- [x] Face verification
- [x] Tinxy IoT integration
- [x] Windows auto-start
- [x] Setup wizard
- [x] Lock screen with keyboard blocking
- [x] System tray integration

### 🚧 In Progress (v1.1)
- [ ] Fix 6-box OTP input styling issues
- [ ] Improve face recognition accuracy
- [ ] Better error logging
- [ ] Settings panel improvements

### 🔮 Future Features (v2.0)
- [ ] Break activity suggestions (stretches, eye exercises)
- [ ] Break statistics dashboard
- [ ] Multiple user profiles
- [ ] Smartwatch integration
- [ ] Mobile companion app
- [ ] Cloud sync (optional)
- [ ] Guided meditation during breaks
- [ ] Posture detection via camera
- [ ] Custom break notifications
- [ ] Integration with fitness trackers

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Bug Reports
1. Check existing issues first
2. Provide detailed reproduction steps
3. Include screenshots if UI-related
4. Share your config.json (remove sensitive data)
5. Include Python version and OS version

### Feature Requests
1. Open an issue with "[Feature Request]" in title
2. Explain the use case
3. Describe expected behavior
4. Suggest implementation approach (optional)

### Code Contributions
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Follow existing code style
4. Test thoroughly
5. Update documentation
6. Submit pull request

### Documentation
- Improve README
- Add tutorials
- Create video guides
- Translate to other languages

### Areas Needing Help
- 🎨 UI/UX improvements
- 🔒 Security enhancements
- 📱 Mobile app development
- 🧪 Testing on different Windows versions
- 🌐 Internationalization (i18n)
- 📝 Better documentation

**Repository:** [github.com/ProgrammerNomad/BreakGuard](https://github.com/ProgrammerNomad/BreakGuard)

---

## 📄 License

**MIT License** - Free to use, modify, and distribute.

Copyright (c) 2025 BreakGuard

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.

See [LICENSE](LICENSE) file for full details.

---

## 💡 Philosophy

> "If willpower was enough, reminders would work.  
> BreakGuard exists because discipline needs structure.  
> Health isn't negotiable - enforce it."

BreakGuard is not about punishment. It's about **protecting yourself from yourself**. It's about building sustainable work habits that prevent burnout, preserve your eyesight, and keep your body healthy for the long term.

We work in an industry where 12-hour days are normalized. Where skipping meals is a badge of honor. Where back pain and eye strain are accepted as inevitable.

**BreakGuard says: Not anymore.**

---

## ⭐ Support the Project

If BreakGuard helps you stay healthy:

- ⭐ **Star this repository** on GitHub
- 👥 **Share with colleagues** who need it
- 🐛 **Report bugs** you encounter
- 💡 **Suggest features** you'd like
- 📝 **Write about it** on your blog
- 💵 **Sponsor development** (link coming soon)

Every star motivates us to keep improving! 🚀

---

## 📧 Contact

- **Issues:** [GitHub Issues](https://github.com/ProgrammerNomad/BreakGuard/issues)
- **Discussions:** [GitHub Discussions](https://github.com/ProgrammerNomad/BreakGuard/discussions)
- **Email:** programmernomad@example.com (update with real email)

---

## 🚀 Quick Links

- [Installation Guide](SETUP.md)
- [Quick Start](QUICKSTART.md)
- [Architecture](ARCHITECTURE.md)
- [PyQt6 Implementation](PYQT6_IMPLEMENTATION.md)
- [Screens & Wireframes](SCREENS_WIREFRAMES.md)

---

**Built with ❤️ for developers who care about their health**

**Stay healthy. Stay productive. Use BreakGuard. 🛡️**
