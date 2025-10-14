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
echo "Happy translating! 🌍"
echo
