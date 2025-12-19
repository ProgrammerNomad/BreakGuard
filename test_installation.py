"""
Test script to verify BreakGuard installation and dependencies
Run this before starting BreakGuard to check everything is OK
"""

import sys
import importlib
from pathlib import Path

def test_python_version():
    """Test Python version"""
    print("=" * 60)
    print("Testing Python Version...")
    print("=" * 60)
    
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ FAIL: Python 3.9+ required")
        return False
    else:
        print("✅ PASS: Python version OK")
        return True

def test_dependencies():
    """Test required dependencies"""
    print("\n" + "=" * 60)
    print("Testing Dependencies...")
    print("=" * 60)
    
    dependencies = {
        'PyQt6': 'PyQt6',
        'pyotp': 'pyotp',
        'qrcode': 'qrcode',
        'cv2': 'opencv-contrib-python',
        'numpy': 'numpy',
        'PIL': 'Pillow',
        'requests': 'requests',
        'cryptography': 'cryptography',
    }
    
    all_ok = True
    
    for module_name, package_name in dependencies.items():
        try:
            importlib.import_module(module_name)
            print(f"✅ {package_name:30} - OK")
        except ImportError:
            print(f"❌ {package_name:30} - MISSING")
            all_ok = False
    
    # Windows-specific
    if sys.platform == 'win32':
        try:
            import win32api
            print(f"✅ {'pywin32':30} - OK")
        except ImportError:
            print(f"❌ {'pywin32':30} - MISSING")
            all_ok = False
    
    return all_ok

def test_project_structure():
    """Test project file structure"""
    print("\n" + "=" * 60)
    print("Testing Project Structure...")
    print("=" * 60)
    
    base_dir = Path(__file__).parent
    
    required_files = [
        'main.py',
        'requirements.txt',
        'install.bat',
        'run_breakguard.bat',
        'src/config_manager.py',
        'src/totp_auth.py',
        'src/face_verification.py',
        'src/tinxy_api.py',
        'src/windows_startup.py',
        'src/work_timer.py',
        'src/lock_screen_pyqt.py',
        'src/setup_wizard_gui_pyqt.py',
        'src/settings_gui_pyqt.py',
    ]
    
    all_ok = True
    
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path:40} - EXISTS")
        else:
            print(f"❌ {file_path:40} - MISSING")
            all_ok = False
    
    return all_ok

def test_modules_import():
    """Test importing project modules"""
    print("\n" + "=" * 60)
    print("Testing Module Imports...")
    print("=" * 60)
    
    # Add src to path
    base_dir = Path(__file__).parent
    src_path = base_dir / 'src'
    sys.path.insert(0, str(src_path))
    
    modules = [
        'config_manager',
        'totp_auth',
        'face_verification',
        'tinxy_api',
        'windows_startup',
    ]
    
    all_ok = True
    
    for module_name in modules:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name:30} - OK")
        except Exception as e:
            print(f"❌ {module_name:30} - ERROR: {e}")
            all_ok = False
    
    return all_ok

def main():
    """Run all tests"""
    print("\n")
    print("🛡️  BreakGuard Installation Test")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Python Version", test_python_version()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("Project Structure", test_project_structure()))
    results.append(("Module Imports", test_modules_import()))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED!")
        print("\nYou can now run:")
        print("  python main.py --setup")
        print("\nOr double-click:")
        print("  run_breakguard.bat")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("\nPlease install missing dependencies:")
        print("  pip install -r requirements.txt")
        print("\nOr run:")
        print("  install.bat")
    
    print("\n")

if __name__ == '__main__':
    main()
