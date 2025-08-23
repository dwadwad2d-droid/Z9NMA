@echo off
echo Installing Roblox Community Analyzer...
echo.

REM Create installation directory
if not exist "%LOCALAPPDATA%\RobloxCommunityAnalyzer" (
    mkdir "%LOCALAPPDATA%\RobloxCommunityAnalyzer"
)

REM Copy executable (rename for Windows)
copy "RobloxCommunityAnalyzer" "%LOCALAPPDATA%\RobloxCommunityAnalyzer\RobloxCommunityAnalyzer.exe"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Roblox Community Analyzer.lnk'); $Shortcut.TargetPath = '%LOCALAPPDATA%\RobloxCommunityAnalyzer\RobloxCommunityAnalyzer.exe'; $Shortcut.Save()"

echo.
echo Installation completed!
echo You can find the shortcut on your desktop.
pause
