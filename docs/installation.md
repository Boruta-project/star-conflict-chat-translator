# Installation Scripts

<div align="center">
  <h1>📦 Automated Installation Scripts</h1>
  <p><em>One-click setup for Windows, Linux, and macOS</em></p>
</div>

## 📋 Overview

This document contains automated installation scripts for setting up the Star Conflict Chat Translator development environment on different platforms. These scripts handle:

- ✅ Virtual environment creation
- ✅ Dependency installation
- ✅ Basic configuration
- ✅ First-run setup
- ✅ Desktop shortcuts (where supported)

## 🚀 Quick Start

### For Windows Users
1. Download `install_windows.bat`
2. Right-click → Run as administrator
3. Follow the on-screen prompts

### For Linux Users
```bash
chmod +x install_linux.sh
./install_linux.sh
```

### For macOS Users
```bash
chmod +x install_macos.sh
./install_macos.sh
```

---

## Windows Installation Script

### File: `install_windows.bat`

```batch
@echo off
REM Star Conflict Chat Translator - Windows Installation Script
REM This script sets up the development environment on Windows

echo ===========================================
echo Star Conflict Chat Translator Setup
echo Windows Installation Script
echo ===========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found. Checking version...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Git is not installed
    echo Git is recommended for version control
    echo Download from: https://git-scm.com/downloads
    echo.
)

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo WARNING: Failed to upgrade pip, continuing...
)

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

REM Create desktop shortcut
echo.
echo Creating desktop shortcut...
set SHORTCUT_PATH=%USERPROFILE%\Desktop\SC Chat Translator.lnk
set TARGET_PATH=%CD%\venv\Scripts\python.exe
set ARGUMENTS=%CD%\main.py
set ICON_PATH=%CD%\assets\logo.ico

echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%SHORTCUT_PATH%" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%TARGET_PATH%" >> CreateShortcut.vbs
echo oLink.Arguments = "%ARGUMENTS%" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%CD%" >> CreateShortcut.vbs
echo oLink.IconLocation = "%ICON_PATH%" >> CreateShortcut.vbs
echo oLink.Description = "Star Conflict Chat Translator" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

cscript CreateShortcut.vbs >nul 2>&1
del CreateShortcut.vbs >nul 2>&1

if exist "%SHORTCUT_PATH%" (
    echo Desktop shortcut created successfully
) else (
    echo Note: Desktop shortcut creation failed (this is optional)
)

REM Test installation
echo.
echo Testing installation...
python -c "import tkinter, customtkinter; print('GUI libraries: OK')"
if %errorlevel% neq 0 (
    echo WARNING: GUI libraries test failed
)

python -c "from googletrans import Translator; print('Translation library: OK')"
if %errorlevel% neq 0 (
    echo WARNING: Translation library test failed
)

echo.
echo ===========================================
echo Installation completed successfully!
echo ===========================================
echo.
echo To run the application:
echo 1. Double-click the desktop shortcut
echo 2. Or run: venv\Scripts\activate.bat && python main.py
echo.
echo For development:
echo 1. Activate environment: venv\Scripts\activate.bat
echo 2. Run application: python main.py
echo 3. Run tests: python -m pytest
echo.
echo Happy translating!
echo.
pause
```

### How to Use the Windows Script

1. **Save** the script as `install_windows.bat`
2. **Right-click** the file → **Run as administrator**
3. **Follow** the on-screen prompts
4. **Wait** for installation to complete
5. **Use** the desktop shortcut to launch the app

---

## Linux Installation Script

### File: `install_linux.sh`

