# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for BreakGuard
Builds standalone Windows executable with all dependencies
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
from pathlib import Path

# Project root
project_root = Path('.').resolve()
src_dir = project_root / 'src'

# Collect OpenCV Haar Cascade data files
import cv2
import os
cv2_data_path = os.path.join(os.path.dirname(cv2.__file__), 'data')

# Collect all data files
datas = [
    ('assets', 'assets'),
    ('data', 'data'),
    ('src/theme', 'src/theme'),
    ('src/*.py', 'src'),  # Include all Python files from src
    ('version.json', '.'),
    ('config.json', '.'),
    ('README.md', '.'),
    ('LICENSE', '.'),
    (cv2_data_path, 'cv2/data'),  # Include OpenCV Haar Cascades
]

# Hidden imports for PyQt6 and other dependencies
hiddenimports = [
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'cv2',
    'numpy',
    'pyotp',
    'qrcode',
    'requests',
    'cryptography',
    'packaging',
    'path_utils',
    'PIL',
    'PIL.Image',
]

# Add all src modules
hiddenimports += collect_submodules('src')

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[str(project_root), str(src_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='BreakGuard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/logo.ico' if Path('assets/logo.ico').exists() else None,
    version_file='version_info.txt' if Path('version_info.txt').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='BreakGuard',
)
