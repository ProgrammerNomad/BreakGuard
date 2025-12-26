"""
Test script to verify paths work in both developer and built modes
Run this with: python test_paths.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_path_utils():
    """Test all path_utils functions"""
    from path_utils import (
        get_app_data_dir,
        get_config_file,
        get_data_dir,
        get_logs_dir,
        get_assets_dir,
        get_app_dir,
        ensure_app_data_dirs
    )
    
    print("=" * 60)
    print("PATH UTILITIES TEST")
    print("=" * 60)
    print(f"Mode: {'FROZEN (Built)' if getattr(sys, 'frozen', False) else 'DEVELOPER (Source)'}")
    print()
    
    print("App Data Dir:", get_app_data_dir())
    print("Config File:", get_config_file())
    print("Data Dir:", get_data_dir())
    print("Logs Dir:", get_logs_dir())
    print("Assets Dir:", get_assets_dir())
    print("App Dir:", get_app_dir())
    print()
    
    # Test assets
    print("Testing Assets:")
    assets = get_assets_dir()
    logo_png = assets / 'logo.png'
    logo_ico = assets / 'logo.ico'
    print(f"  logo.png exists: {logo_png.exists()} ({logo_png})")
    print(f"  logo.ico exists: {logo_ico.exists()} ({logo_ico})")
    print()
    
    # Test theme
    print("Testing Theme:")
    theme_dir = Path(__file__).parent / 'src' / 'theme' if not getattr(sys, 'frozen', False) else Path(sys.executable).parent / '_internal' / 'src' / 'theme'
    styles_qss = theme_dir / 'styles.qss'
    print(f"  styles.qss exists: {styles_qss.exists()} ({styles_qss})")
    print()
    
    # Test OpenCV Haar Cascade
    print("Testing OpenCV Haar Cascade:")
    try:
        import cv2
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        cascade = cv2.CascadeClassifier(cascade_path)
        print(f"  Cascade loaded: {not cascade.empty()}")
        print(f"  Cascade path: {cascade_path}")
    except Exception as e:
        print(f"  ERROR: {e}")
    print()
    
    # Ensure directories
    print("Ensuring app data directories...")
    ensure_app_data_dirs()
    print("  ✓ Done")
    print()
    
    print("=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)

if __name__ == '__main__':
    test_paths()
