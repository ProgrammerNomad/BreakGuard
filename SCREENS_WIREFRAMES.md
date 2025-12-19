# BreakGuard - All Screens Wireframes & Design Specifications

## Overview
BreakGuard has **8 main screens** that need modern PyQt6 design. Below are detailed wireframes for each.

---

## 1. SETUP WIZARD (6 Steps)

### 1.1 Welcome Screen
**Purpose**: Introduce the app and its features

```
┌─────────────────────────────────────────────────────────┐
│ Progress: ███░░░░░░░░░░░░░ (1/6)                       │
│                                                         │
│                    🛡️                                   │
│              Welcome to BreakGuard                      │
│        Your personal break reminder assistant           │
│                                                         │
│   Features:                                            │
│   ⏰ Smart work interval tracking                      │
│   🔒 Secure authentication                             │
│   👤 Optional face verification                        │
│   🔌 IoT device integration                            │
│   🚀 Auto-start with Windows                           │
│                                                         │
│   This wizard will guide you through setup.            │
│   You can change settings later from system tray.      │
│                                                         │
│                        [Next →]                        │
└─────────────────────────────────────────────────────────┘
```

**Design Notes**:
- Large icon/logo at top
- Clean typography with hierarchy
- Feature list with icons
- Single CTA button (Next)
- Soft background color (#f8f9fa)

---

### 1.2 Work Intervals Configuration
**Purpose**: Set work/break intervals

```
┌─────────────────────────────────────────────────────────┐
│ Progress: ██████░░░░░░░░░ (2/6)                        │
│                                                         │
│   ⏱️ Configure Work Intervals                          │
│   Set how often you want to take breaks                │
│                                                         │
│   Work interval (minutes):  [60 ▼]  minutes           │
│                                                         │
│   Warning before lock:      [5  ▼]  minutes           │
│                                                         │
│   💡 Recommended Settings                              │
│   • 60 minutes: Standard (20-20-20 rule)              │
│   • 90 minutes: Extended focus                         │
│   • 30 minutes: Frequent breaks                        │
│                                                         │
│                                                         │
│   [← Back]                             [Next →]       │
└─────────────────────────────────────────────────────────┘
```

**Design Notes**:
- Dropdown spinners with +/- buttons
- Info card with recommendations
- Clear labels
- Both back and next buttons

---

### 1.3 Google Authenticator Setup
**Purpose**: Setup 2FA with QR code

```
┌──────────────────────────────────────────────────────────────────┐
│ Progress: █████████░░░░░ (3/6)                                  │
│                                                                  │
│   🔐 Setup Google Authenticator                                 │
│   Secure your breaks with two-factor authentication             │
│                                                                  │
│   ☑ Enable Google Authenticator                                │
│                                                                  │
│          [Generate QR Code]                                     │
│                                                                  │
│   ┌───────────────────┐  ┌──────────────────────────────────┐ │
│   │                   │  │ ✓ QR Code Generated!             │ │
│   │                   │  │                                  │ │
│   │     QR CODE       │  │ Scan with Google Authenticator: │ │
│   │   [330x330px]     │  │ 1. Open app on phone            │ │
│   │                   │  │ 2. Tap '+' button                │ │
│   │                   │  │ 3. Scan QR code                  │ │
│   │                   │  │ 4. Enter code below              │ │
│   └───────────────────┘  │                                  │ │
│                          │ Secret: ABC123DEF456             │ │
│                          │                                  │ │
│                          │ ┌──────────────────────────────┐ │ │
│                          │ │  🔓 Verify Your Setup        │ │ │
│                          │ │  Enter 6-digit code:         │ │ │
│                          │ │                              │ │ │
│                          │ │  [_] [_] [_] [_] [_] [_]    │ │ │
│                          │ │  (6 separate boxes)          │ │ │
│                          │ │                              │ │ │
│                          │ │  [Verify Code]               │ │ │
│                          │ │                              │ │ │
│                          │ │  ℹ️ Status message here      │ │ │
│                          │ │  💡 Code changes every 30s   │ │ │
│                          │ └──────────────────────────────┘ │ │
│                          └──────────────────────────────────┘ │
│                                                                  │
│   [← Back]                                      [Next →]       │
└──────────────────────────────────────────────────────────────────┘
```

**Design Notes**:
- Side-by-side layout (QR left, instructions right)
- Card-based verification section with white background
- **6 separate input boxes for OTP code (modern style)**
- Auto-focus next box on digit entry
- Auto-submit on 6th digit (optional)
- Clear status messages (green for success, red for error)
- QR in bordered frame
- Each input box: 50x50px, centered digit, large font (20-24px)
- Boxes with 8px spacing between them

---

### 1.4 Face Verification Setup
**Purpose**: Setup face recognition

```
┌─────────────────────────────────────────────────────────┐
│ Progress: ████████████░░ (4/6)                          │
│                                                         │
│   👤 Face Verification Setup                           │
│   Add an extra layer of security                       │
│                                                         │
│   ☑ Enable Face Verification                          │
│                                                         │
│   ┌───────────────────────────────────────────────┐   │
│   │                                               │   │
│   │           CAMERA PREVIEW                      │   │
│   │           [640x480px]                         │   │
│   │                                               │   │
│   │                                               │   │
│   └───────────────────────────────────────────────┘   │
│                                                         │
│   Status: Ready to capture                             │
│   Photos taken: 0/10                                   │
│                                                         │
│   Instructions:                                        │
│   • Look directly at camera                            │
│   • Keep face centered                                 │
│   • Photos will be taken automatically                 │
│                                                         │
│                [Start Capture]                         │
│                                                         │
│   [← Back]                             [Next →]       │
└─────────────────────────────────────────────────────────┘
```

**Design Notes**:
- Large camera preview with border
- Progress indicator (X/10 photos)
- Clear instructions
- Auto-capture with countdown
- Skip option available

---

### 1.5 Tinxy IoT Integration
**Purpose**: Setup smart device control

```
┌─────────────────────────────────────────────────────────┐
│ Progress: ███████████████░ (5/6)                        │
│                                                         │
│   🔌 Tinxy Device Integration                          │
│   Control IoT devices during breaks (Optional)         │
│                                                         │
│   ☐ Enable Tinxy Integration                          │
│                                                         │
│   ┌───────────────────────────────────────────────┐   │
│   │  API Configuration                            │   │
│   │                                               │   │
│   │  API Key:                                     │   │
│   │  [_________________________________]          │   │
│   │                                               │   │
│   │  Device ID:                                   │   │
│   │  [_________________________________]          │   │
│   │                                               │   │
│   │  Device Number: [1 ▼]                        │   │
│   │                                               │   │
│   │              [Test Connection]                │   │
│   │                                               │   │
│   │  Status: Not connected                        │   │
│   └───────────────────────────────────────────────┘   │
│                                                         │
│   ℹ️ What is Tinxy?                                    │
│   Control smart switches/devices during breaks.        │
│   Can turn off monitor automatically.                  │
│                                                         │
│   [← Back]                             [Next →]       │
└─────────────────────────────────────────────────────────┘
```

**Design Notes**:
- Card for API inputs
- Test connection button with status
- Info section explaining feature
- Optional (can skip)

---

### 1.6 Setup Complete
**Purpose**: Confirmation and launch

```
┌─────────────────────────────────────────────────────────┐
│ Progress: ██████████████████ (6/6)                      │
│                                                         │
│                                                         │
│                    ✅                                   │
│              Setup Complete!                            │
│                                                         │
│   BreakGuard is ready to protect your health           │
│   and productivity!                                     │
│                                                         │
│   Configuration Summary:                               │
│   ⏰ Work interval: 60 minutes                         │
│   ⚠️ Warning time: 5 minutes                           │
│   🔐 Auth: Google Authenticator                        │
│   👤 Face verification: Enabled                        │
│   🔌 Tinxy: Disabled                                   │
│                                                         │
│   The app will start in the system tray.              │
│   Right-click the icon to access settings.             │
│                                                         │
│                    [Finish]                            │
└─────────────────────────────────────────────────────────┘
```

**Design Notes**:
- Large success icon/animation
- Summary of settings
- Clear next steps
- Single finish button

---

## 2. LOCK SCREEN (Fullscreen)

**Purpose**: Lock computer during break time

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                                                                 │
│                        ⏸ BREAK TIME                            │
│                                                                 │
│              Time to take a break and rest your eyes            │
│                                                                 │
│                         12:34 PM                                │
│                                                                 │
│   ─────────────────────────────────────────────────────────   │
│                                                                 │
│              🔐 Unlock to Resume Work                          │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐ │
│   │  Enter Google Authenticator Code:                       │ │
│   │                                                          │ │
│   │       [_] [_] [_]  [_] [_] [_]                          │ │
│   │       (6 large separate boxes)                           │ │
│   │                                                          │ │
│   │              [Unlock]                                    │ │
│   │                                                          │ │
│   │  Attempts remaining: 5/5                                │ │
│   └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│                OR                                               │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐ │
│   │         👤 Face Verification                            │ │
│   │                                                          │ │
│   │    [Enable Camera] or [Scan Face]                       │ │
│   │                                                          │ │
│   │    Status: Ready                                         │ │
│   └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│                                                                 │
│              Break duration: 5:00 remaining                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Design Notes**:
- Fullscreen, always on top
- Dark background (#1a1a1a)
- Large text, centered
- Two unlock methods (TOTP and Face)
- Show remaining time
- Prevent close/minimize
- Show current time

---

## 3. WARNING DIALOG

**Purpose**: 5-minute warning before lock

```
┌──────────────────────────────────────────┐
│  ⚠️ Break Time Approaching               │
│                                          │
│  Your screen will lock in 5 minutes.    │
│                                          │
│  Time worked: 60 minutes                │
│  Next break at: 2:30 PM                 │
│                                          │
│  Save your work now!                    │
│                                          │
│  [Snooze 5 min]        [OK]             │
└──────────────────────────────────────────┘
```

**Design Notes**:
- System notification style
- Warning color (orange/yellow)
- Clear message
- Snooze option
- Small, non-intrusive

---

## 4. SETTINGS WINDOW (Tabbed)

**Purpose**: Configure all app settings

```
┌────────────────────────────────────────────────────────────┐
│  ⚙️ Settings                                      [X]       │
├────────────────────────────────────────────────────────────┤
│  [General] [Security] [IoT Devices] [About]               │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  GENERAL TAB                                               │
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Work Interval                                       │ │
│  │  How long to work before break                       │ │
│  │  [60] minutes                                        │ │
│  │                                                      │ │
│  │  Warning Time                                        │ │
│  │  Alert before lock                                   │ │
│  │  [5] minutes                                         │ │
│  │                                                      │ │
│  │  ☑ Enable break notifications                       │ │
│  │  ☑ Play sound on lock                               │ │
│  │  ☑ Auto-start with Windows                          │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│                            [Cancel]  [Save Settings]       │
└────────────────────────────────────────────────────────────┘
```

**Tabs**:
- **General**: Work intervals, notifications, auto-start
- **Security**: TOTP settings, face verification, change codes
- **IoT Devices**: Tinxy configuration, monitor control
- **About**: Version, credits, help

**Design Notes**:
- Tabbed interface
- Card-based sections
- Clear labels and help text
- Save/Cancel buttons
- Modal window (600x700px)

---

## 5. SYSTEM TRAY MENU

**Purpose**: Quick access to common actions

```
┌─────────────────────────────┐
│  🛡️ BreakGuard              │
├─────────────────────────────┤
│  Status: Active             │
│  Next break: 2:30 PM        │
│  Time left: 45 minutes      │
├─────────────────────────────┤
│  ⏸ Pause Monitoring         │
│  ⏭ Skip Current Interval    │
│  ⚙️ Settings                 │
│  📊 Statistics               │
├─────────────────────────────┤
│  🚪 Exit                     │
└─────────────────────────────┘
```

**Design Notes**:
- Show current status
- Quick actions
- Clean separators
- Icon for each item

---

## 6. STATISTICS WINDOW (Optional)

**Purpose**: Show usage statistics

```
┌────────────────────────────────────────────────────────┐
│  📊 Usage Statistics                          [X]      │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Today's Summary                                       │
│  ┌────────────────────────────────────────────────┐   │
│  │  Work sessions: 6                             │   │
│  │  Breaks taken: 5                              │   │
│  │  Total work time: 5h 45m                      │   │
│  │  Total break time: 30m                        │   │
│  └────────────────────────────────────────────────┘   │
│                                                        │
│  Weekly Overview                                       │
│  ┌────────────────────────────────────────────────┐   │
│  │   Chart/Graph of daily work hours             │   │
│  │   [Bar chart or line graph]                   │   │
│  └────────────────────────────────────────────────┘   │
│                                                        │
│  Health Score: 85/100 ⭐                               │
│  • Good break compliance                              │
│  • Regular intervals maintained                       │
│                                                        │
│                                      [Close]           │
└────────────────────────────────────────────────────────┘
```

**Design Notes**:
- Cards for metrics
- Charts/graphs
- Health score gamification
- Clean data presentation

---

## 7. FIRST RUN POPUP

**Purpose**: Detect first run and offer setup

```
┌──────────────────────────────────────────┐
│  🛡️ Welcome to BreakGuard!               │
│                                          │
│  It looks like this is your first time. │
│                                          │
│  Would you like to run the setup wizard?│
│                                          │
│  [Skip]              [Run Setup]        │
└──────────────────────────────────────────┘
```

---

## 8. ERROR/INFO DIALOGS

**Purpose**: Show messages to user

```
┌──────────────────────────────────────────┐
│  ⚠️ Warning                               │
│                                          │
│  [Error message here]                   │
│                                          │
│                           [OK]           │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│  ✓ Success                                │
│                                          │
│  [Success message here]                 │
│                                          │
│                           [OK]           │
└──────────────────────────────────────────┘
```

---

## Design System Recommendations

### Colors
```
Primary:    #0984e3 (blue)
Success:    #00b894 (green)
Warning:    #fdcb6e (yellow)
Error:      #d63031 (red)
Background: #f5f6fa (light gray)
Surface:    #ffffff (white)
Text Dark:  #2f3542
Text Light: #636e72
Border:     #dfe6e9
```

### Typography
```
Titles:     24-28px, Bold
Headings:   18-22px, Bold
Body:       11-14px, Regular
Captions:   9-10px, Regular
Input:      14-16px, Regular
```

### Spacing
```
Extra Small: 4px
Small:       8px
Medium:      16px
Large:       24px
Extra Large: 32px
```

### Border Radius
```
Small:  4px
Medium: 6px
Large:  8px
Cards:  12px
```

### Shadows
```
Light:  0 2px 4px rgba(0,0,0,0.1)
Medium: 0 4px 8px rgba(0,0,0,0.15)
Heavy:  0 8px 16px rgba(0,0,0,0.2)
```

---

## Priority Order for Implementation

1. **Setup Wizard** - First user experience (HIGH)
2. **Lock Screen** - Core functionality (HIGH)
3. **Settings Window** - Configuration (MEDIUM)
4. **System Tray** - Quick access (MEDIUM)
5. **Warning Dialog** - User notification (MEDIUM)
6. **Statistics** - Nice to have (LOW)

---

## Notes for Figma Design

1. Create **components** for reusable elements (buttons, cards, inputs)
2. Use **auto-layout** for responsive design
3. Create **variants** for button states (normal, hover, pressed, disabled)
4. Design for **900x650px** base window size
5. Consider **dark mode** variant
6. Export assets at **@2x** for high DPI screens
7. Use **consistent spacing** (8px grid system)
8. Design **hover states** for interactive elements
9. Consider **animations** for transitions
10. Test on **Windows 11** styling guidelines

---

## Export Requirements

When exporting from Figma:
- **Icons**: SVG format
- **Images**: PNG @2x
- **Colors**: HEX codes
- **Fonts**: System fonts (Segoe UI for Windows)
- **Spacing values**: In pixels
- **Border radius**: In pixels
- **Component specs**: As CSS/PyQt6 stylesheets

---

This document provides complete wireframes for all screens. Use this to create beautiful designs in Figma, then I'll implement them in PyQt6!
