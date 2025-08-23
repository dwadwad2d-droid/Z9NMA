#!/usr/bin/env python3
"""
Build Script for Roblox Community Analyzer
Creates executable file using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command with error handling"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def create_spec_file():
    """Create PyInstaller spec file for better control"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'customtkinter',
        'tkinter',
        'requests',
        'beautifulsoup4',
        'fake_useragent',
        'PIL',
        'lxml',
        'aiohttp'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='RobloxCommunityAnalyzer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)
'''
    
    with open('main.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ PyInstaller spec file created")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🚀 Starting build process for Roblox Community Analyzer")
    
    # Check if PyInstaller is installed
    if not run_command("pyinstaller --version", "Checking PyInstaller installation"):
        print("Installing PyInstaller...")
        if not run_command("pip install pyinstaller", "Installing PyInstaller"):
            return False
    
    # Create spec file
    create_spec_file()
    
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("🧹 Cleaned previous build directory")
    
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("🧹 Cleaned build cache")
    
    # Build executable
    build_command = "pyinstaller main.spec --clean --noconfirm"
    if not run_command(build_command, "Building executable"):
        return False
    
    # Check if executable was created (Linux/Mac vs Windows)
    exe_path_linux = Path('dist/RobloxCommunityAnalyzer')
    exe_path_windows = Path('dist/RobloxCommunityAnalyzer.exe')
    
    if exe_path_windows.exists():
        exe_path = exe_path_windows
    elif exe_path_linux.exists():
        exe_path = exe_path_linux
    else:
        print("❌ Executable was not created")
        return False
    
    print(f"✅ Executable created successfully: {exe_path.absolute()}")
    print(f"📦 File size: {exe_path.stat().st_size / (1024*1024):.1f} MB")
    return True

def create_installer_script():
    """Create a simple installer script"""
    installer_content = '''@echo off
echo Installing Roblox Community Analyzer...
echo.

REM Create installation directory
if not exist "%LOCALAPPDATA%\\RobloxCommunityAnalyzer" (
    mkdir "%LOCALAPPDATA%\\RobloxCommunityAnalyzer"
)

REM Copy executable
copy "RobloxCommunityAnalyzer.exe" "%LOCALAPPDATA%\\RobloxCommunityAnalyzer\\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Roblox Community Analyzer.lnk'); $Shortcut.TargetPath = '%LOCALAPPDATA%\\RobloxCommunityAnalyzer\\RobloxCommunityAnalyzer.exe'; $Shortcut.Save()"

echo.
echo Installation completed!
echo You can find the shortcut on your desktop.
pause
'''
    
    with open('dist/install.bat', 'w') as f:
        f.write(installer_content)
    
    print("✅ Installer script created")

def main():
    """Main build function"""
    print("=" * 60)
    print("  Roblox Community Analyzer - Build Script")
    print("=" * 60)
    
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Install dependencies if needed
    print("\n📦 Checking dependencies...")
    dependencies = [
        "customtkinter", "requests", "beautifulsoup4", 
        "fake-useragent", "pillow", "lxml", "aiohttp"
    ]
    
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✅ {dep} is installed")
        except ImportError:
            print(f"⚠️  {dep} not found, installing...")
            if not run_command(f"pip install {dep}", f"Installing {dep}"):
                print(f"❌ Failed to install {dep}")
                return False
    
    # Build executable
    if build_executable():
        create_installer_script()
        
        print("\n" + "=" * 60)
        print("  🎉 BUILD COMPLETED SUCCESSFULLY! 🎉")
        print("=" * 60)
        print(f"📁 Executable location: {Path('dist/RobloxCommunityAnalyzer.exe').absolute()}")
        print(f"🔧 Installer script: {Path('dist/install.bat').absolute()}")
        print("\n📝 To distribute:")
        print("  1. Copy the entire 'dist' folder")
        print("  2. Run 'install.bat' on target machine")
        print("  3. Or run 'RobloxCommunityAnalyzer.exe' directly")
        
        return True
    else:
        print("\n❌ Build failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)