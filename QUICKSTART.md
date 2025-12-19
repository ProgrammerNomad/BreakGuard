# BreakGuard - Quick Start Guide for Non-Technical Users

## 🎯 What is BreakGuard?

BreakGuard is an application that **forces you to take breaks** while working on your computer. Unlike other reminder apps that you can easily ignore, BreakGuard actually **locks your screen** until you take a proper break!

## 📥 Installation (Simple Steps)

### Step 1: Install Python (One-Time Setup)

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download Python (version 3.8 or newer)
3. **IMPORTANT**: During installation, check the box "Add Python to PATH"
4. Click "Install Now"

### Step 2: Download BreakGuard

1. Go to [github.com/ProgrammerNomad/BreakGuard](https://github.com/ProgrammerNomad/BreakGuard)
2. Click the green "Code" button
3. Click "Download ZIP"
4. Extract the ZIP file to a folder (e.g., `C:\BreakGuard`)

### Step 3: Install BreakGuard

1. Open the extracted folder
2. Hold **Shift** and **Right-Click** in the folder
3. Select "Open PowerShell window here" (or "Open Command window here")
4. Type this command and press Enter:
   ```
   pip install -r requirements.txt
   ```
5. Wait for installation to complete (may take 2-3 minutes)

### Step 4: Run BreakGuard for the First Time

1. In the same PowerShell/Command window, type:
   ```
   python main.py
   ```
2. A **Setup Wizard** will appear!

## 🧙‍♂️ Setup Wizard - Follow These Steps

### Screen 1: Welcome
- Read the welcome message
- Click "Next"

### Screen 2: Work Schedule
- **Work interval**: How long you want to work (default: 60 minutes)
  - 60 minutes = 1 hour of work, then break
  - 90 minutes = 1.5 hours of work, then break
- **Warning before lock**: Heads-up before screen locks (default: 5 minutes)
- Click "Next"

### Screen 3: Google Authenticator Setup

**Why?** This prevents you from cheating by using Task Manager to close the app!

1. Check "Enable Google Authenticator"
2. Click "Generate QR Code"
3. Install Google Authenticator on your phone:
   - **Android**: [Play Store Link](https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2)
   - **iPhone**: [App Store Link](https://apps.apple.com/app/google-authenticator/id388497605)
4. Open the app on your phone
5. Tap the **"+"** button
6. **Scan the QR code** shown on your computer screen
7. Done! The app will now show a 6-digit code
8. Click "Next"

**What's this code for?** When BreakGuard locks your screen, you'll need to enter this 6-digit code (from your phone) to unlock.

### Screen 4: Face Verification (Optional but Recommended)

**Why?** Extra security so only you can unlock the break screen!

1. Check "Enable Face Verification"
2. Click "Capture My Face"
3. Look at your camera
4. Press **SPACE** on your keyboard when your face is visible
5. Click "Next"

**Privacy Note**: Your face data **stays on your computer** and is **never uploaded** anywhere!

### Screen 5: Tinxy Smart Switch (Optional - Advanced)

**Do you have a Tinxy smart switch?**
- **NO**: Just click "Next" (we'll use software to control your monitor)
- **YES**: Enter your Tinxy details:
  1. Open Tinxy app on your phone
  2. Go to Settings → API Token
  3. Copy the token
  4. Paste it in the "API Key" field
  5. Enter your Device ID
  6. Click "Next"

### Screen 6: Complete!

- Review your settings
- Click "Finish"
- **Done!** BreakGuard is now running

## 🚀 Daily Use

### Starting BreakGuard

After setup, BreakGuard **auto-starts with Windows**. You can also start it manually:

1. Open the BreakGuard folder
2. Double-click `run_breakguard.bat` (we'll create this file)

OR

1. Open PowerShell in the BreakGuard folder
2. Type: `python main.py`

### Where is BreakGuard?

Look for the **BreakGuard icon** in your **System Tray** (bottom-right of your screen, near the clock).

### System Tray Controls

**Right-click the BreakGuard icon** to see:

- **Time Remaining**: Shows how long until your next break
- **Pause Timer**: Pause the timer temporarily
- **Resume Timer**: Resume counting
- **Reset Timer**: Start over
- **Settings**: Change your preferences
- **Exit**: Close BreakGuard

### What Happens at Break Time?

1. **5 minutes before** (or your warning time): You'll see a notification
2. **At break time**:
   - Your screen will **lock fullscreen**
   - Your monitor will **turn off** (if Tinxy is connected)
   - You **cannot close** the lock screen with Alt+F4 or Task Manager

3. **To unlock**:
   - Enter the **6-digit code** from Google Authenticator app
   - Click "Verify Face" and look at your camera
   - Once verified, you're unlocked!

4. **Timer resets** and counts down again

## ⚙️ Changing Settings

1. **Right-click** the BreakGuard icon in system tray
2. Click "**Settings**"
3. A window will open with tabs:
   - **General**: Change work interval, warning time
   - **Security**: Enable/disable TOTP, re-register face
   - **Tinxy API**: Configure or update Tinxy credentials
   - **About**: Version info and links

4. Make your changes
5. Click "**Save Settings**"

## 🆘 Troubleshooting

### "Python is not recognized"
- You didn't check "Add Python to PATH" during Python installation
- **Fix**: Reinstall Python and check that box

### Camera Not Working
- Close other apps using the camera (Zoom, Skype, etc.)
- Try restarting BreakGuard

### Can't Unlock - Wrong Code
- Make sure your phone's clock is accurate
- TOTP codes change every 30 seconds - use the current code
- Check that you scanned the correct QR code

### BreakGuard Not Starting with Windows
- Open Settings
- Go to "General" tab
- Check "Start with Windows"
- Save settings

### Monitor Not Turning Off
- If you don't have Tinxy, monitor control is software-based (may not work on all systems)
- The lock screen will still work!

### Emergency: Need to Disable BreakGuard
1. Press **Ctrl+Shift+Esc** before lock screen appears
2. Find "python.exe" in processes
3. Right-click → End Task
4. Or restart your computer in Safe Mode

**Note**: BreakGuard is designed for self-discipline, not as a prison. If you really need to bypass it, you can - but that defeats the purpose!

## 📱 Google Authenticator Lost/Broken Phone?

If you lose access to Google Authenticator:

1. Look for `data/totp_qr.png` in your BreakGuard folder
2. Scan this QR code with Google Authenticator on your new phone

OR

1. Run setup wizard again: `python main.py --setup`
2. Generate a new QR code

## 🎓 Tips for Success

1. **Start with 60-minute intervals** - don't make it too long at first
2. **Enable both TOTP and Face** - harder to cheat!
3. **Use the warning time** - save your work before lock
4. **Don't fight it** - the point is to form healthy habits
5. **Respect the break** - actually get up, move, look away from screen

## 📞 Need More Help?

- **Read detailed docs**: Check `SETUP.md` in the folder
- **Technical guide**: See `ARCHITECTURE.md`
- **Report issues**: [GitHub Issues](https://github.com/ProgrammerNomad/BreakGuard/issues)
- **Ask questions**: Open a discussion on GitHub

## 🎉 You're Ready!

BreakGuard is now protecting your health. Your future self will thank you! 💪

Remember: **"If willpower was enough, reminders would work. BreakGuard exists because discipline needs structure."**
