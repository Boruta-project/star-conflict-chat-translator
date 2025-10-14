# Star Conflict Chat Translator - User Guide

<div align="center">
  <h1>📚 Complete User Manual</h1>
  <p><em>Your comprehensive guide to multilingual gaming</em></p>
</div>

## 📖 Table of Contents

- [🚀 Getting Started](#-getting-started)
- [⚙️ First-Time Setup](#️-first-time-setup)
- [🎮 Using the Application](#-using-the-application)
- [🗨️ Chat Tab Guide](#-chat-tab-guide)
- [📊 History Tab Guide](#-history-tab-guide)
- [📋 App Log Tab Guide](#-app-log-tab-guide)
- [⚙️ Settings Configuration](#️-settings-configuration)
- [🔧 Advanced Features](#-advanced-features)
- [🎨 Customization](#-customization)
- [📱 Mobile & Remote Access](#-mobile--remote-access)
- [🔍 Troubleshooting](#-troubleshooting)
- [❓ FAQ](#-faq)

## 🚀 Getting Started

### Welcome to Star Conflict Chat Translator!

This guide will walk you through everything you need to know to get started with real-time multilingual chat translation for Star Conflict.

### What This Application Does

- **🌍 Translates** in-game chat messages using Google Translate with fully customizable language support
- **⚡ Works in real-time** as messages appear
- **🎨 Color-codes** different types of chat (Trading, Battle, Clan, etc.)
- **📱 Integrates seamlessly** with your gaming experience
- **🔧 Customizable** to match your preferences

### System Requirements Check

Before you begin, ensure your system meets these requirements:

- ✅ **Operating System**: Windows 10+, Ubuntu 18.04+, or macOS 10.14+
- ✅ **Python**: 3.8+ (if running from source)
- ✅ **RAM**: At least 256 MB available
- ✅ **Internet**: Stable connection for Google Translate
- ✅ **Star Conflict**: Game installed and playable

## ⚙️ First-Time Setup

### Step 1: Download and Installation

#### Option A: Pre-built Executable (Recommended)

1. **Visit** the [Releases](https://sites.google.com/view/sc-chat-translator) page on Google Sites
2. **Download** the latest version for your operating system:
   - `SC_Chat_Translator_Windows.zip` for Windows
   - `SC_Chat_Translator_Linux.tar.gz` for Linux (currently unavailable)
   - `SC_Chat_Translator_macOS.zip` for macOS (currently unavailable)
3. **Extract** the archive to your desired location
4. **Run** the executable:
   - Windows: `SC_Chat_Translator.exe`
   - Linux: `./SC_Chat_Translator` (currently unavailable)
   - macOS: `SC_Chat_Translator.app` (currently unavailable)

#### Option B: From Source Code

```bash
# Download the source code
git clone https://github.com/boruta-project/star-conflict-chat-translator.git
cd star-conflict-chat-translator

# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Step 2: Initial Configuration

When you first run the application, you'll see:

1. **Welcome Screen** with application information
2. **Automatic Setup** detecting your Star Conflict installation
3. **Language Selection** prompt

#### Game Detection

The application will automatically try to find your Star Conflict installation:

**Default Search Paths:**
- **Windows**: `C:\Users\[YourName]\Documents\My Games\StarConflict\logs`
- **Linux**: `~/Documents/My Games/StarConflict/logs`
- **macOS**: `~/Documents/My Games/StarConflict/logs`

If automatic detection fails, you'll be prompted to manually select the logs folder.

### Step 3: Language Configuration

1. **Go to** the Settings tab
2. **Select** your preferred translation language from the dropdown
3. **Choose** your manual translation language if different
4. **Click** "Apply Changes" to save

**Recommended Settings for New Users:**
- **Chat Translation**: Your native language or English (en) - most common in international games
- **Manual Translation**: The language in which we would like to communicate

### Step 4: Test the Setup

1. **Start** Star Conflict
2. **Join** a game or chat channel
3. **Observe** the Chat tab in the translator
4. **Verify** messages are being translated

## 🎮 Using the Application

### Main Interface Overview

The application uses a **tabbed interface** with four main sections:

#### 🗨️ **Chat Tab** (Primary)
Real-time translation display and manual translation input

#### 📊 **History Tab**
Browse and search previous chat sessions

#### 📋 **App Log Tab**
Monitor application status and troubleshoot issues

#### ⚙️ **Settings Tab**
Configure languages, paths, and preferences

### Status Indicators (not yet implemented)

**Bottom Status Bar:**
- 🟢 **Green**: Connected and translating
- 🟡 **Yellow**: Connecting or minor issues
- 🔴 **Red**: Connection problems or errors

**Status Messages:**
- "Processing chat.log..." - Normal operation
- "Translation error: [details]" - Google Translate issues
- "Game logs not found" - Path configuration needed

## 🗨️ Chat Tab Guide

### Real-Time Translation Display

#### Message Format

```
[2024-01-15 14:30:22] [Battle] [PlayerName]:
>   '¡Vamos al punto B!' (Spanish)
→ 'Let's go to point B!' (English)
```

#### Color Coding System

| Chat Type | Color | Description |
|-----------|-------|-------------|
| **Trading** 🛒 | Light Grey | `#trading>` messages |
| **Battle** ⚔️ | Cornflower Blue | `#battle_` messages |
| **Squad** 👥 | Dark Orange | `#squad_` messages |
| **Clan** 🏰 | Lime Green | `#clan_` messages |
| **Private** 💬 | Medium Orchid | Private messages |
| **General** 🌍 | Light Blue | Language-specific channels |

#### Message Components

1. **Timestamp**: When the message was received
2. **Category**: Type of chat channel
3. **Username**: Player who sent the message
4. **Original**: Original message in source language (grey)
5. **Translation**: Translated message in target language

### Manual Translation Feature

#### How to Use

1. **Locate** the input field at the bottom of the Chat tab
2. **Type or paste** the text you want to translate
3. **Select** your target language using the dropdown (Settings option) or button (selected language)
4. **Press Enter** or click the language button
The translated message will be displayed in the app's chat window and automatically copied to the clipboard.

#### Example Usage

```
Input: "Où est le point de rendez-vous?"
Button: FR (French to your selected language)
Output:
[Manual Translation → English]
>   'Où est le point de rendez-vous?'
→ 'Where is the meeting point?'
```

#### Advanced Manual Translation

- **Multi-line**: Paste entire paragraphs for translation
- **Mixed Languages**: The app will detect the source language automatically
- **Clipboard**: Translations are automatically copied to your clipboard
- **History**: Manual translations are not saved to chat history

### Translation Quality Tips

#### Best Practices

1. **Complete Sentences**: Better translation quality than fragments
2. **Context Matters**: Game-specific terms may need custom dictionary entries
3. **Language Mixing**: Avoid mixing multiple languages in one message
4. **Special Characters**: Some Cyrillic or Asian characters may display differently

#### Handling Translation Issues

- **Poor Quality**: Try rephrasing the original message
- **Missing Context**: Add custom dictionary entries for game terms
- **Connection Issues**: Check your internet connection
- **Rate Limiting**: Google Translate has usage limits; wait a few minutes

## 📊 History Tab Guide

### Browsing Chat History

#### Date-Based Navigation

1. **Enter** a date in YYYY-MM-DD format (e.g., `2024-01-15`)
2. **Click** "Load Date" to view all messages from that day
3. **Scroll** through the chronological message list

#### Session-Based Navigation

1. **Click** "Load Last Session" to view your most recent gaming chat session
2. **Browse** messages from your last play session
3. **Use** for reviewing strategies or important communications

### History Format

```
[2024-01-15 14:30:22] [Battle] [PlayerName]: ¡Vamos al punto B!
→ Let's go to point B!

[2024-01-15 14:30:25] [Trading] [Trader123]: Vendo módulos baratos
→ Selling cheap modules
```

### Exporting History (not yet implemented)

#### CSV Export Feature

```bash
# Export current history to CSV
# File will be saved as: history_export.csv
# Contains: timestamp, category, username, message, translated, lang, session_id
```

**Use Cases:**
- **Analysis**: Review your gaming communication patterns
- **Reporting**: Document important in-game events
- **Backup**: Preserve chat history for future reference
- **Sharing**: Export specific conversations

### Search and Filter

While the current version doesn't have advanced search, you can:

- **Date Filtering**: Load specific dates to find messages
- **Manual Search**: Use your system's find function (Ctrl+F)
- **Category Focus**: Look for specific chat types by color

## 📋 App Log Tab Guide

### Understanding Log Messages

#### Log Levels

- **INFO**: Normal operation messages
- **WARNING**: Potential issues that don't stop operation
- **ERROR**: Problems that may affect functionality
- **DEBUG**: Detailed technical information

#### Common Log Messages

```
INFO: Application started
INFO: Switched to logfile C:\Users\...\chat.log
INFO: Remote welcome updated to id=0003
WARNING: Remote dictionary fetch failed
ERROR: Translation failed: [details]
```

### Using Logs for Troubleshooting

#### Connection Issues

```
WARNING: Remote welcome fetch failed: [URLError]
INFO: Retrying connection in 5 minutes
```

**Solutions:**
1. Check your internet connection
2. Verify firewall settings
3. Try restarting the application
4. Check if Google Translate is accessible in your region

#### Translation Errors

```
ERROR: Translation failed: HTTP 429
WARNING: Rate limit exceeded, waiting...
```

**Solutions:**
1. Reduce translation frequency
2. Wait a few minutes for rate limits to reset
3. Switch to a different translation service (future feature)

#### File System Issues

```
ERROR: Error opening logfile: [PermissionError]
WARNING: Game logs path not found
```

**Solutions:**
1. Run the application as administrator (Windows)
2. Check file permissions on the logs folder
3. Manually set the correct game logs path in Settings

### Log File Management

#### Automatic Rotation

- **File Size**: 1 MB maximum per log file
- **Backup Count**: 5 old log files kept
- **Location**: `%LOCALAPPDATA%\ScTranslationApp\logs\app.log`

#### Manual Log Access

1. **Go to** App Log tab
2. **Click** "Open Log File" to view in your default text editor
3. **Scroll** to recent entries for troubleshooting
4. **Search** for specific error messages or timestamps

## ⚙️ Settings Configuration

### Language Settings

#### Chat Translation Language

```json
"last_language": "English"
```

**Options:**
- English, Spanish, French, German, Italian, Polish, Portuguese
- Russian, Japanese, Chinese (Simplified), Arabic, Hindi

**Recommendation:** Choose English for international games, or your native language for local communities.

#### Manual Translation Language

```json
"manual_translate_lang": "ru"
```

**Use Case:** Different from chat translation for quick personal translations.

### Game Integration

#### Automatic Path Detection

The application automatically searches for:

```
Windows: %USERPROFILE%\Documents\My Games\StarConflict\logs
Linux: ~/Documents/My Games/StarConflict/logs
macOS: ~/Documents/My Games/StarConflict/logs
```

#### Manual Path Configuration

1. **Go to** Settings tab
2. **Click** "Browse" next to "StarConflict game logs folder"
3. **Navigate** to your Star Conflict logs directory
4. **Select** the `logs` folder
5. **Click** "Save Path"

#### Verifying Path Configuration

- ✅ **Green status**: Path found and accessible
- ⚠️ **Yellow status**: Path exists but no recent chat files
- ❌ **Red status**: Path not found or inaccessible

### Dictionary Management

#### Custom Dictionary Overview

The application includes a built-in dictionary for game-specific terms:

```json
{
  "xpam": "temple",
  "cnc": "thank you",
  "co+": "spec ops +",
  "cow+": "spec ops +"
}
```

#### Adding Custom Entries

1. **Go to** Settings → "Open Game Dictionary"
2. **Add** key-value pairs in JSON format
3. **Save** the file
4. **Click** "Update / Reload Dictionary" in Settings

#### Remote Dictionary

```json
"allow_remote_dictionary": true
```

**Benefits:**
- Automatic updates with new game terms
- Community-contributed translations
- Reduced manual maintenance

### Remote Updates

#### Welcome Messages

```json
"remote_welcome_id": "0003"
"welcome_counter": 5
```

**Features:**
- Automatic important announcements
- Version update notifications
- Community news and updates

#### Update Frequency

```json
"remote_fetch_interval": 3600
```

**Default:** 1 hour between update checks
**Range:** 300 seconds (5 minutes) to 86400 seconds (24 hours)

## 🔧 Advanced Features

### Command Line Options

```bash
# Run with debug logging
python main.py --debug

# Specify custom config path
python main.py --config /path/to/settings.json

# Run in portable mode
python main.py --portable
```

### API Integration

#### Google Translate API

- **Service**: googletrans Python library
- **Rate Limits**: ~100 requests per hour
- **Fallback**: Automatic retry with exponential backoff

#### Custom Translation Services

Future versions may support:
- DeepL API (premium)
- Microsoft Translator
- Yandex Translate
- Local translation models

### Performance Optimization

#### Memory Usage

- **Base Memory**: ~50 MB
- **Per Hour of Chat**: ~10 MB
- **Peak Usage**: ~200 MB during intense battles

#### CPU Usage

- **Idle**: <1% CPU
- **Active Translation**: 5-15% CPU
- **Background Monitoring**: 2-5% CPU

### Backup and Restore

#### Configuration Backup

```bash
# Manual backup
copy settings.json settings_backup.json
copy game_dictionary.json dictionary_backup.json
```

#### Automatic Backups

The application automatically creates backups of:
- Settings files on major updates
- Dictionary files when modified
- Log files (rotated, 5 generations kept)

## 🎨 Customization

### Theme Customization

#### Dark Theme (Default)

```python
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")
```

#### Light Theme (Alternative)

```python
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")
```

### Color Scheme Modification

#### Chat Category Colors

Located in `main.py`:

```python
COLOR_CATEGORIES = {
    "Trading": "lightgrey",
    "English": "lightblue",
    "Battle": "CornflowerBlue",
    "Squad": "DarkOrange",
    "Clan": "LimeGreen",
    "Priv_from": "MediumOrchid",
}
```

#### Language Colors

```python
LANGUAGE_COLORS = [
    "lightgreen", "darkblue", "purple", "brown",
    "teal", "darkred", "orange", "navy",
    "maroon", "darkmagenta", "darkcyan", "olive"
]
```

### Font and Display

#### Interface Scaling

```python
ctk.set_widget_scaling(1.0)  # Default
ctk.set_widget_scaling(1.2)  # Larger interface
ctk.set_widget_scaling(0.8)  # Smaller interface
```

#### Font Customization

```python
# Default font settings
font_family = "Segoe UI"
font_size = 10
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+T` | Focus manual translation input |
| `Enter` | Execute manual translation |
| `Ctrl+L` | Open application log |
| `Ctrl+S` | Save current settings |
| `F5` | Refresh/Reload settings |

## 📱 Mobile & Remote Access

### Remote Monitoring (Future Feature)

While not currently implemented, planned features include:

- **Web Interface**: Access translations via browser
- **Mobile App**: Companion app for Android/iOS
- **Remote API**: REST API for third-party integrations
- **Discord Integration**: Send translations to Discord channels

### Current Workarounds

#### Remote Desktop
- Use Windows Remote Desktop or TeamViewer
- Access the application from another computer

#### Shared Folders
- Store chat logs on network drives
- Run the translator on a dedicated machine

## 🔍 Troubleshooting

### Quick Diagnosis Guide

#### Step 1: Check Status Indicators

1. **Green Status**: Everything working normally
2. **Yellow Status**: Minor issues, check logs
3. **Red Status**: Major problems, immediate attention needed

#### Step 2: Review Recent Logs

1. **Go to** App Log tab
2. **Look for** ERROR or WARNING messages in the last 5 minutes
3. **Note** any patterns or repeated errors

#### Step 3: Test Basic Functionality

1. **Manual Translation**: Try translating "Hello world"
2. **Settings Save**: Change a setting and restart
3. **File Access**: Verify log files are being created

### Common Issues and Solutions

#### Issue: "No chat messages appearing"

**Symptoms:**
- Chat tab remains empty
- Status shows "Processing chat.log..." but no messages

**Solutions:**
1. **Verify Game Path**: Check Settings → Game logs path is correct
2. **Check File Permissions**: Ensure read access to chat.log files
3. **Restart Game**: Sometimes chat logging needs game restart
4. **Check Game Settings**: Verify chat logging is enabled in Star Conflict

#### Issue: "Translations are wrong or missing"

**Symptoms:**
- Messages appear but translations are incorrect
- Some messages show "[Translation error]"

**Solutions:**
1. **Check Internet**: Verify stable internet connection
2. **Language Detection**: Ensure source language is supported
3. **Rate Limiting**: Wait a few minutes if getting 429 errors
4. **Custom Dictionary**: Add game-specific terms

#### Issue: "Application won't start"

**Symptoms:**
- Double-clicking executable does nothing
- Command line shows import errors

**Solutions:**
1. **Dependencies**: Run `pip install -r requirements.txt`
2. **Python Version**: Ensure Python 3.8+ is installed
3. **Virtual Environment**: Activate venv before running
4. **Missing Files**: Verify all files from repository are present

#### Issue: "High CPU or memory usage"

**Symptoms:**
- Application uses excessive system resources
- Computer becomes slow during gaming

**Solutions:**
1. **Close Other Apps**: Free up system resources
2. **Reduce Frequency**: Increase translation intervals
3. **Disable Features**: Turn off remote dictionary updates
4. **Restart Application**: Clear memory leaks

### Advanced Troubleshooting

#### Debug Mode

```bash
# Run with detailed logging
python main.py --debug
```

#### Manual Testing

```python
# Test translation service
from googletrans import Translator
translator = Translator()
result = translator.translate("Hello world", dest="es")
print(result.text)
```

#### Network Diagnostics

```bash
# Test Google Translate connectivity
curl -s "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=es&dt=t&q=hello"
```

## ❓ FAQ

### General Questions

**Q: Is this application free?**
A: Yes, completely free and open source under MIT license.

**Q: Does it work with all Star Conflict versions?**
A: Compatible with all recent versions. May require path updates for major game updates.

**Q: Can I use it for other games?**
A: Currently designed specifically for Star Conflict, but the core translation engine could be adapted.

**Q: Is my chat data stored or sent anywhere?**
A: No, all translations happen locally. Chat logs are only stored on your computer.

### Technical Questions

**Q: Why does it need internet access?**
A: Required for Google Translate API. No internet = no translations.

**Q: Can I run multiple instances?**
A: Not recommended. Each instance monitors the same log files.

**Q: Does it interfere with the game?**
A: No, it's completely passive. Only reads chat logs, never modifies game files.

**Q: What's the translation delay?**
A: Typically 1-3 seconds, depending on internet speed and Google Translate load.

### Language & Translation

**Q: Which languages are supported?**
A: By default, 12 languages ​​are set: English, Spanish, French, German, Italian, Polish, Portuguese, Russian, Japanese, Chinese (Simplified), Arabic, Hindi.

**Q: Can I add more languages?**
A: The app supports 12 languages, set in the settings.json file. You can change them to your preferred languages.

**Q: Why are some translations poor quality?**
A: Game chat often uses abbreviations, slang, and mixed languages. Use the custom dictionary for game-specific terms.

**Q: Can I change the translation service?**
A: Currently only Google Translate. Alternative services may be added in future versions.

### Performance & Compatibility

**Q: Does it work on Mac/Linux?**
A: Yes, full support for all major platforms.

**Q: What's the system impact?**
A: Minimal - typically <5% CPU and <100MB RAM.

**Q: Can I use it without Python installed?**
A: Yes, download the pre-built executable for your platform.

**Q: Does it support multiple monitors?**
A: Yes, the application window can be moved to any monitor.

### Support & Updates

**Q: How do I report bugs?**
A: Create an issue on GitHub with detailed information about your problem.

**Q: Are there updates planned?**
A: Yes, active development with regular updates and new features.

**Q: Can I contribute to development?**
A: Absolutely! See the Contributing section in the main README.

**Q: Is there a Discord or community?**
A: Check the GitHub repository for community links and discussions.

---

<div align="center">

**🎮 Happy Gaming in Any Language! 🎮**

*Need more help? Check the [Issues](../../issues) page or create a new issue.*

</div>
