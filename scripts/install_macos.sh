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
    <string>1.0.16</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.16</string>
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
