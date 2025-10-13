# Changelog

<div align="center">
  <h1>📋 Version History</h1>
  <p><em>Complete history of changes and improvements</em></p>
</div>

All notable changes to **Star Conflict Chat Translator** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.3] - 2025-10-12

### Added
- Close confirmation popup with minimize, close, and cancel options
- Window position freezing during close confirmation dialog
- Async translation support for googletrans 4.0.2 compatibility
- Separate Translator instances to prevent coroutine reuse issues
- Version control system with automatic update notifications
- Enhanced remote welcome message handling
- Improved error handling for network operations
- Better logging and debugging capabilities

### Changed
- Updated googletrans integration to handle async API changes
- Optimized remote fetch intervals for better performance
- Improved settings persistence and backward compatibility
- Enhanced user interface responsiveness

### Fixed
- Fixed googletrans 4.0.2 async coroutine errors ("Event loop is closed", "cannot reuse already awaited coroutine")
- Fixed "Translation error: 'NoneType' object has no attribute 'send'" issues
- Fixed issue with simultaneous message ID and version changes
- Resolved settings update timing issues
- Improved translation error handling

## [1.1.2] - 2025-08-24

### Added
- Remote dictionary support for community translations
- Enhanced welcome message system with color customization
- Improved chat category detection and color coding
- Better error handling for translation failures
- Clipboard integration for manual translations

### Changed
- Updated Google Translate API integration
- Improved performance for large chat logs
- Enhanced user interface with better tooltips

### Fixed
- Fixed crash when translation service is unavailable
- Resolved issues with Cyrillic character display
- Fixed settings not saving properly on some systems
- Improved compatibility with different Star Conflict versions

## [1.1.0] - 2025-08-17

### Added
- Manual translation feature with clipboard integration
- Enhanced dictionary management system
- Better support for game-specific terminology
- CSV export functionality for chat history

### Changed
- Updated user interface with modern design
- Improved translation accuracy for gaming terms
- Enhanced performance for real-time translation
- Better error messages and user feedback

### Fixed
- Fixed memory leaks during long sessions
- Resolved issues with special characters in translations
- Fixed problems with automatic game path detection
- Improved stability on different Windows versions

## [1.0.14] - 2025-07-26

### Added
- Real-time chat log monitoring
- Automatic language detection
- Custom dictionary for game terms
- SQLite database for chat history
- Modern GUI with dark theme
- Multi-language support with customizable language configuration via Google Translate

### Changed
- Complete rewrite with modern Python practices
- Improved translation speed and accuracy
- Better error handling and recovery
- Enhanced user experience

### Fixed
- Initial release with core functionality
- Basic translation and monitoring features
- Fundamental UI and user interaction

## [1.0.9] - 2025-05-17

### Added
- Dictionary override functionality in settings
- Fixed crash when translation returned None
- Improved display of Cyrillic characters
- Basic remote update system
- Enhanced error handling

### Changed
- Improved translation reliability
- Better handling of network timeouts
- Enhanced user interface elements

### Fixed
- Various stability improvements
- Better error recovery mechanisms
- Improved compatibility with different systems

## [1.0.4] - 2025-05-01

### Added
- Initial stable release
- Basic chat translation functionality
- Support for user-selected languages
- Simple settings management
- Basic error handling

### Changed
- Initial implementation with core features
- Basic user interface
- Fundamental translation capabilities

### Fixed
- Initial bug fixes and stability improvements
- Basic functionality verification

---

## 📋 Types of Changes

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities

## 🔖 Version Numbering

This project uses [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.0.16)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

## 📅 Release Schedule

- **Major releases**: Every 6-12 months
- **Minor releases**: Every 1-2 months
- **Patch releases**: As needed for critical fixes

## 🧪 Pre-release Versions

- **Alpha**: Early testing, may have bugs
- **Beta**: Feature complete, stability testing
- **RC (Release Candidate)**: Final testing before release

## 📊 Download Statistics

| Version | Downloads | Release Date |
|---------|-----------|--------------|

## 🤝 How to Report Issues

Found a bug or have a feature request? Please:

1. Check existing [Issues](../../issues) first
2. Create a new issue with detailed information
3. Include your system information and steps to reproduce
4. Attach relevant log files if available

## 🙏 Acknowledgments

Special thanks to:
- **Star Conflict Community** for feedback and testing
- **Google Translate** for translation services
- **Open Source Contributors** for improvements and fixes
- **Beta Testers** for valuable feedback

---

<div align="center">

**📈 Keep up with the latest improvements!**

*See the [Releases](../../releases) page for downloadable versions.*

</div>
