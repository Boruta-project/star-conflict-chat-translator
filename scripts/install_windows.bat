@echo off
REM Windows installation script for Star Conflict Chat Translator
REM This script sets up the development environment on Windows

echo ========================================
echo Star Conflict Chat Translator Installer
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Checking version...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo WARNING: Failed to upgrade pip, continuing...
)

REM Install requirements
echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

REM Install development dependencies if requirements-dev.txt exists
if exist requirements-dev.txt (
    echo.
    echo Installing development dependencies...
    pip install -r requirements-dev.txt
    if errorlevel 1 (
        echo WARNING: Failed to install dev requirements, continuing...
    )
)

REM Create desktop shortcut (optional)
echo.
echo Creating desktop shortcut...
set SCRIPT_DIR=%~dp0
set SHORTCUT_NAME=SC Chat Translator.lnk
set TARGET=%SCRIPT_DIR%venv\Scripts\python.exe
set ARGUMENTS="%SCRIPT_DIR%main.py"
set ICON=%SCRIPT_DIR%assets\logo.ico
set DESCRIPTION=Star Conflict Chat Translator

powershell "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%USERPROFILE%\Desktop\%SHORTCUT_NAME%'); $s.TargetPath='%TARGET%'; $s.Arguments='%ARGUMENTS%'; $s.IconLocation='%ICON%'; $s.Description='%DESCRIPTION%'; $s.Save()"

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo To run the application:
echo 1. Activate the virtual environment: venv\Scripts\activate.bat
echo 2. Run the application: python main.py
echo.
echo Or use the desktop shortcut that was created.
echo.
echo For development:
echo - Run tests: python -m pytest tests/
echo - Build executable: python scripts\build.py windows
echo.
pause