```bash
#!/bin/bash

# Star Conflict Chat Translator - Linux Installation Script
# This script sets up the development environment on Linux

set -e  # Exit on any error

echo "==========================================="
echo "Star Conflict Chat Translator Setup"
echo "Linux Installation Script"
echo "==========================================="
echo

# Function to print colored output
print_status() {
    echo -e "\033[1;32m$1\033[0m"
}

print_warning() {
    echo -e "\033[1;33mWARNING: $1\033[0m"
}

print_error() {
    echo -e "\033[1;31mERROR: $1\033[0m"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    echo "Please install Python 3.8+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    exit 1
fi

print_status "Python 3 found. Checking version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Check Python version
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MAJOR" -eq 3 -a "$PYTHON_MINOR" -lt 8 ]; then
    print_error "Python 3.8+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_warning "Git is not installed"
    echo "Git is recommended for version control"
    echo "Install with: sudo apt install git  (Ubuntu/Debian)"
    echo "Or: sudo yum install git  (CentOS/RHEL)"
    echo
fi

# Create virtual environment
print_status "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    print_error "Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip
print_status "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    print_error "Failed to install dependencies"
    echo "Please check your internet connection and try again"
    exit 1
fi

# Create desktop shortcut (if desktop environment supports it)
print_status "Creating desktop shortcut..."
DESKTOP_FILE="$HOME/Desktop/sc-chat-translator.desktop"

cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=SC Chat Translator
Comment=Star Conflict Chat Translator
Exec=$PWD/venv/bin/python $PWD/main.py
Icon=$PWD/assets/logo.ico
Path=$PWD
Terminal=false
StartupNotify=false
Categories=Utility;Game;
EOF

chmod +x "$DESKTOP_FILE"

if [ -f "$DESKTOP_FILE" ]; then
    print_status "Desktop shortcut created successfully"
else
    print_warning "Desktop shortcut creation failed (this is optional)"
fi

# Test installation
print_status "Testing installation..."

# Test GUI libraries
python -c "import tkinter, customtkinter; print('GUI libraries: OK')" 2>/dev/null
if [ $? -ne 0 ]; then
    print_warning "GUI libraries test failed"
    echo "This might be due to missing display server (common in headless environments)"
fi

# Test translation library
python -c "from googletrans import Translator; print('Translation library: OK')" 2>/dev/null
if [ $? -ne 0 ]; then
    print_warning "Translation library test failed"
    echo "Check your internet connection"
fi

echo
echo "==========================================="
print_status "Installation completed successfully!"
echo "==========================================="
echo
echo "To run the application:"
echo "1. Double-click the desktop shortcut"
echo "2. Or run: source venv/bin/activate && python main.py"
echo
echo "For development:"
echo "1. Activate environment: source venv/bin/activate"
echo "2. Run application: python main.py"
echo "3. Run tests: python -m pytest"
echo
echo "Happy translating!"
echo
```

### How to Use the Linux Script

1. **Save** the script as `install_linux.sh`
2. **Make executable**: `chmod +x install_linux.sh`
3. **Run**: `./install_linux.sh`
4. **Follow** the prompts
5. **Use** the desktop shortcut or terminal commands

---

## macOS Installation Script

### File: `install_macos.sh`

```bash
#!/bin/bash

# Star Conflict Chat Translator - macOS Installation Script
# This script sets up the development environment on macOS

set -e  # Exit on any error

echo "==========================================="
echo "Star Conflict Chat Translator Setup"
echo "macOS Installation Script"
echo "==========================================="
echo

# Function to print colored output
print_status() {
    echo -e "\033[1;32m$1\033[0m"
}

print_warning() {
    echo -e "\033[1;33mWARNING: $1\033[0m"
}

print_error() {
    echo -e "\033[1;31mERROR: $1\033[0m"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    echo "Please install Python 3.8+ from https://python.org"
    echo "Or using Homebrew: brew install python"
    exit 1
fi

print_status "Python 3 found. Checking version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Check Python version
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MAJOR" -eq 3 -a "$PYTHON_MINOR" -lt 8 ]; then
    print_error "Python 3.8+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_warning "Git is not installed"
    echo "Git is recommended for version control"
    echo "Install with: brew install git  (if using Homebrew)"
    echo "Or download from: https://git-scm.com/download/mac"
    echo
fi

# Check if Xcode command line tools are installed
if ! command -v xcode-select &> /dev/null; then
    print_warning "Xcode Command Line Tools not found"
    echo "Installing Xcode Command Line Tools (this may take a few minutes)..."
    xcode-select --install
    echo "Please complete the Xcode installation and run this script again"
    exit 1
fi

# Create virtual environment
print_status "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    print_error "Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip
print_status "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    print_error "Failed to install dependencies"
    echo "Please check your internet connection and try again"
    exit 1
fi

# Create Applications shortcut
print_status "Creating Applications shortcut..."
APP_NAME="SC Chat Translator"
APP_PATH="/Applications/$APP_NAME.app"

# Create app bundle structure
mkdir -p "$APP_PATH/Contents/MacOS"
mkdir -p "$APP_PATH/Contents/Resources"

# Create Info.plist
cat > "$APP_PATH/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>com.hystrix.scchattranslator</string>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundleVersion</key>
    <string>1.1.3</string>
    <key>CFBundleShortVersionString</key>
    <string>1.1.3</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>CFBundleIconFile</key>
    <string>logo.icns</string>
</dict>
</plist>
EOF

# Create executable script
cat > "$APP_PATH/Contents/MacOS/$APP_NAME" << EOF
#!/bin/bash
cd "$PWD"
source venv/bin/activate
python main.py
EOF

chmod +x "$APP_PATH/Contents/MacOS/$APP_NAME"

# Copy icon if available
if [ -f "assets/logo.ico" ]; then
    cp "assets/logo.ico" "$APP_PATH/Contents/Resources/logo.icns" 2>/dev/null || true
fi

if [ -d "$APP_PATH" ]; then
    print_status "Applications shortcut created successfully"
    echo "You can now find '$APP_NAME' in your Applications folder"
else
    print_warning "Applications shortcut creation failed (this is optional)"
fi

# Test installation
print_status "Testing installation..."

# Test GUI libraries (may fail in headless environments)
python -c "import tkinter, customtkinter; print('GUI libraries: OK')" 2>/dev/null
if [ $? -ne 0 ]; then
    print_warning "GUI libraries test failed"
    echo "This is normal if running in a headless environment"
fi

# Test translation library
python -c "from googletrans import Translator; print('Translation library: OK')" 2>/dev/null
if [ $? -ne 0 ]; then
    print_warning "Translation library test failed"
    echo "Check your internet connection"
fi

echo
echo "==========================================="
print_status "Installation completed successfully!"
echo "==========================================="
echo
echo "To run the application:"
echo "1. Open Applications folder and double-click 'SC Chat Translator'"
echo "2. Or run: source venv/bin/activate && python main.py"
echo
echo "For development:"
echo "1. Activate environment: source venv/bin/activate"
echo "2. Run application: python main.py"
echo "3. Run tests: python -m pytest"
echo
echo "Happy translating!"
echo
```

