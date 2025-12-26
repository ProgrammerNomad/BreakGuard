# BreakGuard Build & Release Guide

This guide explains how to build and release BreakGuard with professional installers.

## Prerequisites

### Required Software

1. **Python 3.10+** - Already installed
2. **PyInstaller** - Automatically installed by build script
3. **Inno Setup 6** - Download from: https://jrsoftware.org/isdl.php
   - Install to default location: `C:\Program Files (x86)\Inno Setup 6\`

## Building the Installer

### Quick Build (Recommended)

Simply run the build script:

```batch
build.bat
```

This will:
1. Clean previous builds
2. Build executable with PyInstaller
3. Create Windows installer with Inno Setup
4. Output installer to `dist\installer\`

### Manual Build Steps

If you prefer manual control:

#### Step 1: Build Executable

```batch
pyinstaller breakguard.spec --clean --noconfirm
```

Output: `dist\BreakGuard\BreakGuard.exe`

#### Step 2: Create Installer

```batch
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

Output: `dist\installer\BreakGuard_Setup_v1.0.0.exe`

## Version Management

### Updating Version Number

Before building a new release, update version in these files:

1. **version.json** - Main version file
   ```json
   {
     "version": "1.1.0",
     "release_date": "2025-12-27",
     "changelog": [...]
   }
   ```

2. **version_info.txt** - Windows executable metadata
   ```
   filevers=(1, 1, 0, 0),
   prodvers=(1, 1, 0, 0),
   ```

3. **installer.iss** - Installer version
   ```pascal
   #define MyAppVersion "1.1.0"
   ```

### Auto-Update System

When you release a new version:

1. Update `version.json` with new version and changelog
2. Build and test the installer
3. Create GitHub release with installer
4. Push updated `version.json` to repository
5. Users will be notified in Settings > About tab

## Distribution

### GitHub Release Process

1. **Build the installer** using `build.bat`

2. **Test the installer** on a clean Windows machine

3. **Create GitHub Release:**
   - Go to: https://github.com/ProgrammerNomad/BreakGuard/releases
   - Click "Draft a new release"
   - Tag version: `v1.0.0`
   - Release title: `BreakGuard v1.0.0`
   - Upload: `dist\installer\BreakGuard_Setup_v1.0.0.exe`
   - Add release notes from changelog

4. **Update Repository:**
   - Commit and push updated `version.json`
   - Users will auto-detect the update

## Features

### Installer Features

✅ **Smart Upgrades** - Detects existing installation
✅ **Data Preservation** - Keeps settings during upgrade
✅ **Auto-Backup** - Backs up data before upgrade
✅ **Startup Option** - Add to Windows startup
✅ **Desktop Shortcut** - Optional desktop icon
✅ **Clean Uninstall** - Option to keep or delete data
✅ **No Python Required** - Standalone executable

### Update Checker Features

✅ **Auto-Detection** - Checks GitHub for updates
✅ **Version Comparison** - Shows changelog
✅ **One-Click Download** - Direct link to releases
✅ **Non-Intrusive** - Manual check in settings

## Testing Checklist

Before releasing, test:

- [ ] Clean install on fresh Windows
- [ ] Upgrade from previous version (settings preserved)
- [ ] Desktop shortcut creation
- [ ] Windows startup integration
- [ ] Update checker functionality
- [ ] Uninstall (with and without data preservation)
- [ ] All features work in installed version

## Troubleshooting

### Build Errors

**PyInstaller fails:**
- Ensure all dependencies in `requirements.txt` are installed
- Check `breakguard.spec` for missing data files
- Try: `pip install pyinstaller --upgrade`

**Inno Setup not found:**
- Install from: https://jrsoftware.org/isdl.php
- Verify path in `build.bat`

**Missing icon:**
- Create `assets\icon.ico` or comment out icon line in spec

### Testing Issues

**Installer doesn't preserve settings:**
- Check `installer.iss` backup/restore functions
- Verify AppId matches between versions

**Update checker fails:**
- Ensure `version.json` URL is correct
- Check network connectivity
- Verify JSON format on GitHub

## Advanced Configuration

### Custom Build Options

Edit `breakguard.spec` to:
- Add/remove included files
- Exclude unnecessary packages
- Enable/disable UPX compression
- Add custom hooks

### Installer Customization

Edit `installer.iss` to:
- Change install directory
- Add custom setup pages
- Modify uninstall behavior
- Add registry entries

## Dependencies

The installer packages these dependencies:

- PyQt6 - Modern UI framework
- OpenCV - Face recognition
- OpenCV (opencv-contrib-python) - Face detection via Haar Cascade
- pyotp - TOTP authentication
- qrcode - QR code generation
- requests - Update checking
- cryptography - Secure storage

- packaging - Version comparison

## Support

For build issues:
- Check logs in `build` directory
- Review PyInstaller warnings
- Test on clean Windows VM
- Open issue on GitHub

## License

MIT License - See LICENSE file
