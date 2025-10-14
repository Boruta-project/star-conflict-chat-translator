# Troubleshooting Guide

<div align="center">
  <h1>🔧 Troubleshooting Guide</h1>
  <p><em>Solutions to common issues and problems</em></p>
</div>

## 📖 Table of Contents

- [🚀 Quick Diagnosis](#-quick-diagnosis)
- [❌ Application Won't Start](#-application-wont-start)
- [🌍 Translation Issues](#-translation-issues)
- [📋 Chat Display Problems](#-chat-display-problems)
- [⚙️ Settings & Configuration](#️-settings--configuration)
- [🌐 Network & Connectivity](#-network--connectivity)
- [💾 Performance Issues](#-performance-issues)
- [🔧 Advanced Troubleshooting](#-advanced-troubleshooting)
- [📞 Getting Help](#-getting-help)

## 🚀 Quick Diagnosis

### Step 1: Check System Requirements

**Minimum Requirements:**
- ✅ Python 3.8+ installed
- ✅ 256 MB RAM available
- ✅ Internet connection
- ✅ Star Conflict game installed

**Check Python Version:**
```bash
python --version
# Should show: Python 3.8.x or higher
```

**Check Available Memory:**
```bash
# Windows
wmic OS get FreePhysicalMemory /Value

# Linux
free -h

# macOS
vm_stat | grep "Pages free"
```

### Step 2: Run Basic Tests

**Test 1: Python Import Test**
```bash
python -c "import tkinter, customtkinter; print('GUI: OK')"
python -c "from googletrans import Translator; print('Translation: OK')"
```

**Test 2: Application Launch Test**
```bash
python main.py --test
# Should show basic functionality without full GUI
```

### Step 3: Check Logs

**View Application Logs:**
1. Open the application
2. Go to "App Log" tab
3. Look for ERROR or WARNING messages
4. Note timestamps and error details

**Log File Location:**
- **Windows**: `%LOCALAPPDATA%\ScTranslationApp\logs\app.log`
- **Linux**: `~/.local/share/ScTranslationApp/logs/app.log`
- **macOS**: `~/Library/Application Support/ScTranslationApp/logs/app.log`

## ❌ Application Won't Start

### Issue: "Python is not recognized"

**Symptoms:**
- Double-clicking executable does nothing
- Command prompt shows "'python' is not recognized"

**Solutions:**

1. **Check Python Installation:**
   ```bash
   # Verify Python is installed
   python --version
   ```

2. **Add Python to PATH (Windows):**
   - Open System Properties → Advanced → Environment Variables
   - Find "Path" in System Variables
   - Add: `C:\Python39\` (adjust for your version)
   - Add: `C:\Python39\Scripts\`
   - Restart command prompt

3. **Reinstall Python:**
   - Download from python.org
   - ✅ Check "Add Python to PATH" during installation
   - ✅ Install for all users (if admin)

### Issue: "Module not found" Errors

**Symptoms:**
- ImportError messages
- "No module named 'customtkinter'"

**Solutions:**

1. **Install Missing Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Upgrade pip:**
   ```bash
   python -m pip install --upgrade pip
   ```

3. **Virtual Environment Issues:**
   ```bash
   # Recreate virtual environment
   rm -rf venv
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Permission Issues:**
   ```bash
   # Run as administrator/sudo
   sudo pip install -r requirements.txt
   ```

### Issue: "Application window doesn't appear"

**Symptoms:**
- Application starts (process visible in Task Manager)
- No window appears
- No error messages

**Solutions:**

1. **Check Display Server (Linux):**
   ```bash
   echo $DISPLAY
   # Should show something like :0 or :1
   ```

2. **GUI Backend Issues:**
   ```bash
   # Force specific tkinter backend
   export TK_SILENCE_DEPRECATION=1
   python main.py
   ```

3. **Reinstall GUI Libraries:**
   ```bash
   pip uninstall tkinter customtkinter
   pip install customtkinter
   ```

## 🌍 Translation Issues

### Issue: "Translation failed" Messages

**Symptoms:**
- Messages show "[Translation error]"
- Some translations work, others don't

**Solutions:**

1. **Check Internet Connection:**
   ```bash
   ping google.com
   ```

2. **Test Google Translate Service:**
   ```bash
   python -c "from googletrans import Translator; t = Translator(); print(t.translate('Hello', dest='es'))"
   ```

3. **Rate Limiting:**
   - Google Translate has usage limits
   - Wait 5-10 minutes between tests
   - Reduce translation frequency in settings

4. **Language Support:**
   - Verify source language is supported
   - Check target language selection
   - Some languages may have limited support

### Issue: Poor Translation Quality

**Symptoms:**
- Translations are inaccurate
- Game-specific terms are wrong

**Solutions:**

1. **Add Custom Dictionary Entries:**
   ```
   Key: xpam
   Value: temple
   ```

2. **Use Complete Sentences:**
   - "Go to point B" → better than "Go B"
   - "Need backup" → better than "Backup pls"

3. **Context Matters:**
   - Game abbreviations need dictionary entries
   - Mixed languages cause confusion

### Issue: "Network timeout" Errors

**Symptoms:**
- Translations take too long
- Connection timeout messages

**Solutions:**

1. **Increase Timeout Settings:**
   ```python
   # In code (advanced users)
   translator = Translator(timeout=10)
   ```

2. **Check Network Speed:**
   ```bash
   speedtest-cli  # Install: pip install speedtest-cli
   ```

3. **Proxy Configuration:**
   ```bash
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   ```

## 📋 Chat Display Problems

### Issue: "No chat messages appearing"

**Symptoms:**
- Chat tab remains empty
- Status shows "Processing chat.log..." but no messages

**Solutions:**

1. **Verify Game Path:**
   - Go to Settings → "Browse"
   - Navigate to Star Conflict logs folder
   - Default: `Documents\My Games\StarConflict\logs`

2. **Check File Permissions:**
   ```bash
   # Windows
   icacls "C:\Users\YourName\Documents\My Games\StarConflict\logs"

   # Linux
   ls -la ~/Documents/My\ Games/StarConflict/logs
   ```

3. **Restart Star Conflict:**
   - Some versions need game restart for logging
   - Verify chat logging is enabled in game settings

4. **Check Log File Creation:**
   ```bash
   # Monitor log directory
   watch -n 1 ls -la /path/to/logs/
   ```

### Issue: Messages in Wrong Language/Category

**Symptoms:**
- Messages categorized incorrectly
- Wrong color coding

**Solutions:**

1. **Update Chat Patterns:**
   - The app uses regex patterns for categorization
   - Some game updates may change message formats

2. **Custom Category Patterns:**
   ```python
   # Advanced: Modify CHAT_CATEGORIES in main.py
   CHAT_CATEGORIES = {
       "#custom>[": "Custom",
       "#newpattern>[": "New Category",
   }
   ```

3. **Language Detection Issues:**
   - Mixed language messages confuse detection
   - Very short messages are hard to categorize

### Issue: Chat Log File Not Found

**Symptoms:**
- "Game logs not found" error
- Red status indicator

**Solutions:**

1. **Manual Path Configuration:**
   - Use Settings → "Browse" button
   - Select the `logs` folder manually

2. **Verify Game Installation:**
   ```bash
   # Check if game is installed
   ls "/path/to/StarConflict"
   ```

3. **Alternative Log Locations:**
   - Some game versions use different paths
   - Check game settings for custom log locations

## ⚙️ Settings & Configuration

### Issue: Settings Not Saving

**Symptoms:**
- Changes don't persist after restart
- Settings reset to defaults

**Solutions:**

1. **Check File Permissions:**
   ```bash
   # Windows
   attrib %LOCALAPPDATA%\ScTranslationApp\settings.json

   # Linux
   ls -la ~/.config/ScTranslationApp/settings.json
   ```

2. **Disk Space:**
   ```bash
   df -h  # Linux/macOS
   wmic logicaldisk get size,freespace  # Windows
   ```

3. **Manual Settings Edit:**
   - Use Settings → "Open Settings File"
   - Edit JSON directly
   - Save and restart application

### Issue: Language Settings Not Working

**Symptoms:**
- Language changes don't take effect
- Wrong language used for translations

**Solutions:**

1. **Apply Settings:**
   - Always click "Apply Changes" after modifications
   - Restart application if changes don't take effect

2. **Language Code Verification:**
   ```python
   # Check language codes in main.py
   LANGUAGES = {
       "English": "en",
       "Spanish": "es",
       # Verify your language is listed
   }
   ```

3. **Reset to Defaults:**
   - Delete settings.json file
   - Application will recreate with defaults

## 🌐 Network & Connectivity

### Issue: "Connection refused" Errors

**Symptoms:**
- Unable to connect to Google Translate
- Network timeout errors

**Solutions:**

1. **Firewall Settings:**
   ```bash
   # Windows: Check firewall rules
   # Linux: Check ufw/iptables
   sudo ufw status
   ```

2. **DNS Issues:**
   ```bash
   nslookup translate.googleapis.com
   ```

3. **VPN/Anti-virus Interference:**
   - Temporarily disable VPN
   - Check anti-virus firewall rules
   - Add exception for Python/Google Translate

### Issue: Slow Translations

**Symptoms:**
- Translations take 5+ seconds
- Application becomes unresponsive

**Solutions:**

1. **Network Speed Test:**
   ```bash
   # Install speedtest-cli
   pip install speedtest-cli
   speedtest
   ```

2. **Server Location:**
   - Google Translate routes to nearest server
   - VPN may route to slower servers

3. **Concurrent Requests:**
   - Reduce number of simultaneous translations
   - Add delays between requests

## 💾 Performance Issues

### Issue: High CPU Usage

**Symptoms:**
- CPU usage >50%
- Computer becomes slow
- Fan runs constantly

**Solutions:**

1. **Reduce Translation Frequency:**
   - Increase delays between translations
   - Process fewer messages per second

2. **Optimize Settings:**
   ```python
   # Reduce logging verbosity
   logging.getLogger().setLevel(logging.WARNING)
   ```

3. **Background Processing:**
   - Ensure watcher threads don't consume main thread
   - Check for infinite loops in log monitoring

### Issue: High Memory Usage

**Symptoms:**
- Memory usage >500MB
- Application becomes slow
- System runs out of RAM

**Solutions:**

1. **Clear Chat History Periodically:**
   ```python
   # Limit stored messages
   MAX_CHAT_HISTORY = 1000
   ```

2. **Memory Leak Detection:**
   ```python
   import tracemalloc
   tracemalloc.start()
   # Monitor memory usage over time
   ```

3. **File Handle Management:**
   ```python
   # Ensure log files are properly closed
   with open(logfile, 'r') as f:
       # Process file
       pass  # File automatically closed
   ```

### Issue: Application Freezes

**Symptoms:**
- UI becomes unresponsive
- No response to clicks
- Must force quit application

**Solutions:**

1. **Threading Issues:**
   - Check for deadlocks in background threads
   - Ensure GUI operations run on main thread

2. **Infinite Loops:**
   ```python
   # Add timeouts to network operations
   import signal
   def timeout_handler(signum, frame):
       raise TimeoutError("Operation timed out")

   signal.signal(signal.SIGALRM, timeout_handler)
   signal.alarm(30)  # 30 second timeout
   ```

3. **Large Log Files:**
   - Split large log files into chunks
   - Process files incrementally

## 🔧 Advanced Troubleshooting

### Debug Mode

**Enable Debug Logging:**
```bash
python main.py --debug
```

**Debug Configuration:**
```python
# Add to main.py
if "--debug" in sys.argv:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
```

### Manual Testing

**Test Individual Components:**
```python
# Test translation service
from googletrans import Translator
translator = Translator()
result = translator.translate("Test message", dest="es")
print(f"Translation: {result.text}")

# Test file monitoring
import os
log_path = "/path/to/chat.log"
if os.path.exists(log_path):
    with open(log_path, 'r') as f:
        print(f"Log file size: {os.path.getsize(log_path)} bytes")
```

### System Information Gathering

**Create System Report:**
```bash
# Windows
systeminfo > system_report.txt

# Linux
uname -a > system_report.txt
lsb_release -a >> system_report.txt

# macOS
sw_vers > system_report.txt
system_profiler SPSoftwareDataType >> system_report.txt
```

### Configuration Backup/Restore

**Backup Settings:**
```bash
cp settings.json settings_backup.json
cp game_dictionary.json dictionary_backup.json
```

**Restore from Backup:**
```bash
cp settings_backup.json settings.json
# Restart application
```

## 📞 Getting Help

### Before Asking for Help

**Gather Information:**
1. ✅ **System Information:** OS, Python version, RAM
2. ✅ **Application Version:** Check main.py or logs
3. ✅ **Error Messages:** Copy exact error text
4. ✅ **Steps to Reproduce:** Detailed reproduction steps
5. ✅ **Log Files:** Recent application logs

### Where to Get Help

#### 1. GitHub Issues
- **Best for:** Bug reports, feature requests
- **Location:** [Issues](../../issues)
- **Template:** Use provided issue templates

#### 2. GitHub Discussions
- **Best for:** General questions, troubleshooting
- **Location:** [Discussions](../../discussions)
- **Format:** Free-form discussion

#### 3. Documentation
- **README.md:** General usage and setup
- **USER_GUIDE.md:** Detailed user instructions
- **DEVELOPMENT.md:** Development setup
- **TROUBLESHOOTING.md:** This guide

#### 4. Community Support
- **Star Conflict Forums:** Game-specific issues
- **Reddit:** r/starconflict or r/learnpython
- **Discord:** Python or gaming communities

### Creating Effective Support Requests

#### Good Issue Report
```markdown
## Issue: Application crashes on startup

### Environment
- OS: Windows 10 Pro 22H2
- Python: 3.9.7
- App Version: 1.1.3
- RAM: 16GB

### Steps to Reproduce
1. Download latest release
2. Extract to C:\Program Files\
3. Run SC_Chat_Translator.exe
4. Application shows splash screen then crashes

### Expected Behavior
Application should start and show main window

### Actual Behavior
Application crashes with no error message

### Additional Information
- Tried running as administrator: Same result
- Antivirus disabled: Same result
- Windows Event Viewer shows no relevant errors
- Log file location: No log file created
```

#### What to Include
- ✅ **Clear Title:** Summarize the problem
- ✅ **Environment Details:** OS, versions, hardware
- ✅ **Step-by-Step Reproduction:** Exact steps to reproduce
- ✅ **Expected vs Actual:** What should happen vs what does
- ✅ **Screenshots/Logs:** Visual evidence and error logs
- ✅ **Attempts Made:** What you've already tried

### Response Times

- **Bug Fixes:** 1-7 days (depending on complexity)
- **Feature Requests:** 1-4 weeks (depending on scope)
- **General Questions:** 1-3 days
- **Documentation:** 1-2 days

---

<div align="center">

**🎯 Still Having Issues? We're Here to Help! 🎯**

*Most problems have simple solutions. Let's find yours!*

[📧 Contact Support](mailto:borutaproject@gmail.com) • [🐛 Report Issues](../../issues) • [💬 Start Discussion](../../discussions)

</div>