### How to Use the macOS Script

1. **Save** the script as `install_macos.sh`
2. **Make executable**: `chmod +x install_macos.sh`
3. **Run**: `./install_macos.sh`
4. **Follow** the prompts (may need to install Xcode tools)
5. **Find** the app in your Applications folder

---

## 📋 Script Features

### All Scripts Include:

- ✅ **Python version checking** (requires 3.8+)
- ✅ **Virtual environment creation** and activation
- ✅ **Dependency installation** from requirements.txt
- ✅ **Desktop/Application shortcuts** creation
- ✅ **Installation testing** and verification
- ✅ **Error handling** and user-friendly messages
- ✅ **Cross-platform compatibility**

### Platform-Specific Features:

#### Windows
- Uses `venv\Scripts\activate.bat`
- Creates Windows `.lnk` shortcut on desktop
- Handles Windows-specific path formats

#### Linux
- Uses `venv/bin/activate`
- Creates `.desktop` file for application menus
- Supports various Linux distributions

#### macOS
- Uses `venv/bin/activate`
- Creates proper `.app` bundle in Applications
- Handles macOS-specific requirements (Xcode tools)

---

## 🆘 Troubleshooting Installation

### Common Issues

#### "Python is not installed"
**Solution:**
- Windows: Download from python.org, check "Add to PATH"
- Linux: `sudo apt install python3 python3-pip python3-venv`
- macOS: `brew install python` or download from python.org

#### "Virtual environment creation failed"
**Solution:**
- Ensure you have write permissions in the current directory
- Try running as administrator/sudo
- Check available disk space

#### "Dependencies installation failed"
**Solutions:**
- Check internet connection
- Try `pip install --upgrade pip` first
- Install system dependencies:
  - Ubuntu: `sudo apt install python3-dev build-essential`
  - macOS: Install Xcode Command Line Tools

#### "Desktop shortcut creation failed"
**Solution:**
- This is optional and doesn't affect functionality
- You can still run the application from command line
- Check write permissions to Desktop folder

### Getting Help

If you encounter issues:

1. **Check the error messages** carefully
2. **Verify your Python version**: `python --version`
3. **Test basic functionality**: `python -c "import tkinter"`
4. **Check internet connection** for dependency downloads
5. **Create an issue** on GitHub with full error output

---

<div align="center">

**🎉 Happy Installing! 🎉**

*Need help? Check the [Issues](../../issues) page or create a new issue.*

</div>
