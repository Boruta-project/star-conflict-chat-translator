"""
Unit tests for translation functionality.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import from main.py in the root directory
from main import TranslatedFileWatcher
from translate.exceptions import TranslationError


class TestTranslationFunctionality:
    """Test translation-related functionality.

    EXPERIMENTAL backend (see docs/design-translate-library-migration.md): translation
    goes through the `translate` package's MyMemory provider, mocked here as
    `main.MyMemoryTranslator`. Source language is always "autodetect" — MyMemory's own
    real auto-detect sentinel — since chat lines arrive in unpredictable languages.
    """

    def test_safe_translate_success(self, headless_app):
        """Test successful translation."""
        from main import TranslatedFileWatcher

        app = headless_app

        with patch('main.MyMemoryTranslator') as mock_translator_class:
            mock_translator_class.return_value.translate.return_value = "Hola Mundo"

            result = app._safe_translate("Hello World", "es")
            assert result == "Hola Mundo"
            mock_translator_class.assert_called_once_with(to_lang="es", from_lang="autodetect", email="")
            mock_translator_class.return_value.translate.assert_called_once_with("Hello World")

    def test_safe_translate_failure(self, headless_app):
        """Test translation failure fallback."""
        from main import TranslatedFileWatcher

        app = headless_app

        with patch('main.MyMemoryTranslator') as mock_translator_class:
            mock_translator_class.return_value.translate.side_effect = TranslationError("Translation failed")

            result = app._safe_translate("Hello World", "es")
            assert result == "Hello World"  # Should return original text on failure

    def test_safe_translate_empty_text(self, headless_app):
        """Test translation with empty text."""
        from main import TranslatedFileWatcher

        app = headless_app

        result = app._safe_translate("", "es")
        assert result == ""

        result = app._safe_translate(None, "es")
        assert result is None

    def test_safe_translate_uses_configured_mymemory_email(self, headless_app):
        """An optional per-user email (settings.json "mymemory_email") raises MyMemory's
        anonymous 5,000 chars/day cap to 50,000/day — must never be hard-coded, only
        forwarded from whatever the user configured."""
        from main import TranslatedFileWatcher

        app = headless_app
        app.settings["mymemory_email"] = "player@example.com"

        with patch('main.MyMemoryTranslator') as mock_translator_class:
            mock_translator_class.return_value.translate.return_value = "Hola"

            app._safe_translate("Hello", "es")
            mock_translator_class.assert_called_once_with(
                to_lang="es", from_lang="autodetect", email="player@example.com"
            )

    def test_safe_translate_over_length_falls_back(self, headless_app):
        """MyMemory hard-caps queries at 500 chars/request; translate's own chunking
        (calibrated at 1000 chars) doesn't split anything below that, so a long welcome
        message can raise TranslationError — must fall back like any other failure."""
        from main import TranslatedFileWatcher

        app = headless_app

        long_text = "x" * 753
        with patch('main.MyMemoryTranslator') as mock_translator_class:
            mock_translator_class.return_value.translate.side_effect = TranslationError(
                "QUERY LENGTH LIMIT EXCEEDED. MAX ALLOWED QUERY : 500 CHARS"
            )

            result = app._safe_translate(long_text, "es")
            assert result == long_text

    def test_translate_text_returns_original_when_already_target_language(self):
        """MyMemory refuses to 'translate' text it auto-detects as already being in the
        target language (e.g. short/ambiguous chat slang like 'ping 200 xd' detected as
        English when the target is also English) — raises TranslationError with this
        exact message instead of a no-op. The correct output is the original text, not
        a surfaced error, and this must work from every call site (chat, manual,
        welcome messages alike), so it's handled in the shared _translate_text helper."""
        from main import _translate_text

        with patch('main.MyMemoryTranslator') as mock_translator_class:
            mock_translator_class.return_value.translate.side_effect = TranslationError(
                "PLEASE SELECT TWO DISTINCT LANGUAGES"
            )

            result = _translate_text("ping 200 xd", "en")
            assert result == "ping 200 xd"

    def test_translate_text_reraises_other_translation_errors(self):
        """Only the same-language case should be swallowed — any other TranslationError
        (quota exceeded, invalid language, etc.) must still propagate so callers'
        existing fallback-and-log behavior applies."""
        from main import _translate_text

        with patch('main.MyMemoryTranslator') as mock_translator_class:
            mock_translator_class.return_value.translate.side_effect = TranslationError(
                "QUERY LENGTH LIMIT EXCEEDED. MAX ALLOWED QUERY : 500 CHARS"
            )

            with pytest.raises(TranslationError):
                _translate_text("x" * 600, "es")

    def test_translate_calls_are_throttled(self):
        """Consecutive translate calls (regardless of call site — startup welcome
        messages, manual translate, live chat) must never fire back-to-back without
        spacing, as reasonable etiquette toward MyMemory's free service."""
        import time as time_module
        from main import _throttle_translate_call
        import main as main_module

        main_module._last_translate_call_ts = 0.0
        start = time_module.monotonic()
        _throttle_translate_call()
        _throttle_translate_call()
        elapsed = time_module.monotonic() - start
        assert elapsed >= main_module._MIN_SECONDS_BETWEEN_TRANSLATE_CALLS * 0.9

    def test_game_dictionary_application(self, headless_app):
        """Test game-specific dictionary substitution."""
        from main import TranslatedFileWatcher

        app = headless_app

        app.game_dictionary = {
            "xpam": "temple",
            "cnc": "thank you",
            "[Link 2 D: Ship_race3_m_t5_craftuniq]": "[Tornado]"
        }
        app._rebuild_dict_patterns()

        # Test dictionary substitution
        result = app._apply_game_dictionary("I found xpam in the game")
        assert "temple" in result

        result = app._apply_game_dictionary("cnc for the help")
        assert "thank you" in result

        # Test case insensitive matching
        result = app._apply_game_dictionary("XPAM is great")
        assert "temple" in result

    def test_manual_translate_functionality(self, headless_app):
        """Test manual translation feature."""
        from main import TranslatedFileWatcher

        app = headless_app

        from main import TranslationOutcome

        with patch.object(app.translation_service, 'translate',
                          return_value=TranslationOutcome("Hola", True)), \
             patch.object(app, '_insert_message_tab1') as mock_insert, \
             patch('main.pyperclip.copy') as mock_clipboard:

            app.manual_translate_lang = "es"
            app._manual_translate()

            # Should have called clipboard copy
            mock_clipboard.assert_called_once_with("Hola")

            # Should have inserted messages
            assert mock_insert.call_count >= 3  # Header, original, translated

    def test_language_short_code_conversion(self, headless_app):
        """Test conversion between language names and codes."""
        from main import TranslatedFileWatcher

        app = headless_app

        # Test getting short code for language
        result = app._get_short_code_for_lang("en")
        assert result == "EN"

        result = app._get_short_code_for_lang("ru")
        assert result == "RU"

        # Test unknown language
        result = app._get_short_code_for_lang("unknown")
        assert result == "EN"  # fallback


