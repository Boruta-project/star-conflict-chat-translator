# Contributing to Star Conflict Chat Translator

<div align="center">
  <h1>🤝 How to Contribute</h1>
  <p><em>Welcome! We're excited to have you contribute to our project</em></p>
</div>

## 📖 Table of Contents

- [🚀 Getting Started](#-getting-started)
- [💡 Types of Contributions](#-types-of-contributions)
- [🔄 Development Workflow](#-development-workflow)
- [📋 Contribution Guidelines](#-contribution-guidelines)
- [🧪 Testing](#-testing)
- [📝 Documentation](#-documentation)
- [🐛 Reporting Bugs](#-reporting-bugs)
- [💭 Feature Requests](#-feature-requests)
- [📜 Code of Conduct](#-code-of-conduct)
- [🙏 Recognition](#-recognition)

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have:
- ✅ Python 3.8+ installed
- ✅ Git for version control
- ✅ A GitHub account
- ✅ Basic knowledge of Python and GUI development

### Quick Setup

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/boruta-project/star-conflict-chat-translator.git
cd star-conflict-chat-translator

# Set up development environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run the application
python main.py
```

## 💡 Types of Contributions

### 🐛 Bug Fixes
Help us squash bugs and improve stability:
- Fix reported issues
- Improve error handling
- Fix performance problems
- Update dependencies

### ✨ New Features
Add new functionality to the application:
- New translation languages
- UI improvements
- New export formats
- Enhanced settings options

### 📚 Documentation
Improve our documentation:
- Fix typos and errors
- Add missing information
- Create tutorials and guides
- Translate documentation

### 🎮 Game Dictionary
Contribute to the community-maintained game dictionary:
- Add translations for game-specific terms
- Improve existing translations
- Test dictionary entries in-game
- Help expand coverage for new game content

### 🧪 Testing
Help ensure code quality:
- Write unit tests
- Create integration tests
- Test on different platforms
- Improve test coverage

### 🎨 Design & UX
Improve the user experience:
- UI/UX improvements
- Icon and theme updates
- Accessibility enhancements
- User feedback implementation

## 🔄 Development Workflow

### 1. Choose an Issue

- Check the [Issues](../../issues) page
- Look for "good first issue" or "help wanted" labels
- Comment on the issue to indicate you're working on it

### 2. Create a Branch

```bash
# Create and switch to a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-number-description
```

### 3. Make Changes

```bash
# Make your changes
# Write tests for new functionality
# Test your changes thoroughly
# Update documentation if needed
```

### 4. Commit Changes

```bash
# Stage your changes
git add .

# Commit with a clear message
git commit -m "Add: Brief description of changes

- More detailed explanation
- List of changes made
- Reference issue numbers"

# Example:
git commit -m "Add: Support for Spanish language

- Added Spanish (es) to language options
- Updated translation service integration
- Added Spanish UI strings
- Fixes #123"
```

### 5. Push and Create Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create a Pull Request on GitHub
# Fill out the PR template
# Wait for review
```

### 6. Address Feedback

```bash
# Make requested changes
git add .
git commit -m "Address review feedback"
git push origin feature/your-feature-name
```

## 📋 Contribution Guidelines

### Code Style

#### Python Standards
- Follow [PEP 8](https://pep8.org/) style guidelines
- Use 4 spaces for indentation
- Keep line length under 88 characters
- Use descriptive variable names

#### Example Good Code
```python
def translate_message(message, target_lang, source_lang=None):
    """
    Translate a chat message to the target language.

    Args:
        message (str): The message to translate
        target_lang (str): Target language code (e.g., 'en', 'es')
        source_lang (str, optional): Source language code

    Returns:
        str: Translated message

    Raises:
        TranslationError: If translation fails
    """
    if not message or not target_lang:
        raise ValueError("Message and target language are required")

    try:
        result = translator.translate(message, dest=target_lang)
        return result.text
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return f"[Translation error: {e}]"
```

#### Example Bad Code
```python
def trans_msg(msg,tgt_lang,src_lang=None):  # Bad: unclear names, no spaces
    if not msg or not tgt_lang:  # Bad: no error handling details
        raise ValueError("req")  # Bad: unclear error message
    try:
        r = translator.translate(msg,dest=tgt_lang)  # Bad: short variable names
        return r.text
    except:  # Bad: bare except
        return "[error]"  # Bad: unclear error message
```

### Commit Messages

#### Format
```
Type: Brief description of changes

- More detailed explanation
- List specific changes made
- Reference issue numbers with #123
```

#### Types
- **Add**: New features or functionality
- **Fix**: Bug fixes
- **Update**: Changes to existing functionality
- **Remove**: Removed features or code
- **Docs**: Documentation changes
- **Test**: Test-related changes
- **Style**: Code style/formatting changes

### Pull Request Guidelines

#### PR Template
```markdown
## Description
Brief description of the changes made

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change
- [ ] Documentation update
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
- [ ] Commit messages are clear
```

#### PR Best Practices

1. **Keep PRs Small**: Focus on one feature or fix per PR
2. **Clear Description**: Explain what and why, not just how
3. **Reference Issues**: Link to related issues with #123
4. **Test Thoroughly**: Ensure your changes work as expected
5. **Update Documentation**: Include docs for new features
6. **Squash Commits**: Clean up commit history before merging

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific tests
pytest tests/test_translation.py
pytest tests/test_main.py::test_language_selection

# Run tests in verbose mode
pytest -v

# Run tests and stop on first failure
pytest -x
```

### Writing Tests

#### Unit Test Example
```python
# tests/test_translation.py
import pytest
from main import compare_versions

class TestVersionComparison:
    def test_equal_versions(self):
        assert compare_versions("1.0.0", "1.0.0") == 0

    def test_newer_version(self):
        assert compare_versions("1.1.0", "1.0.0") == 1

    def test_older_version(self):
        assert compare_versions("1.0.0", "1.1.0") == -1

    @pytest.mark.parametrize("version1,version2,expected", [
        ("1.0.0", "1.0.0", 0),
        ("1.1.0", "1.0.0", 1),
        ("1.0.0", "1.1.0", -1),
        ("2.0.0", "1.9.9", 1),
    ])
    def test_version_comparison_parametrized(self, version1, version2, expected):
        assert compare_versions(version1, version2) == expected
```

#### Integration Test Example
```python
# tests/test_integration.py
import pytest
from main import TranslatedFileWatcher

class TestApplicationIntegration:
    def test_full_translation_workflow(self):
        # Test complete translation workflow
        app = TranslatedFileWatcher()
        app.settings = app._load_settings()

        # Test language setting
        app._change_language("Spanish")
        assert app.target_lang == "es"

        # Test translation (mock the actual service)
        # This would require mocking the Google Translate service
        pass
```

### Test Coverage Goals

- **Unit Tests**: 80%+ coverage for core functions
- **Integration Tests**: Cover major user workflows
- **UI Tests**: Basic functionality verification
- **Cross-Platform**: Test on Windows, Linux, macOS

## 📝 Documentation

### Documentation Types

#### Code Documentation
- **Docstrings**: All public functions and classes
- **Comments**: Complex logic explanations
- **Type Hints**: Parameter and return types

#### User Documentation
- **README.md**: Main project documentation
- **USER_GUIDE.md**: Detailed user instructions
- **DEVELOPMENT.md**: Development setup guide
- **CHANGELOG.md**: Version history

### Documentation Standards

#### Function Documentation
```python
def process_chat_message(message: str, category: str) -> dict:
    """
    Process a single chat message and prepare it for translation.

    This function handles the complete processing pipeline for a chat message,
    including category detection, user extraction, and text cleaning.

    Args:
        message (str): Raw chat message from log file
        category (str): Chat category (e.g., 'Battle', 'Trading')

    Returns:
        dict: Processed message data with keys:
            - 'username': Extracted player name
            - 'text': Clean message text
            - 'timestamp': Message timestamp
            - 'category': Chat category

    Raises:
        ValueError: If message format is invalid
        ProcessingError: If message cannot be processed

    Example:
        >>> process_chat_message("[Player1]: Hello world", "General")
        {'username': 'Player1', 'text': 'Hello world', 'timestamp': '2024-01-01 12:00:00', 'category': 'General'}
    """
    pass
```

#### README Updates
When adding new features, update the README.md:
- Add feature to the feature list
- Include usage examples
- Update screenshots if UI changed
- Add to table of contents

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
## Bug Report

### Description
Brief description of the bug

### Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

### Expected Behavior
What should happen

### Actual Behavior
What actually happens

### Screenshots
If applicable, add screenshots

### Environment
- OS: [e.g., Windows 10]
- Python Version: [e.g., 3.9.0]
- Application Version: [e.g., 1.1.3]
- Star Conflict Version: [e.g., latest]

### Additional Context
Any other information about the problem
```

### Bug Report Checklist

- [ ] Clear, descriptive title
- [ ] Step-by-step reproduction steps
- [ ] Expected vs actual behavior
- [ ] Environment details
- [ ] Screenshots if UI-related
- [ ] Log files if available
- [ ] Related issues or PRs

## 💭 Feature Requests

### Feature Request Template

```markdown
## Feature Request

### Problem
What's the problem this feature would solve?

### Solution
Describe the solution you'd like

### Alternatives
Describe alternative solutions you've considered

### Additional Context
Add any other context about the feature request
```

### Feature Request Guidelines

- **Check Existing Issues**: Search for similar requests first
- **Clear Description**: Explain the problem and solution clearly
- **Use Cases**: Provide specific use cases
- **Mockups**: Include UI mockups if applicable
- **Priorities**: Consider impact vs effort

## 📜 Code of Conduct

### Our Standards

#### ✅ Positive Behavior
- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn
- Acknowledge good work
- Be patient with different skill levels

#### ❌ Unacceptable Behavior
- Harassment or discrimination
- Personal attacks
- Trolling or spam
- Sharing private information
- Promoting harmful content

### Enforcement

Violations of the code of conduct will result in:
1. **Warning**: Private message with explanation
2. **Temporary Ban**: If behavior continues
3. **Permanent Ban**: For serious violations

### Reporting Violations

To report code of conduct violations:
- Email: borutaproject@gmail.com
- GitHub Issue: Create private issue
- Be specific about the incident
- Include dates, links, and screenshots

## 🙏 Recognition

### How We Recognize Contributors

#### 🏆 Hall of Fame
Contributors are recognized in:
- **CHANGELOG.md**: Credit for features and fixes
- **CONTRIBUTORS.md**: List of all contributors
- **GitHub Insights**: Contribution statistics
- **Release Notes**: Special mentions

#### 🎖️ Contribution Levels

**🥉 Contributor** (1-5 contributions)
- Bug fixes and small improvements
- Documentation updates
- Test additions

**🥈 Regular Contributor** (6-25 contributions)
- Feature implementations
- Significant bug fixes
- Major documentation improvements

**🥇 Core Contributor** (26+ contributions)
- Major features
- Architecture improvements
- Project maintenance
- Community leadership

### Special Recognition

- **🎯 First-Time Contributors**: Welcome message and mentorship
- **🏆 Major Features**: Highlighted in release announcements
- **📚 Documentation Heroes**: Special thanks for comprehensive docs
- **🐛 Bug Hunters**: Recognition for finding critical issues

### Getting Recognition

Contributors receive:
- ✅ GitHub profile recognition
- ✅ Project contributor status
- ✅ Priority support for issues
- ✅ Early access to new features
- ✅ Invitation to private discussions

---

<div align="center">

**🚀 Ready to Contribute? Let's Build Something Amazing! 🚀**

*Questions? Check the [Issues](../../issues) or start a [Discussion](../../discussions).*

*First-time contributor? Look for issues labeled ["good first issue"](../../issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).*

</div>
