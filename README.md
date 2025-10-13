# Star Conflict Chat Translator

<div align="center">
  <h1>🌍 Real-time Multilingual Chat Translation for Star Conflict</h1>

  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg" alt="Platform Support">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Status">
  <br>
  <img src="https://img.shields.io/badge/Game-Star%20Conflict-orange.svg" alt="Game">
  <img src="https://img.shields.io/badge/Translation-12%20Languages-blue.svg" alt="Languages">
</div>

## 📖 Table of Contents

- [✨ Overview](#-overview)
- [🎯 Key Features](#-key-features)
- [🚀 Quick Start](#-quick-start)
- [📋 System Requirements](#-system-requirements)
- [💾 Installation](#-installation)
- [🎮 Usage](#-usage)
- [⚙️ Configuration](#️-configuration)
- [🔧 Development](#-development)
- [🎮 Game Dictionary](#-game-dictionary)
- [🆘 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)

## ✨ Overview

**Star Conflict Chat Translator** is a desktop application that provides **real-time multilingual chat translation** for the popular space combat game *Star Conflict*. Designed to enhance the gaming experience for international players, it automatically detects and translates in-game chat messages using Google Translate with **fully customizable language support** that you can configure through the settings, making communication seamless across language barriers.

The application monitors your game's chat logs in real-time, translates messages using Google Translate's advanced AI, and displays them with color-coded formatting. Whether you're coordinating with your squad in different languages or trading with international players, this tool ensures you never miss an important message again.

### 🎯 Why Choose Star Conflict Chat Translator?

- **🌍 Universal Communication**: Break down language barriers in one of gaming's most international communities
- **⚡ Real-time Performance**: Instant translation with minimal latency
- **🎨 Modern Interface**: Modern dark theme with intuitive color-coded chat categories
- **🔧 Customizable**: Settings for language preferences and game integration
- **📱 Cross-Platform**: Works on Windows, Linux, and macOS
- **🆓 Free & Open Source**: MIT licensed, no hidden costs or subscriptions

## 🎯 Key Features

### 🌍 **Multilingual Support**
- **Customizable Language Support**: Configure your preferred languages through Google Translate settings
- **12 Default Languages Included**: Possibility to choose from 12 languages ​​supported by Google Translator, e.g. English, Spanish, French, German, Polish, Portuguese, Russian, Japanese, Arabic, Hindi
- - **Automatic Language Detection**: Smart detection of message languages
- **Bidirectional Translation**: Translate to and from any configured language

### ⚡ **Real-time Translation**
- **Instant Processing**: Translates messages as they appear in chat
- **Low Latency**: Optimized for gaming performance
- **Background Operation**: Runs seamlessly while you play

### 🎮 **Game Integration**
- **Automatic Detection**: Finds your Star Conflict installation automatically
- **Log Monitoring**: Real-time monitoring of chat.log files
- **Channel Categorization**: Color-coded display for different chat types:
  - 🟦 **Trading** (Light Grey)
  - 🟩 **Clan** (Lime Green)
  - 🟥 **Battle** (Cornflower Blue)
  - 🟨 **Squad** (Dark Orange)
  - 🟪 **Private** (Medium Orchid)

### 🎨 **Modern Interface**
- **Dark Theme**: Easy on the eyes during long gaming sessions
- **Responsive Design**: Adapts to different screen sizes
- **Intuitive Controls**: Simple one-click language switching
- **Status Indicators**: Real-time connection and processing status

### 🔧 **Advanced Features**
- **Community Game Dictionary**: Override translations for game-specific terms with community-maintained translations
- **Local Chat Archive**: Private database storing all translated conversations locally
- **Real-Time Chat Monitoring**: See all game chat tabs simultaneously, even during combat
- **Built-in Translation Tool**: Integrated Google Translate without external tools
- **Remote Updates**: Automatic dictionary and welcome message updates
- **Export Functionality**: Save chat history to CSV for analysis
- **Clipboard Integration**: One-click copying of translations
- **Version Control**: Automatic update notifications

## 🚀 Quick Start

### For Users (Pre-built Executable)

1. **Download** the latest release from the [Releases](../../releases) page
2. **Extract** the ZIP file to your preferred location
3. **Run** `SC_Chat_Translator.exe` (Windows) or the appropriate executable for your platform
4. **Configure** your preferred translation language in Settings
5. **Start** Star Conflict and enjoy multilingual chat!

### For Developers (From Source)

```bash
# Clone the repository
git clone https://github.com/boruta-project/star-conflict-chat-translator.git
cd star-conflict-chat-translator

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

> 📝 **First-time Setup**: The application will automatically detect your Star Conflict installation and create necessary configuration files.

## 📋 System Requirements

### Minimum Requirements
- **Operating System**: Windows 10, Ubuntu 18.04+, or macOS 10.14+
- **Python**: 3.8 or higher (for source installation)
- **RAM**: 256 MB
- **Storage**: 50 MB free space
- **Internet**: Required for Google Translate API

### Recommended Requirements
- **Operating System**: Windows 10/11, Ubuntu 20.04+, or macOS 11+
- **Python**: 3.9 or higher
- **RAM**: 512 MB
- **Storage**: 100 MB free space
- **Internet**: Stable broadband connection

### Game Requirements
- **Star Conflict**: Latest version installed
- **Game Account**: Active account with chat access
- **Log Files**: Chat logging enabled in game settings

## 💾 Installation

### Option 1: Pre-built Executable (Recommended for Users)

1. Visit the [Releases](../../releases) page
2. Download the latest version for your operating system
3. Extract the archive to your desired location
4. Run the executable file
5. The application will create its configuration files automatically

### Option 2: From Source Code (For Developers)

#### Windows
```batch
# Clone repository
git clone https://github.com/boruta-project/star-conflict-chat-translator.git
cd star-conflict-chat-translator

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

#### Linux/macOS
```bash
# Clone repository
git clone https://github.com/boruta-project/star-conflict-chat-translator.git
cd star-conflict-chat-translator

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Automated Installation Scripts

We've provided automated installation scripts for your convenience:

- **Windows**: Run `install_windows.bat`
- **Linux**: Run `install_linux.sh`
- **macOS**: Run `install_macos.sh`

These scripts will:
- Create a virtual environment
- Install all required dependencies
- Set up the application for first run
- Create desktop shortcuts (where supported)

## 🎮 Usage

### Basic Operation

1. **Launch** the application
2. **Select** your preferred translation language from the Settings tab
3. **Start** Star Conflict
4. **Play** normally - translations appear automatically in the Chat tab

### Interface Overview

The application features a clean, tabbed interface:

#### 🗨️ **Chat Tab**
- **Real-time Translations**: See translated messages as they arrive
- **Original Messages**: View original text in grey
- **Category Colors**: Different colors for different chat types
- **Manual Translation**: Translate custom text using the input field

#### 📊 **History Tab**
- **Date-based Browsing**: View chat history by date
- **Session Playback**: Review entire gaming sessions
- **Search Functionality**: Find specific messages or players

#### 📋 **App Log Tab**
- **Debug Information**: Monitor application performance
- **Error Messages**: Troubleshoot issues
- **Connection Status**: Verify Google Translate connectivity

#### ⚙️ **Settings Tab**
- **Language Selection**: Choose your translation preferences
- **Game Path Configuration**: Set custom game installation paths
- **Dictionary Management**: Add custom translations
- **Remote Updates**: Configure automatic updates

### Advanced Features

#### Local Chat Archive
The application creates a local database that stores all translated chat messages:
- **Review past conversations** with friends and clan members
- **Search through chat history** using the History tab
- **Export conversations** for record-keeping
- **Complete privacy** - database stays only on your computer

#### Real-Time Chat Monitoring
See **all chat tabs simultaneously**, even when the game interface doesn't show them:
- **Trading chat** in open space
- **Clan discussions** while on missions
- **Messages from friends** visible during battle
- **Read-only access** - no interaction with game code

#### Built-in Translation Tool
**Integrated Google Translate** functionality:
- **Translate any text** without opening additional tools
- **Automatic clipboard copy** for easy pasting into game
- **Works offline** once translations are cached
- **Fast and convenient** for quick communications

#### Community Game Dictionary
Contribute to and benefit from community-maintained translations for game-specific terms:
1. Go to Settings → "Open Game Dictionary"
2. Add key-value pairs (e.g., "xpam" → "temple")
3. Save and reload the application
4. **Contribute back**: Help improve translations for all players by updating the community dictionary on GitHub

#### Manual Translation
Translate any text instantly:
1. Type or paste text in the input field at the bottom of the Chat tab
2. Select your target language
3. Press Enter or click the language button

## ⚙️ Configuration

### Language Settings

```json
{
  "last_language": "English",
  "manual_translate_lang": "ru",
  "languages": {
    "English": "en",
    "Russian": "ru",
    "German": "de"
  }
}
```

### Game Path Configuration

The application automatically detects Star Conflict installations, but you can manually configure paths:

**Default Locations:**
- **Windows**: `%USERPROFILE%\Documents\My Games\StarConflict\logs`
- **Linux**: `~/Documents/My Games/StarConflict/logs`
- **macOS**: `~/Documents/My Games/StarConflict/logs`

### Remote Updates

The application supports automatic updates for:
- **Dictionary Updates**: New game terms and translations
- **Welcome Messages**: Important announcements and news
- **Version Notifications**: Update alerts for new releases

## 🔧 Development

### Project Structure

```
star-conflict-chat-translator/
├── main.py                 # Main application entry point
├── game_dictionary.json    # Community-maintained game terms dictionary
├── requirements.txt        # Python dependencies
├── requirements-dev.txt    # Development dependencies
├── pyproject.toml          # Modern Python project configuration
├── MANIFEST.in            # Package manifest for distribution
├── assets/                 # Static assets
│   ├── logo.ico           # Application icon
│   └── help_blue.png      # Help icons
├── docs/                  # Documentation
│   ├── game-dictionary.md # Dictionary contribution guide
│   ├── user-guide.md      # Complete user manual
│   ├── installation.md    # Installation instructions
│   ├── troubleshooting.md # Troubleshooting guide
│   ├── development.md     # Development documentation
│   └── ...                # Other documentation
├── scripts/               # Build and installation scripts
│   ├── build.py           # Build automation script
│   ├── install_windows.bat # Windows installer
│   ├── install_linux.sh   # Linux installer
│   └── install_macos.sh   # macOS installer
├── src/                   # Source code
│   └── sc_translator/     # Main package
│       ├── __init__.py
│       └── main.py        # Main application module
├── tests/                 # Unit tests
│   ├── __init__.py
│   ├── test_main.py       # Main module tests
│   └── test_translator.py # Translation functionality tests
├── .github/               # GitHub configuration
├── .gitignore            # Git ignore rules
├── CHANGELOG.md          # Version history
├── CONTRIBUTING.md       # Contribution guidelines
├── LICENSE               # MIT license
└── README.md             # This file
```

### Dependencies

```txt
customtkinter>=5.2.0
Pillow>=9.0.0
googletrans>=4.0.0rc1
pyperclip>=1.8.0
```

### Building Executables

#### Windows
```batch
pip install pyinstaller
pyinstaller --windowed --icon=assets/logo.ico --add-data "assets;assets" main.py
```

#### Linux/macOS
```bash
pip install pyinstaller
pyinstaller --windowed --icon=assets/logo.ico --add-data "assets:assets" main.py
```

## 🎮 Game Dictionary

### Community-Maintained Translations

The `game_dictionary.json` file contains community-contributed translations for game-specific terms that improve translation accuracy beyond standard Google Translate. This dictionary includes:

- **Ship names and classes** (Tornado, Mammoth, Kusarigama)
- **Weapon and equipment names** (Plasma Gun, Tai'thaq 17)
- **Game-specific terminology** (spec ops, xpam, CNC)
- **Faction and location names**
- **Common gaming phrases and slang**

### Updating Your Dictionary

**Easy Method (Recommended):**
- In the app, go to Settings → "Open Game Dictionary"
- Edit the JSON file in your text editor
- Save and click "Update / Reload Dictionary"

**Manual Method:**
- Find the file: `C:\Users\[YourName]\AppData\Local\ScTranslationApp\game_dictionary.json`
- Edit with any text editor
- Restart the app to reload changes

### Contributing to the Community

Help improve translations for all players:

1. **Edit directly on GitHub**: Navigate to `game_dictionary.json` and click "Edit this file"
2. **Add translations**: Use the format `"original_term": "translated_term"`
3. **Test your changes**: Verify translations work correctly in-game
4. **Create a pull request**: Submit your improvements for review

**Example contribution:**
```json
"new_game_term": "translated_term",
"another_ship": "ship_translation"
```

### Dictionary Guidelines

- ✅ **Accurate translations** - Verify translations are correct in gaming context
- ✅ **Consistent formatting** - Follow existing JSON structure
- ✅ **No duplicates** - Check if terms already exist
- ✅ **Test entries** - Ensure they improve in-game translations
- ✅ **Community benefit** - Focus on commonly used terms

**Current status**: 335+ community-contributed translations across ship names, weapons, and terminology.

*Learn more: [Game Dictionary Guide](docs/game-dictionary.md)*

## 🆘 Troubleshooting

### Common Issues

#### ❌ "Application can't find Star Conflict logs"

**Solution:**
1. Manually set the logs path in Settings → "Browse"
2. Default path: `Documents\My Games\StarConflict\logs`
3. Ensure Star Conflict is installed and has been run at least once

#### ❌ "Translation not working"

**Solutions:**
1. Check your internet connection
2. Verify Google Translate accessibility (may be blocked in some regions)
3. Try switching to a different translation language
4. Check the App Log tab for error messages

#### ❌ "Chat not updating"

**Solutions:**
1. Ensure Star Conflict is running
2. Verify that chat logging is enabled in game settings
3. Check that `chat.log` files are being created in the logs folder
4. Restart both the game and the translator application

#### ❌ "Application won't start"

**Solutions:**
1. Ensure Python 3.8+ is installed
2. Try running from command line: `python main.py`
3. Check for missing dependencies: `pip install -r requirements.txt`
4. Verify all required files are present

### Performance Optimization

- **Close unnecessary applications** to free up RAM
- **Use SSD storage** for faster log file reading
- **Disable remote dictionary updates** if experiencing lag
- **Lower translation frequency** in high-traffic scenarios

### Getting Help

1. **Check existing issues** in the [Issues](../../issues) section
2. **Search the documentation** for your specific problem
3. **Create a new issue** with detailed information:
   - Operating system and version
   - Python version
   - Application version
   - Steps to reproduce the issue
   - Error messages from the App Log tab

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Ways to Contribute

- 🐛 **Bug Reports**: Found a bug? [Create an issue](../../issues/new)
- 💡 **Feature Requests**: Have an idea? [Suggest it](../../issues/new)
- 🔧 **Code Contributions**: Fix bugs or add features
- 📚 **Documentation**: Improve guides and tutorials
- 🌍 **Translations**: Help translate the application
- 🎮 **Game Dictionary**: Contribute translations for game-specific terms

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes and test thoroughly
4. **Commit** your changes: `git commit -m 'Add amazing feature'`
5. **Push** to your branch: `git push origin feature/amazing-feature`
6. **Create** a Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Include unit tests for new features
- Update documentation for significant changes

### Testing

```bash
# Run basic tests
python -m pytest

# Test with sample data
python test_remote_welcome.py

# Manual testing checklist
- [ ] Application starts without errors
- [ ] Language selection works
- [ ] Translation functions properly
- [ ] Settings are saved correctly
- [ ] No console errors during operation
```

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](../LICENSE) file for details.

### Permissions
- ✅ **Commercial Use**: You can use this software for commercial purposes
- ✅ **Modification**: You can modify the source code
- ✅ **Distribution**: You can distribute copies of the software
- ✅ **Private Use**: You can use the software privately

### Limitations
- ❌ **No Liability**: The software is provided "as is" without warranty
- ❌ **No Trademark Rights**: This license doesn't grant trademark rights

### Conditions
- 🔄 **Include Copyright**: You must include the copyright notice
- 🔄 **Include License**: You must include the license text
- 🔄 **State Changes**: If you modify the source, you must state the changes

## 🙏 Acknowledgments

### 🌟 Special Thanks

- **Star Conflict Community**: For creating such an amazing international gaming experience
- **Google Translate**: For providing the translation engine that makes this possible
- **CustomTkinter**: For the beautiful modern GUI framework
- **Open Source Community**: For the countless libraries and tools

### 🎮 Game Credits

*Star Conflict* is a trademark of [Gaijin Entertainment](https://gaijin.net/). This tool is not officially affiliated with or endorsed by Gaijin Entertainment.

### 🤝 Contributors

- **Hystrix** (Project Creator & Lead Developer)
- **Community Contributors** (Bug fixes, features, documentation)

### 📚 Resources

- [Star Conflict Official Website](https://star-conflict.com/)
- [Gaijin Entertainment](https://gaijin.net/)
- [CustomTkinter Documentation](https://customtkinter.tomschimansky.com/)
- [Googletrans Library](https://py-googletrans.readthedocs.io/)

---

<div align="center">

**Made with ❤️ for the Star Conflict community**

*Breaking language barriers, one translation at a time*

[⭐ Star this repository](../../stargazers) • [🐛 Report issues](../../issues) • [📧 Contact](mailto:borutaproject@gmail.com)

</div>
