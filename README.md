# 🎮 Roblox Community Analyzer

A powerful desktop application that analyzes Roblox communities to create wealth leaderboards and discover Discord connections.

## ✨ Features

- **🔍 Community Analysis**: Analyze any Roblox community by URL
- **💰 Wealth Leaderboard**: Ranks members by their limited items value
- **🎮 Discord Integration**: Finds community Discord servers and matches users
- **🖥️ Modern UI**: Clean, dark-themed interface with real-time progress
- **📊 Detailed Reports**: Comprehensive analysis with export functionality
- **🔐 Secure Authentication**: Uses your Roblox cookie for authenticated access

## 🚀 Quick Start

### Option 1: Use Pre-built Executable (Recommended)

1. Download the latest release from the releases page
2. Extract the ZIP file
3. Run `install.bat` as administrator for system installation
4. Or run `RobloxCommunityAnalyzer.exe` directly

### Option 2: Run from Source

1. **Install Python 3.8+**
   ```bash
   # Check if Python is installed
   python --version
   ```

2. **Clone/Download the repository**
   ```bash
   git clone <repository-url>
   cd roblox-community-analyzer
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

## 📋 Requirements

- **Operating System**: Windows 10+ (primary), Linux, macOS
- **Python**: 3.8 or higher (if running from source)
- **Internet Connection**: Required for API access
- **Roblox Account**: Must have a valid Roblox account

## 🔧 Setup Instructions

### 1. Get Your Roblox Cookie

1. **Open your browser** and go to [roblox.com](https://www.roblox.com)
2. **Log in** to your Roblox account
3. **Open Developer Tools** (F12 or Right-click → Inspect)
4. **Go to Application tab** → Cookies → https://www.roblox.com
5. **Find `.ROBLOSECURITY`** cookie and copy its value
6. **Paste it** into the application's cookie field

⚠️ **Important**: Keep your cookie secure and never share it with others!

### 2. Find Community URL

1. **Visit the community** you want to analyze on Roblox
2. **Copy the URL** from your browser's address bar
3. **Example format**: `https://www.roblox.com/communities/35461612/Z9-Market#!/about`

## 📖 How to Use

### Basic Usage

1. **Launch the application**
2. **Enter your Roblox cookie** in the secure field
3. **Paste the community URL** you want to analyze
4. **Click "Analyze Community"** and wait for results
5. **View results** in the different tabs:
   - 💰 **Wealth Leaderboard**: Top wealthy members
   - 🎮 **Discord Matches**: Found Discord connections
   - ℹ️ **Community Info**: Basic community details
   - 📋 **Analysis Log**: Detailed process log

### Advanced Features

- **Export Results**: Save analysis data as JSON
- **Real-time Progress**: Monitor analysis progress
- **Error Handling**: Comprehensive error messages
- **Rate Limiting**: Automatic API rate limiting

## 🏗️ Building from Source

To create your own executable:

```bash
# Install build dependencies
pip install pyinstaller

# Run build script
python build.py
```

The executable will be created in the `dist/` folder.

## 🔒 Privacy & Security

- **Your cookie**: Stored only in memory, never saved to disk
- **API Requests**: Made directly to Roblox APIs
- **No Data Collection**: The app doesn't collect or send your data anywhere
- **Local Processing**: All analysis happens on your computer

## ⚠️ Important Notes

### Rate Limiting
- The application includes built-in rate limiting to respect Roblox's API limits
- Large communities may take several minutes to analyze
- Analysis is limited to first 1000 members to prevent timeouts

### Limitations
- **Private Communities**: Cannot analyze private communities you're not a member of
- **Privacy Settings**: Some user data may be limited by privacy settings
- **Discord Matching**: Limited by what users share in their profiles
- **API Changes**: Roblox API changes may affect functionality

### Legal Compliance
- This tool uses public Roblox APIs
- Respects rate limits and terms of service
- For educational and research purposes
- Do not use for harassment or malicious purposes

## 🛠️ Troubleshooting

### Common Issues

**"Invalid cookie" error:**
- Ensure you copied the complete `.ROBLOSECURITY` cookie value
- Try logging out and back into Roblox, then get a fresh cookie
- Check that your account has access to the community

**"Community not found" error:**
- Verify the community URL format is correct
- Ensure the community is public or you're a member
- Check your internet connection

**Application won't start:**
- Ensure all dependencies are installed
- Check Python version (3.8+ required)
- Try running from command line to see error messages

**Slow analysis:**
- Large communities take time due to rate limiting
- Check your internet connection speed
- Consider analyzing smaller communities first

### Getting Help

1. **Check the Analysis Log** tab for detailed error messages
2. **Verify your inputs** (cookie and URL format)
3. **Try with a different community** to isolate issues
4. **Check internet connection** and firewall settings

## 📊 Technical Details

### Architecture
- **Frontend**: CustomTkinter (modern GUI framework)
- **Backend**: Python with requests for API calls
- **Threading**: Async processing for responsive UI
- **Data Processing**: JSON parsing and analysis

### API Endpoints Used
- Roblox Groups API
- Roblox Users API
- Roblox Inventory API
- Discord API (public endpoints)

### Performance
- **Memory Usage**: ~50-100MB typical
- **CPU Usage**: Low, with spikes during analysis
- **Network**: Depends on community size and member count
- **Storage**: Minimal, no persistent data storage

## 🔮 Future Enhancements

- **Multi-community comparison**
- **Historical wealth tracking**
- **Advanced Discord bot integration**
- **More social media platforms**
- **Batch processing capabilities**
- **Web dashboard version**

## 📄 License

This project is for educational purposes. Please ensure compliance with:
- Roblox Terms of Service
- Discord Terms of Service
- Local laws regarding data scraping

## 🤝 Contributing

This is a standalone application, but suggestions and improvements are welcome!

## ⚡ Performance Tips

- **Smaller communities** analyze faster
- **Close other applications** for better performance
- **Stable internet** connection improves reliability
- **Updated Roblox cookie** ensures best results

---

**Disclaimer**: This tool is not affiliated with Roblox Corporation. Use responsibly and in accordance with all applicable terms of service.