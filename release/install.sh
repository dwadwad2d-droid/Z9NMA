#!/bin/bash
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
