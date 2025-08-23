#!/usr/bin/env python3
"""
Release Package Creator
Creates a complete package for distribution
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def create_release_package():
    """Create a complete release package"""
    print("🚀 Creating release package for Roblox Community Analyzer")
    
    # Create release directory
    release_dir = Path('release')
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # Copy executable
    exe_source = Path('dist/RobloxCommunityAnalyzer')
    exe_dest = release_dir / 'RobloxCommunityAnalyzer'
    
    if exe_source.exists():
        shutil.copy2(exe_source, exe_dest)
        print(f"✅ Copied executable: {exe_source} -> {exe_dest}")
    else:
        print("❌ Executable not found! Please run build.py first.")
        return False
    
    # Copy documentation
    docs_to_copy = ['README.md']
    for doc in docs_to_copy:
        if Path(doc).exists():
            shutil.copy2(doc, release_dir / doc)
            print(f"✅ Copied documentation: {doc}")
    
    # Create installation script for Linux/Mac
    linux_install_script = release_dir / 'install.sh'
    with open(linux_install_script, 'w') as f:
        f.write('''#!/bin/bash
echo "Installing Roblox Community Analyzer..."

# Create installation directory
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

# Copy executable
cp "RobloxCommunityAnalyzer" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/RobloxCommunityAnalyzer"

# Create desktop entry
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"

cat > "$DESKTOP_DIR/roblox-community-analyzer.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Roblox Community Analyzer
Comment=Analyze Roblox communities for wealth and Discord connections
Exec=$INSTALL_DIR/RobloxCommunityAnalyzer
Icon=applications-games
Terminal=false
Categories=Game;Utility;
EOF

echo "Installation completed!"
echo "You can run the application from: $INSTALL_DIR/RobloxCommunityAnalyzer"
echo "Or find it in your applications menu."
''')
    
    # Make install script executable
    os.chmod(linux_install_script, 0o755)
    print(f"✅ Created Linux/Mac installer: {linux_install_script}")
    
    # Create Windows batch installer
    windows_install_script = release_dir / 'install.bat'
    with open(windows_install_script, 'w') as f:
        f.write('''@echo off
echo Installing Roblox Community Analyzer...
echo.

REM Create installation directory
if not exist "%LOCALAPPDATA%\\RobloxCommunityAnalyzer" (
    mkdir "%LOCALAPPDATA%\\RobloxCommunityAnalyzer"
)

REM Copy executable (rename for Windows)
copy "RobloxCommunityAnalyzer" "%LOCALAPPDATA%\\RobloxCommunityAnalyzer\\RobloxCommunityAnalyzer.exe"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Roblox Community Analyzer.lnk'); $Shortcut.TargetPath = '%LOCALAPPDATA%\\RobloxCommunityAnalyzer\\RobloxCommunityAnalyzer.exe'; $Shortcut.Save()"

echo.
echo Installation completed!
echo You can find the shortcut on your desktop.
pause
''')
    print(f"✅ Created Windows installer: {windows_install_script}")
    
    # Create usage instructions
    usage_file = release_dir / 'USAGE.txt'
    with open(usage_file, 'w') as f:
        f.write('''ROBLOX COMMUNITY ANALYZER - USAGE INSTRUCTIONS

QUICK START:
1. Run the application (double-click RobloxCommunityAnalyzer)
2. Get your Roblox cookie:
   - Open browser, go to roblox.com and login
   - Press F12, go to Application > Cookies > .ROBLOSECURITY
   - Copy the cookie value and paste in the app
3. Enter community URL (e.g., https://www.roblox.com/communities/12345/CommunityName#!/about)
4. Click "Analyze Community" and wait for results

INSTALLATION:
- Linux/Mac: Run ./install.sh
- Windows: Run install.bat as administrator
- Or run the executable directly

SYSTEM REQUIREMENTS:
- Operating System: Windows 10+, Linux, macOS
- Internet connection required
- Valid Roblox account

FEATURES:
- Wealth Leaderboard: Ranks members by limited items value
- Discord Integration: Finds community Discord servers
- Export Results: Save analysis as JSON file
- Modern UI: Clean interface with progress tracking

TROUBLESHOOTING:
- If "Invalid cookie" error: Get fresh cookie from browser
- If slow analysis: Large communities take time due to rate limiting
- If app won't start: Check internet connection and firewall

For more information, see README.md

DISCLAIMER:
This tool is for educational purposes. Use responsibly and respect
Roblox Terms of Service and Discord Terms of Service.
''')
    print(f"✅ Created usage instructions: {usage_file}")
    
    # Create version info
    version_file = release_dir / 'VERSION.txt'
    with open(version_file, 'w') as f:
        f.write(f'''Roblox Community Analyzer
Version: 1.0.0
Build Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Platform: Cross-platform (Linux/Windows/macOS)

Changes in this version:
- Initial release
- Community member analysis
- Wealth leaderboard based on limiteds
- Discord server discovery
- Modern GUI interface
- Export functionality
- Cross-platform support

For updates and support, check the project repository.
''')
    print(f"✅ Created version info: {version_file}")
    
    # Create ZIP package
    zip_name = f"RobloxCommunityAnalyzer-v1.0.0-{datetime.now().strftime('%Y%m%d')}.zip"
    zip_path = Path(zip_name)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in release_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(release_dir)
                zipf.write(file_path, arcname)
                print(f"📦 Added to ZIP: {arcname}")
    
    print(f"✅ Created release package: {zip_path.absolute()}")
    
    # Show final stats
    exe_size = exe_dest.stat().st_size / (1024*1024)
    zip_size = zip_path.stat().st_size / (1024*1024)
    
    print("\n" + "="*60)
    print("🎉 RELEASE PACKAGE CREATED SUCCESSFULLY!")
    print("="*60)
    print(f"📁 Package: {zip_path.absolute()}")
    print(f"📏 Executable size: {exe_size:.1f} MB")
    print(f"📦 Package size: {zip_size:.1f} MB")
    print(f"📄 Files included:")
    for file_path in release_dir.rglob('*'):
        if file_path.is_file():
            print(f"   - {file_path.name}")
    
    print(f"\n📋 Distribution Instructions:")
    print(f"1. Share the ZIP file: {zip_name}")
    print(f"2. Users extract and run installer for their platform")
    print(f"3. Or run executable directly: RobloxCommunityAnalyzer")
    
    return True

if __name__ == "__main__":
    success = create_release_package()
    if success:
        print("\n✅ Release package creation completed!")
    else:
        print("\n❌ Release package creation failed!")