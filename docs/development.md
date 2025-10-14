# Star Conflict Chat Translator - Development Guide

<div align="center">
  <h1>🔧 Development Setup & Contribution Guide</h1>
  <p><em>Everything you need to develop, test, and contribute to the project</em></p>
</div>

## 📖 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [💻 Development Environment Setup](#-development-environment-setup)
- [📦 Dependencies & Installation](#-dependencies--installation)
- [🏗️ Project Structure](#️-project-structure)
- [🧪 Testing](#-testing)
- [🔧 Development Workflow](#-development-workflow)
- [📋 Code Standards](#-code-standards)
- [🔍 Debugging](#-debugging)
- [📦 Building & Distribution](#-building--distribution)
- [🤝 Contributing Guidelines](#-contributing-guidelines)
- [📚 API Documentation](#-api-documentation)
- [🔧 Advanced Configuration](#-advanced-configuration)

## 🚀 Quick Start

### For Experienced Developers

```bash
# Clone and setup in one command
git clone https://github.com/boruta-project/star-conflict-chat-translator.git
cd star-conflict-chat-translator
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
python main.py
```

### Prerequisites Checklist

- ✅ **Python 3.8+** installed
- ✅ **Git** for version control
- ✅ **Code Editor** (VS Code, PyCharm, etc.)
- ✅ **Internet connection** for dependencies and Google Translate
- ✅ **Star Conflict** game installed (for testing)

## 💻 Development Environment Setup

### 1. Clone the Repository

```bash
# HTTPS (recommended for most users)
git clone https://github.com/boruta-project/star-conflict-chat-translator.git

# SSH (if you have SSH keys set up)
git clone git@github.com:boruta-project/star-conflict-chat-translator.git

# Change to project directory
cd star-conflict-chat-translator
```

### 2. Set Up Python Virtual Environment

#### Windows
```batch
# Create virtual environment
python -m venv venv

# Activate environment
venv\Scripts\activate

# Verify activation (should show (venv) in prompt)
python --version
pip --version
```

#### Linux/macOS
```bash
# Create virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate

# Verify activation (should show (venv) in prompt)
python --version
pip --version
```

#### Using conda (Alternative)
```bash
# Create conda environment
conda create -n sc-translator python=3.9
conda activate sc-translator

# Install pip in conda environment
conda install pip
```

### 3. Install Dependencies

#### Basic Dependencies
```bash
# Install core requirements
pip install -r requirements.txt
```

#### Development Dependencies
```bash
# Install development tools
pip install -r requirements-dev.txt
```

#### Optional Dependencies
```bash
# For building executables
pip install pyinstaller

# For advanced testing
pip install pytest-cov
pip install tox
```

### 4. Verify Installation

```bash
# Test basic import
python -c "import tkinter, customtkinter, googletrans; print('All imports successful!')"

# Test application startup
python main.py --help
```

### 5. Configure Development Tools

#### VS Code Setup
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/Scripts/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
}
```

#### PyCharm Setup
1. **Open** project in PyCharm
2. **Configure** interpreter: File → Settings → Project → Python Interpreter
3. **Add** virtual environment: `venv/Scripts/python.exe` (Windows) or `venv/bin/python` (Linux/macOS)
4. **Enable** code style: File → Settings → Editor → Code Style → Python

## 📦 Dependencies & Installation

### Core Dependencies

```txt
# requirements.txt
customtkinter>=5.2.0        # Modern GUI framework
Pillow>=9.0.0              # Image processing for icons
googletrans>=4.0.0rc1      # Google Translate API wrapper
pyperclip>=1.8.0           # Clipboard operations
```

### Development Dependencies

```txt
# requirements-dev.txt
pytest>=7.0.0              # Testing framework
black>=22.0.0              # Code formatting
flake8>=4.0.0              # Linting
mypy>=0.900                # Type checking
pre-commit>=2.0.0          # Git hooks
```

### Installing from Different Sources

#### From PyPI (Recommended)
```bash
pip install customtkinter googletrans pyperclip Pillow
```

#### From GitHub (Latest Development)
```bash
pip install git+https://github.com/TomSchimansky/CustomTkinter.git
pip install git+https://github.com/ssut/py-googletrans.git
```

#### Editable Installation
```bash
# Install in development mode
pip install -e .
```

## 🏗️ Project Structure

```
star-conflict-chat-translator/
├── main.py                          # Main application entry point
├── game_dictionary.json             # Community-maintained game terms dictionary
├── requirements.txt                 # Core dependencies
├── requirements-dev.txt            # Development dependencies
├── pyproject.toml                  # Modern Python project configuration
├── MANIFEST.in                     # Package manifest for distribution
├── .gitignore                      # Git ignore rules
├── .github/                        # GitHub configuration and workflows
├── assets/                         # Static assets
│   ├── logo.ico                    # Application icon
│   └── help_blue.png               # Help icons
├── docs/                           # Documentation
│   ├── game-dictionary.md          # Dictionary contribution guide
│   ├── user-guide.md               # Complete user manual
│   ├── installation.md             # Installation instructions
│   ├── troubleshooting.md          # Troubleshooting guide
│   └── development.md              # Development documentation
├── scripts/                        # Build and installation scripts
│   ├── build.py                    # Build automation script
│   ├── install_windows.bat         # Windows installer
│   ├── install_linux.sh            # Linux installer
│   └── install_macos.sh            # macOS installer
├── src/                            # Source code
│   └── sc_translator/              # Main package
│       ├── __init__.py
│       └── main.py                 # Main application module
├── tests/                          # Unit tests
│   ├── __init__.py
│   ├── test_main.py                # Main module tests
│   └── test_translator.py          # Translation functionality tests
├── CHANGELOG.md                    # Version history
├── CONTRIBUTING.md                 # Contribution guidelines
├── LICENSE                         # MIT license
└── README.md                       # This file
```

### Key Files Explanation

#### Core Application Files
- **`main.py`**: Main application logic, GUI, and business rules
- **`requirements.txt`**: Runtime dependencies
- **`pyproject.toml`**: Modern Python project configuration

#### Configuration Files
- **`.gitignore`**: Excludes build artifacts, secrets, and local files
- **`.pre-commit-config.yaml`**: Automated code quality checks
- **`setup.py`**: Legacy package configuration

#### Development Files
- **`requirements-dev.txt`**: Development and testing tools
- **`tests/`**: Unit and integration tests
- **`_dev_files/`**: Development utilities and backups

## 🧪 Testing

### Running Tests

#### Basic Test Suite
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_translation.py

# Run specific test
pytest tests/test_main.py::test_language_selection
```

#### Test Coverage
```bash
# Generate coverage report
pytest --cov=src --cov-report=html

# View coverage in browser
open htmlcov/index.html
```

#### Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Writing Tests

#### Test Structure
```python
# tests/test_translation.py
import pytest
from main import compare_versions, Translator

class TestTranslation:
    def test_compare_versions_equal(self):
        assert compare_versions("1.0.0", "1.0.0") == 0

    def test_compare_versions_newer(self):
        assert compare_versions("1.1.0", "1.0.0") == 1

    def test_compare_versions_older(self):
        assert compare_versions("1.0.0", "1.1.0") == -1

    @pytest.mark.integration
    def test_google_translate_connection(self):
        translator = Translator()
        result = translator.translate("Hello", dest="es")
        assert result.text.lower() == "hola"
```

#### Test Fixtures
```python
# tests/conftest.py
import pytest
from pathlib import Path
import tempfile

@pytest.fixture
def temp_settings_file():
    """Create a temporary settings file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{"test": true}')
        temp_path = f.name

    yield temp_path
    Path(temp_path).unlink()
```

### Test Data Management

#### Mock Data for Testing
```python
# Sample remote JSON for testing
MOCK_REMOTE_DATA = {
    "id": "0001",
    "welcome_message": "Welcome to test",
    "version": "1.0.0",
    "whats_new": {"changes": ["Test change"]},
    "download_url": "https://drive.google.com/drive/folders/1O59M6QIr3anfxi8K0UgDf6ao44KYIKrG?usp=sharing",
    "notes": "Test notes"
}
```

## 🔧 Development Workflow

### 1. Create Feature Branch

```bash
# Create and switch to feature branch
git checkout -b feature/new-translation-language

# Push branch to remote
git push -u origin feature/new-translation-language
```

### 2. Development Process

```bash
# Make changes to code
# Write tests for new functionality
# Run tests locally
pytest

# Format code
black main.py

# Check for linting issues
flake8 main.py

# Commit changes
git add .
git commit -m "Add support for new translation language"
```

### 3. Code Review Process

```bash
# Ensure branch is up to date
git fetch origin
git rebase origin/main

# Push final changes
git push

# Create Pull Request on GitHub
# Wait for review and approval
```

### 4. Merge Process

```bash
# After PR approval, merge to main
git checkout main
git pull origin main
git branch -d feature/new-translation-language
```

## 📋 Code Standards

### Python Style Guide

#### PEP 8 Compliance
```python
# Good: Proper spacing and naming
def calculate_translation_score(text, language):
    score = len(text) * get_language_complexity(language)
    return score

# Bad: Poor spacing and naming
def calc_trans_score(txt,lang):
    score=len(txt)*get_lang_complexity(lang)
    return score
```

#### Import Organization
```python
# Standard library imports
import os
import sys
from pathlib import Path

# Third-party imports
import customtkinter as ctk
from googletrans import Translator
from PIL import Image

# Local imports
from .utils import helper_function
from .constants import APP_VERSION
```

### Documentation Standards

#### Docstring Format
```python
def translate_message(message, target_lang, source_lang=None):
    """
    Translate a chat message to the target language.

    Args:
        message (str): The message to translate
        target_lang (str): Target language code (e.g., 'en', 'es')
        source_lang (str, optional): Source language code. Auto-detected if None

    Returns:
        str: Translated message

    Raises:
        TranslationError: If translation fails
        NetworkError: If network connection fails

    Example:
        >>> translate_message("Hello world", "es")
        'Hola mundo'
    """
    pass
```

#### Code Comments
```python
# Good: Explains why, not what
def process_chat_line(line):
    # Skip system messages as they don't need translation
    if is_system_message(line):
        return None

    # Extract and validate message components
    username, message = parse_chat_line(line)

    # Bad: Just repeats what the code does
    # Check if line is system message
    # if is_system_message(line):
    #     return None
```

### Naming Conventions

#### Variables and Functions
```python
# Good
def translate_chat_message(message, target_language):
    translated_text = perform_translation(message, target_language)
    return translated_text

# Bad
def trans_msg(msg, tgt_lang):
    trans_txt = do_trans(msg, tgt_lang)
    return trans_txt
```

#### Classes and Constants
```python
# Classes: PascalCase
class ChatTranslator:
    pass

class RemoteUpdateManager:
    pass

# Constants: UPPER_CASE
MAX_TRANSLATION_LENGTH = 5000
DEFAULT_LANGUAGE = "en"
GOOGLE_TRANSLATE_URL = "https://translate.googleapis.com"
```

### Error Handling

#### Proper Exception Handling
```python
# Good: Specific exception types
try:
    result = translator.translate(text, dest=target_lang)
    return result.text
except googletrans.exceptions.TranslationError as e:
    logger.error(f"Translation failed: {e}")
    return f"[Translation error: {e}]"
except requests.exceptions.RequestException as e:
    logger.error(f"Network error: {e}")
    return "[Network error]"

# Bad: Bare except
try:
    # some code
except:
    pass  # Never do this!
```

## 🔍 Debugging

### Debug Mode

#### Running in Debug Mode
```bash
# Enable debug logging
python main.py --debug

# Or set environment variable
DEBUG=1 python main.py
```

#### Debug Configuration
```python
# In main.py
import logging

if __name__ == "__main__":
    if "--debug" in sys.argv or os.getenv("DEBUG"):
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
```

### Common Debugging Techniques

#### Logging Best Practices
```python
import logging

logger = logging.getLogger(__name__)

def process_message(message):
    logger.debug(f"Processing message: {message[:50]}...")
    logger.info(f"Message length: {len(message)}")

    try:
        result = translate_message(message)
        logger.info("Translation successful")
        return result
    except Exception as e:
        logger.error(f"Translation failed: {e}", exc_info=True)
        return None
```

#### Debugging Remote Updates
```python
# Debug remote JSON fetching
def debug_remote_fetch(url):
    logger.debug(f"Fetching from: {url}")

    try:
        data = fetch_remote_json(url)
        logger.debug(f"Received data keys: {list(data.keys())}")
        logger.debug(f"Data preview: {str(data)[:200]}...")
        return data
    except Exception as e:
        logger.error(f"Remote fetch failed: {e}", exc_info=True)
        return None
```

### Performance Debugging

#### Profiling Code Execution
```python
import cProfile
import pstats

def profile_translation():
    profiler = cProfile.Profile()
    profiler.enable()

    # Code to profile
    for i in range(100):
        translate_message(f"Test message {i}", "es")

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions

if __name__ == "__main__":
    profile_translation()
```

#### Memory Usage Monitoring
```python
import psutil
import os

def get_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    return memory_info.rss / 1024 / 1024  # MB

def log_memory_usage():
    memory_mb = get_memory_usage()
    logger.info(f"Memory usage: {memory_mb:.2f} MB")
```

## 📦 Building & Distribution

### Building Executables

#### Windows Executable
```batch
# Install PyInstaller
pip install pyinstaller

# Create single executable
pyinstaller --onefile --windowed --icon=assets/logo.ico main.py

# Create directory-based executable
pyinstaller --onedir --windowed --icon=assets/logo.ico main.py
```

#### Linux/macOS Executables
```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --icon=assets/logo.ico main.py
```

#### Advanced PyInstaller Configuration
```python
# pyinstaller.spec
a = Analysis(['main.py'],
             pathex=['.'],
             binaries=[],
             datas=[('assets', 'assets')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='SC_Chat_Translator',
          debug=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False,
          icon='assets/logo.ico')
```

### Creating Installers

#### Windows Installer (NSIS)
```bash
# Install NSIS
# Create installer script
# Build installer
makensis installer.nsi
```

#### Linux Packages
```bash
# Create .deb package
dpkg-deb --build star-conflict-translator_1.0.0

# Create .rpm package
rpmbuild -ba star-conflict-translator.spec
```

#### macOS Application Bundle
```bash
# Use PyInstaller with --onedir
pyinstaller --onedir --windowed main.py

# Create .dmg file
hdiutil create -volname "SC Chat Translator" -srcfolder dist/main -ov -format UDZO SC_Chat_Translator.dmg
```

### Distribution Checklist

- ✅ **Test executable** on clean system
- ✅ **Verify dependencies** are included
- ✅ **Check file paths** work correctly
- ✅ **Test translations** work
- ✅ **Verify settings** save/load correctly
- ✅ **Check for errors** in logs
- ✅ **Test uninstall** (if applicable)

## 🤝 Contributing Guidelines

### Getting Started with Contributing

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Create** a feature branch
4. **Make** your changes
5. **Write** tests for new functionality
6. **Run** the test suite
7. **Commit** your changes
8. **Push** to your fork
9. **Create** a Pull Request

### Types of Contributions

#### 🐛 Bug Fixes
- Fix reported bugs
- Improve error handling
- Fix performance issues
- Update dependencies

#### ✨ New Features
- Add new translation languages
- Implement new UI features
- Add configuration options
- Create new export formats

#### 📚 Documentation
- Improve user guides
- Add code documentation
- Create video tutorials
- Translate documentation

#### 🧪 Testing
- Write unit tests
- Create integration tests
- Add performance tests
- Improve test coverage

### Pull Request Process

#### PR Template
```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] No breaking changes

## Screenshots (if applicable)
Add screenshots of UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No new linting errors
```

#### Code Review Process

1. **Automated Checks**: CI/CD runs tests and linting
2. **Peer Review**: At least one maintainer reviews code
3. **Testing**: Reviewer tests functionality
4. **Approval**: PR approved and merged
5. **Deployment**: Changes deployed to production

### Recognition

Contributors are recognized in:
- **CHANGELOG.md**: List of changes by version
- **CONTRIBUTORS.md**: List of all contributors
- **GitHub Insights**: Contribution statistics
- **Release Notes**: Special mentions for major contributions

## 📚 API Documentation

### Core Classes

#### `TranslatedFileWatcher`
Main application class handling GUI and file monitoring.

**Methods:**
- `__init__()`: Initialize application and settings
- `_watch_latest_chat()`: Monitor chat log files
- `_check_remote_welcome()`: Handle remote updates
- `_manual_translate()`: Process manual translations

**Attributes:**
- `settings`: Application configuration dictionary
- `translator`: Google Translate instance
- `text_area_tab1`: Main chat display widget

#### `ToolTip`
Custom tooltip implementation for help text.

**Usage:**
```python
tooltip = ToolTip(widget, "Help text here")
```

### Key Functions

#### Translation Functions
```python
def compare_versions(remote_ver: str, local_ver: str) -> int:
    """Compare version strings semantically."""

def _safe_translate(text: str, dest: str) -> str:
    """Translate text with error handling."""
```

#### File Management
```python
def _load_settings() -> dict:
    """Load settings from JSON file."""

def _save_settings() -> None:
    """Save current settings to file."""
```

#### Remote Operations
```python
def _fetch_remote_json(url: str) -> dict:
    """Fetch JSON data from remote URL."""

def _check_remote_welcome() -> bool:
    """Check for remote welcome updates."""
```

## 🔧 Advanced Configuration

### Environment Variables

```bash
# Debug mode
export DEBUG=1

# Custom settings path
export SC_SETTINGS_PATH=/path/to/settings.json

# Custom log level
export LOG_LEVEL=DEBUG

# Disable remote updates
export DISABLE_REMOTE_UPDATES=1
```

### Configuration File

```json
{
  "app": {
    "version": "1.1.3",
    "debug": false,
    "log_level": "INFO"
  },
  "translation": {
    "default_language": "en",
    "fallback_language": "en",
    "timeout": 10,
    "retry_count": 3
  },
  "remote": {
    "welcome_url": "https://api.jsonsilo.com/public/...",
    "dictionary_url": "https://api.jsonsilo.com/public/...",
    "fetch_interval": 3600,
    "timeout": 5
  },
  "ui": {
    "theme": "dark",
    "scaling": 1.0,
    "font_size": 10
  }
}
```

### Performance Tuning

#### Memory Optimization
```python
# Limit chat history size
MAX_CHAT_HISTORY = 1000

# Clear old translations periodically
def cleanup_old_translations():
    # Implementation here
    pass
```

#### CPU Optimization
```python
# Throttle translation requests
import time
last_translation = 0
TRANSLATION_THROTTLE = 0.5  # seconds

def throttled_translate(text, dest):
    global last_translation
    now = time.time()
    if now - last_translation < TRANSLATION_THROTTLE:
        time.sleep(TRANSLATION_THROTTLE - (now - last_translation))
    last_translation = time.time()
    return translator.translate(text, dest=dest)
```

### Custom Extensions

#### Adding New Languages
```python
# In main.py, update LANGUAGES dictionary
LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    # Add new language here
    "Korean": "ko"
}
```

#### Custom Translation Service
```python
class CustomTranslator:
    def translate(self, text, dest):
        # Implement custom translation logic
        return translated_text

# Replace default translator
self.translator = CustomTranslator()
```

---

<div align="center">

**🚀 Happy Developing! 🚀**

*Questions? Check the [Issues](../../issues) or create a new discussion.*

*Found this guide helpful? ⭐ Star the repository!*

</div>
