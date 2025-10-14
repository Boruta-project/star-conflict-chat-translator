#!/usr/bin/env python3
"""
Build script for creating executable distributions of Star Conflict Chat Translator.
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return True if successful."""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True,
                              capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return False

def build_windows():
    """Build Windows executable using PyInstaller."""
    print("Building Windows executable...")

    # Ensure PyInstaller is installed
    if not run_command("pip install pyinstaller"):
        return False

    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")

    # Build the executable
    cmd = 'pyinstaller --windowed --icon=assets/logo.ico --add-data "assets;assets" main.py'
    if run_command(cmd):
        print("Windows executable built successfully in dist/ folder")
        return True
    return False

def build_linux():
    """Build Linux executable using PyInstaller."""
    print("Building Linux executable...")

    if not run_command("pip install pyinstaller"):
        return False

    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")

    # Build the executable
    cmd = 'pyinstaller --windowed --icon=assets/logo.ico --add-data "assets:assets" main.py'
    if run_command(cmd):
        print("Linux executable built successfully in dist/ folder")
        return True
    return False

def build_macos():
    """Build macOS executable using PyInstaller."""
    print("Building macOS executable...")

    if not run_command("pip install pyinstaller"):
        return False

    # Clean previous builds
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")

    # Build the executable
    cmd = 'pyinstaller --windowed --icon=assets/logo.ico --add-data "assets:assets" main.py'
    if run_command(cmd):
        print("macOS executable built successfully in dist/ folder")
        return True
    return False

def create_zip_archive():
    """Create a ZIP archive of the source code."""
    print("Creating source code archive...")

    import zipfile
    from datetime import datetime

    version = "1.1.2"  # Should be read from main.py
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"sc_translator_{version}_{timestamp}.zip"

    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add source files
        for root, dirs, files in os.walk('.'):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'build', 'dist', '.venv']]

            for file in files:
                # Skip certain file types
                if file.endswith(('.pyc', '.pyo', '.log')) or file.startswith('.'):
                    continue

                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, '.')
                zipf.write(file_path, arc_name)

    print(f"Source archive created: {zip_name}")
    return True

def main():
    """Main build function."""
    if len(sys.argv) < 2:
        print("Usage: python build.py [windows|linux|macos|zip|all]")
        sys.exit(1)

    platform = sys.argv[1].lower()

    if platform == "windows":
        success = build_windows()
    elif platform == "linux":
        success = build_linux()
    elif platform == "macos":
        success = build_macos()
    elif platform == "zip":
        success = create_zip_archive()
    elif platform == "all":
        # Build for current platform and create zip
        if os.name == 'nt':  # Windows
            success = build_windows()
        elif sys.platform.startswith('linux'):
            success = build_linux()
        elif sys.platform == 'darwin':
            success = build_macos()
        else:
            print("Unsupported platform for 'all' build")
            success = False

        if success:
            create_zip_archive()
    else:
        print(f"Unknown platform: {platform}")
        print("Supported platforms: windows, linux, macos, zip, all")
        success = False

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
