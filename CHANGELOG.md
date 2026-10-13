# Changelog

<div align="center">
  <h1>📋 Version History</h1>
  <p><em>Complete history of changes and improvements</em></p>
</div>

All notable changes to **Star Conflict Chat Translator** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.1] - 2026-10-13

### Added
- **Translated Channels** (Settings): a checkbox for every chat channel, all ticked by default. Unticked channels are still shown and saved, just not translated, which saves the free daily limit. Explained in [Translation Service](docs/translation-service.md#translate-only-the-channels-you-need).
- **Project website** at https://jacek-mar.github.io/star-conflict-chat-translator/ (GitHub Pages, built from `docs/`).

### Fixed
- The app no longer crashes at startup on Linux and macOS (the window icon is Windows-only).

### Changed
- Settings → Translation Service: the status line under the email field only takes up space while it shows a message.

### Developer notes
- **Build and CI rebuilt.** One PyInstaller spec (`packaging/`) and one build script (`scripts/build_exe.py`) used both locally and in CI; every build is smoke-tested without Python on `PATH`. Runtime libraries are pinned in `requirements-lock.txt`; a weekly workflow tests the newest allowed versions. Tag pushes create a draft release after a version check and the full test matrix. See [docs/releasing.md](docs/releasing.md).
- Supported Python versions for running from source: 3.10–3.14 (3.8/3.9 are no longer supported by the libraries the app uses).
- The exe accepts `--smoke-test [report-file]` to check a build without starting the app.
- Removed the old build scripts (`build/`, `scripts/build.py`) and the unused `src/sc_translator/` copy of `main.py`.

## [1.4.0] - 2026-10-13

### Fixed
- **New Star Conflict log folder.** The game now writes its logs to `%LOCALAPPDATA%\Targem\StarConflict\logs` instead of `Documents\My Games\StarConflict\logs`. The app now defaults to the new folder (falling back to the old one), and switches existing installs automatically if they still point at the old default and the game has moved. A custom logs folder chosen by the user is never changed.
- **Readable translation errors.** Failed translations used to print the raw exception — including the full request URL — into the chat. They now show a short note such as `[not translated – daily limit reached]`; technical details go to the App Log only. The original message is always displayed.
- Manual translation no longer copies an error message to the clipboard.

### Added
- **Translation pause when the free daily limit is reached.** Instead of sending (and failing) a request for every chat line, the app pauses translation until the time MyMemory reports for the reset, shows one notice in the chat and the resume time in the status bar, then resumes on its own.
- **Email setting in the Settings tab** (Settings → Translation Service). Optional; raises MyMemory's free limit from 5,000 to 50,000 characters/day. Empty by default, stored only in the local `settings.json`, never written to the log.
- **Translation cache.** Repeated messages are answered from memory instead of a new request.
- Messages with no letters at all (numbers, punctuation, emoji) are shown unchanged without a request.
- Status bar message when no `chat.log` can be found in the configured logs folder.
- Help: links to Releases and to the issue tracker.
- Settings → Translation Service: a "Read more" link to the new [Translation Service](docs/translation-service.md) page, which explains why an email raises the daily limit and why the app no longer uses Google Translate. README and User Guide no longer describe the app as using Google Translate.

### Changed
- The project's primary home is now https://github.com/jacek-mar/star-conflict-chat-translator. The user manual is the GitHub-hosted [User Guide](docs/user-guide.md); the Google Sites page is no longer maintained.
- **Remote welcome message and community dictionary moved from jsonsilo.com to the GitHub repository.** The app reads `remote/welcome.json` and `game_dictionary.json` from the `main` branch (see `remote/README.md`). Saved settings that still point at the old jsonsilo dictionary URL are updated automatically; a custom URL is kept.

### Developer notes
- Tests no longer create real Tk windows or touch the developer's real settings: `tests/conftest.py` isolates `USERPROFILE`/`LOCALAPPDATA` and provides a headless app fixture. Pre-existing failing tests were fixed; new tests cover the translation service and the log folder migration.
- `requests` is now a declared dependency (it was already installed with `translate`).

## [1.3.0] - 2026-09-26

### Changed — Translation backend switched to MyMemory via `translate` (experimental)
- Replaced the unmaintained `googletrans` dependency with the `translate` package's MyMemory backend. Google's free/unofficial translate endpoints began blocking automated queries platform-wide in September 2026, affecting scraping-based libraries generally. MyMemory is an independent service unaffected by this. See `docs/design-deep-translator-migration.md` and `docs/design-translate-library-migration.md` for the full evaluation; this backend is marked experimental and may be revisited if MyMemory's quality or limits prove insufficient in practice.
- Translation calls are now synchronous; removed the `asyncio` event-loop bridging (`run_async_translation`) that the previous async API required.
- Source language is auto-detected for every translation (chat lines, manual translate, welcome messages) — no source language ever needs to be configured.
- Added an optional `mymemory_email` setting (`settings.json`, empty by default) that raises MyMemory's daily quota from 5,000 to 50,000 characters when set to a personal email address. This must remain a per-user setting; sharing one email across installs pools everyone onto the same quota.

### Fixed
- MyMemory rejects "translating" text into the language it's already detected as being in, rather than returning it unchanged — surfacing as `[Translation error: PLEASE SELECT TWO DISTINCT LANGUAGES]`, most often on short or ambiguous chat messages. This is now handled centrally: the original text is returned in this case, since that is the correct output.
- Hardcoded and remote-fetched UI strings (welcome message, "what's new" list, etc.) are always authored in English; translation is now skipped for them when the chat-translation target language is also English, avoiding the same no-op error above.
- All translation calls (startup welcome message, manual translate, live chat) are spaced at least ~0.3s apart app-wide as a courtesy to the free service.

### Removed
- `googletrans` and `deep-translator` dependencies, the `run_async_translation()` helper, an unused `self.translator` instance attribute, and a Google-specific language-code normalization step (`zh-cn` → `zh-CN`) that MyMemory does not require.

### Fixed — packaging and naming
- The `sc-chat-translator` console-script entry point declared `main:main`, but `main.py` had no `main()` function; installing the package and running the command would have failed. Added a proper `main()` entry point in both `main.py` and `src/sc_translator/main.py`.
- `src/sc_translator/main.py`, an unpackaged duplicate of the application, still referenced `googletrans` and an older version number; brought up to date with the current translation backend and version.
- Reworded the welcome message's description of the translation engine to be backend-agnostic, rather than naming a specific provider that may change.
- Corrected `pyproject.toml`'s isort configuration, which listed a first-party module that does not exist in this project.

## [1.2.0] - 2026-03-28

### Added
- Resizable application window with enforced minimum size (640×670)
- Remote dictionary sync now persists merged entries to local `game_dictionary.json` — community entries survive offline starts
- "Sync Now" button forces immediate remote dictionary fetch from the Settings tab
- "Remote overrides local on conflict" toggle — opt-in to let community dictionary win on key conflicts
- Sync status label in Settings shows last sync time and entry count
- `_load_local_dictionary()` fast path used at startup — no network call blocks the GUI
- `_rebuild_dict_patterns()` pre-compiles dictionary regex patterns on each dictionary reload for better message-throughput performance
- Version update notification message now appears in chat (was commented out in 1.1.3)
- New settings keys: `remote_dictionary_overrides_local`, `remote_dict_version`

### Changed

- Remote fetch (welcome + dictionary) moved to background daemon thread — window is interactive immediately on launch
- Rate limiting for remote fetch re-enabled: default interval 1 hour (was disabled/commented out since 1.1.2)
- Help button width formula corrected: `DEFAULT_WINDOW_WIDTH * HELP_BUTTON_RATIO` (was `* 0.1 * 0.1` = 6 px)
- `app_version` in settings now always reflects the current binary version on each save
- Settings tab reorganised into four labelled groups: Translation Languages, Star Conflict Logs Folder, Game Dictionary, Remote Dictionary
- Game-path buttons (Browse / Save Path / Reset) consolidated onto a single row
- Hardcoded pixel widths removed from tabview and game-path entry — layout adapts to window size
- Dictionary "Update / Reload Dictionary" button split into "Add" and "Reload" — clearer actions, no silent behaviour difference
- Log message in `_fetch_remote_json` now shows the URL prefix instead of always saying "Remote welcome fetch failed"
- `_show_help_version_result` now displays the actual message passed to it (was hardcoded "Check complete")
- `show_extended_welcome` flag reset to `False` immediately after the extended message is shown

### Fixed

- Startup freeze of 6–8 seconds (50-70% of starts) caused by two synchronous HTTP calls on the main thread
- Ghost `last_notified_version` > `APP_VERSION` permanently suppressing update notifications — corrected on first 1.2.0 start
- Remote dictionary entries never reaching `game_dictionary.json` on disk — users saw only 16 local entries despite 343 remote entries
- Welcome counter stuck at 11 for users who received a test remote version value — reset on correction of ghost version
- Redundant double load of settings at startup removed (lines 287–289 → 312–314)
- Four redundant backward-compatibility guards in `_load_settings()` removed (already covered by general migration loop)
- Obsolete `welcome_message_override` migration code removed

### Removed

- Debug logging blocks `=== RAW REMOTE DATA RECEIVED ===` and `=== CONTENT COMPARISON DEBUG ===` from production log output
- Commented-out `TEMPORARILY DISABLE FETCH INTERVAL FOR DEBUGGING` block

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