class TestMessageProcessing:
    """Test message parsing and processing."""

    def test_parse_line_trading(self, headless_app):
        """Test parsing trading channel messages."""
        from main import TranslatedFileWatcher

        app = headless_app

        line = "11:45:05.447     CHAT| <        #trading>[ Player1] Hello world"
        category = "Trading"
        result = app._parse_line(line, category)

        assert result is not None
        ts, username, message, header, display = result
        assert username == "Player1"
        assert message == "Hello world"
        assert category in header

    def test_parse_line_skip_patterns(self, headless_app):
        """Test that system messages are skipped."""
        from main import TranslatedFileWatcher

        app = headless_app

        # Test skip patterns
        skip_lines = [
            "CHAT| Join channel",
            "CHAT| Leave channel",
            "CHAT| System",
        ]

        for line in skip_lines:
            result = app._parse_line(line, "General")
            assert result is None

    def test_extract_second_bracket(self, headless_app):
        """Test extraction of ship/item links."""
        from main import TranslatedFileWatcher

        app = headless_app

        # Test with ship link
        line = "[Player] [Link 2 D: Ship_race3_m_t5_craftuniq] is cool"
        result = app._extract_second_bracket(line)
        assert result == "Link 2 D: Ship_race3_m_t5_craftuniq"

        # Test without second bracket
        line = "[Player] Hello world"
        result = app._extract_second_bracket(line)
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__])
