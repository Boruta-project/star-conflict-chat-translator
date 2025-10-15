#!/usr/bin/env python3
"""
Enhanced build automation script for Star Conflict Chat Translator.
Features:
- Virtual environment isolation
- Cross-platform executable generation
- Automated testing
- Version management
- GitHub release preparation
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import json
from datetime import datetime
import argparse
import shutil

class BuildAutomation:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.venv_dir = self.project_root / ".venv"

        # Build configuration
        self.config = {
            "app_name": "SC Chat Translator",
            "app_version": "1.1.3",
            "author": "Hystrix",

            "platforms": {
                "windows": {
                    "spec_file": "build_windows.spec",
                    "icon": "assets/logo.ico",
                    "output_name": "SC_Chat_Translator_v{version}_Windows.exe",
                    "pyinstaller_args": ["--onefile", "--windowed"]
                },
                "linux": {
                    "spec_file": "build_linux.spec",
                    "icon": "assets/logo.ico",
                    "output_name": "SC_Chat_Translator_v{version}_Linux",
                    "pyinstaller_args": ["--onefile"]
                },
                "macos": {
                    "spec_file": "build_macos.spec",
                    "icon": "assets/logo.icns",
                    "output_name": "SC_Chat_Translator_v{version}_macOS.app",
                    "pyinstaller_args": ["--windowed", "--onedir"]
                }
            }
        }

    def setup_venv(self):
        """Create and setup virtual environment"""
        print("Setting up virtual environment...")

        if not self.venv_dir.exists():
            print(f"Creating virtual environment at {self.venv_dir}")
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_dir)], check=True)

        # Get pip path for the virtual environment
        if platform.system() == "Windows":
            pip_path = self.venv_dir / "Scripts" / "pip"
            python_path = self.venv_dir / "Scripts" / "python"
        else:
            pip_path = self.venv_dir / "bin" / "pip"
            python_path = self.venv_dir / "bin" / "python"

        # Upgrade pip
        print("Upgrading pip...")
        subprocess.run([str(python_path), "-m", "pip", "install", "--upgrade", "pip"], check=True)

        # Install build dependencies
        requirements_build = self.project_root / "requirements-build.txt"
        if requirements_build.exists():
            print("Installing build dependencies...")
            subprocess.run([str(pip_path), "install", "-r", str(requirements_build)], check=True)

        # Install runtime dependencies
        requirements = self.project_root / "requirements.txt"
        if requirements.exists():
            print("Installing runtime dependencies...")
            subprocess.run([str(pip_path), "install", "-r", str(requirements)], check=True)

        return str(python_path), str(pip_path)

    def run_tests(self, python_path):
        """Run test suite in virtual environment"""
        print("Running tests...")
        try:
            subprocess.run([python_path, "-m", "pytest", "tests/", "-v", "--tb=short"], check=True)
            print("Tests passed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Tests failed with exit code {e.returncode}")
            return False

    def build_executable(self, target_platform, python_path):
        """Build executable for specific platform"""
        print(f"Building executable for {target_platform}...")

        if target_platform not in self.config["platforms"]:
            raise ValueError(f"Unsupported platform: {target_platform}")

        platform_config = self.config["platforms"][target_platform]

        # Ensure dist directory exists
        self.dist_dir.mkdir(exist_ok=True)

        # Clean previous builds
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)
        self.dist_dir.mkdir()

        # Build with PyInstaller
        spec_file = self.build_dir / platform_config["spec_file"]
        if spec_file.exists():
            # Use spec file if it exists
            cmd = [python_path, "-m", "PyInstaller", str(spec_file)]
        else:
            # Fallback to command line
            cmd = [python_path, "-m", "PyInstaller"]
            cmd.extend(platform_config["pyinstaller_args"])
            if platform_config["icon"]:
                icon_path = self.project_root / platform_config["icon"]
                if icon_path.exists():
                    cmd.extend(["--icon", str(icon_path)])
            cmd.extend(["--add-data", f"{self.project_root / 'assets'}{os.pathsep}assets"])
            cmd.extend(["--add-data", f"{self.project_root / 'game_dictionary.json'}{os.pathsep}."])
            cmd.append(str(self.project_root / "main.py"))

        print(f"Running: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, cwd=self.project_root, check=True)
            print(f"{target_platform} executable built successfully")

            # Rename output if needed
            output_name = platform_config["output_name"].format(version=self.config["app_version"])
            expected_output = self.dist_dir / output_name

            # Find the actual output file
            if platform.system() == "Windows":
                actual_output = self.dist_dir / "main.exe"
            else:
                actual_output = self.dist_dir / "main"

            if actual_output.exists() and not expected_output.exists():
                actual_output.rename(expected_output)
                print(f"Renamed to {expected_output.name}")

            return True
        except subprocess.CalledProcessError as e:
            print(f"Build failed for {target_platform} with exit code {e.returncode}")
            return False

    def create_release_archive(self):
        """Create release-ready source archive"""
        print("Creating release archive...")

        import zipfile

        version = self.config["app_version"]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"sc_translator_{version}_source_{timestamp}.zip"

        # Define files and directories to include
        include_patterns = [
            '*.py', '*.md', '*.txt', '*.toml', '*.json', '*.in', '*.ico', '*.png',
            'assets/*', 'docs/*', 'scripts/*', 'src/*', 'tests/*',
            '.gitignore', 'LICENSE', 'MANIFEST.in', 'pyproject.toml', 'CHANGELOG.md', 'CONTRIBUTING.md',
            'main.py', 'game_dictionary.json', 'requirements.txt', 'requirements-dev.txt'
        ]

        exclude_dirs = {'__pycache__', '.pytest_cache', 'build', 'dist', '.venv', '_dev_files', '.git'}

        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk('.'):
                # Remove excluded directories from traversal
                dirs[:] = [d for d in dirs if d not in exclude_dirs]

                # Skip if current directory is excluded
                current_dir = os.path.basename(root)
                if current_dir in exclude_dirs:
                    continue

                for file in files:
                    # Skip system files and build artifacts
                    if (file.endswith(('.pyc', '.pyo', '.log', '.spec')) or
                        file.startswith('.') or
                        'Analysis-' in file or 'COLLECT-' in file or 'EXE-' in file or
                        'PKG-' in file or 'PYZ-' in file or 'xref-' in file or
                        'warn-' in file):
                        continue

                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, '.')

                    # Only include files that match our patterns or are in included directories
                    should_include = False
                    for pattern in include_patterns:
                        if pattern.endswith('/*'):
                            # Directory pattern
                            dir_name = pattern[:-2]
                            if arc_name.startswith(dir_name + '/'):
                                should_include = True
                                break
                        elif pattern in arc_name or arc_name.endswith(pattern):
                            should_include = True
                            break

                    if should_include:
                        zipf.write(file_path, arc_name)

        print(f"Release archive created: {zip_name}")
        return zip_name

    def main(self):
        parser = argparse.ArgumentParser(description="Build automation for Star Conflict Chat Translator")
        parser.add_argument("--target", choices=["windows", "linux", "macos", "all"], default="all",
                          help="Target platform(s) to build for")
        parser.add_argument("--test", action="store_true", help="Run tests before building")
        parser.add_argument("--release", action="store_true", help="Create release archive")
        parser.add_argument("--clean", action="store_true", help="Clean build artifacts")

        args = parser.parse_args()

        # Clean if requested
        if args.clean:
            print("Cleaning build artifacts...")
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
            if self.dist_dir.exists():
                shutil.rmtree(self.dist_dir)
            print("Cleaned build artifacts")
            return

        # Setup environment
        try:
            python_path, pip_path = self.setup_venv()
            print("Virtual environment ready")
        except Exception as e:
            print(f"Failed to setup virtual environment: {e}")
            return

        # Run tests if requested
        if args.test:
            if not self.run_tests(python_path):
                print("Tests failed, aborting build")
                return

        # Build for target platform(s)
        success = True
        if args.target == "all":
            current_platform = platform.system().lower()
            if current_platform == "windows":
                targets = ["windows"]
            elif current_platform == "linux":
                targets = ["linux"]
            elif current_platform == "darwin":
                targets = ["macos"]
            else:
                print(f"Unsupported platform for build: {current_platform}")
                return

            for target in targets:
                if not self.build_executable(target, python_path):
                    success = False
        else:
            if not self.build_executable(args.target, python_path):
                success = False

        # Create release archive if requested and build was successful
        if args.release and success:
            self.create_release_archive()

        if success:
            print("Build automation completed successfully")
        else:
            print("Build automation failed")
            sys.exit(1)

if __name__ == "__main__":
    BuildAutomation().main()
