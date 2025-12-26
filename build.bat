@echo off
REM ========================================
REM BreakGuard Build Script
REM Builds standalone executable and installer
REM ========================================

echo ========================================
echo BreakGuard Build System
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo [1/4] Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
echo Done.

echo.
echo [2/4] Building executable with PyInstaller...
echo This may take a few minutes...
pyinstaller breakguard.spec --clean --noconfirm

if %errorlevel% neq 0 (
    echo.
    echo ERROR: PyInstaller build failed
    pause
    exit /b 1
)

echo Done.

echo.
echo [3/4] Checking for Inno Setup...
set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if not exist "%INNO_PATH%" (
    echo.
    echo WARNING: Inno Setup not found at default location
    echo.
    echo To create the installer, please:
    echo 1. Download Inno Setup from: https://jrsoftware.org/isdl.php
    echo 2. Install it to default location
    echo 3. Run this script again
    echo.
    echo For now, you can find the executable at: dist\BreakGuard\BreakGuard.exe
    pause
    exit /b 0
)

echo.
echo [4/4] Creating Windows installer with Inno Setup...
"%INNO_PATH%" installer.iss

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Inno Setup build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Executable: dist\BreakGuard\BreakGuard.exe
echo Installer:  dist\installer\BreakGuard_Setup_v1.0.0.exe
echo.
echo You can now distribute the installer to users!
echo.
pause
