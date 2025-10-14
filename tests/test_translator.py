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


class TestTranslationFunctionality:
    """Test translation-related functionality."""

    def test_safe_translate_success(self):
        """Test successful translation."""
        from main import TranslatedFileWatcher

        # Create a mock app instance without GUI
        with patch('main.ctk.CTk'):
            app = TranslatedFileWatcher()

        with patch('main.Translator') as mock_translator_class:
            mock_translator = MagicMock()
            mock_result = MagicMock()
            mock_result.text = "Hola Mundo"
            mock_translator.translate.return_value = mock_result
            mock_translator_class.return_value = mock_translator

            result = app._safe_translate("Hello World", "es")
            assert result == "Hola Mundo"
            mock_translator.translate.assert_called_once_with("Hello World", dest="es")

    def test_safe_translate_failure(self):
        """Test translation failure fallback."""
        from main import TranslatedFileWatcher

        # Create a mock app instance without GUI
        with patch('main.ctk.CTk'):
            app = TranslatedFileWatcher()

        with patch('main.Translator') as mock_translator_class:
            mock_translator = MagicMock()
            mock_translator.translate.side_effect = Exception("Translation failed")
            mock_translator_class.return_value = mock_translator

            result = app._safe_translate("Hello World", "es")
            assert result == "Hello World"  # Should return original text on failure

    def test_safe_translate_empty_text(self):
        """Test translation with empty text."""
        from main import TranslatedFileWatcher

        # Create a mock app instance without GUI
        with patch('main.ctk.CTk'):
            app = TranslatedFileWatcher()

        result = app._safe_translate("", "es")
        assert result == ""

        result = app._safe_translate(None, "es")
        assert result is None

    def test_game_dictionary_application(self):
        """Test game-specific dictionary substitution."""
        from main import TranslatedFileWatcher

        # Create a mock app instance without GUI
        with patch('main.ctk.CTk'):
            app = TranslatedFileWatcher()

        app.game_dictionary = {
            "xpam": "temple",
            "cnc": "thank you",
            "[Link 2 D: Ship_race3_m_t5_craftuniq]": "[Tornado]"
        }

        # Test dictionary substitution
        result = app._apply_game_dictionary("I found xpam in the game")
        assert "temple" in result

        result = app._apply_game_dictionary("cnc for the help")
        assert "thank you" in result

        # Test case insensitive matching
        result = app._apply_game_dictionary("XPAM is great")
        assert "temple" in result

    def test_manual_translate_functionality(self):
        """Test manual translation feature."""
        from main import TranslatedFileWatcher

        # Create a mock app instance without GUI
        with patch('main.ctk.CTk'):
            app = TranslatedFileWatcher()

        with patch.object(app, '_safe_translate', return_value="Hola"), \
             patch.object(app, '_insert_message_tab1') as mock_insert, \
             patch('main.pyperclip.copy') as mock_clipboard:

            app.manual_translate_lang = "es"
            app._manual_translate()

            # Should have called clipboard copy
            mock_clipboard.assert_called_once_with("Hola")

            # Should have inserted messages
            assert mock_insert.call_count >= 3  # Header, original, translated

    def test_language_short_code_conversion(self):
        """Test conversion between language names and codes."""
        from main import TranslatedFileWatcher

        # Create a mock app instance without GUI
        with patch('main.ctk.CTk'):
            app = TranslatedFileWatcher()

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

    def test_parse_line_trading(self):
        """Test parsing trading channel messages."""
        from main import TranslatedFileWatcher

        # Create a mock app instance without GUI
        with patch('main.ctk.CTk'):
            app = TranslatedFileWatcher()

        line = "[Player1] #trading>Hello world"
        category = "Trading"
        result = app._parse_line(line, category)

        assert result is not None
        ts, username, message, header, display = result
        assert username == "Player1"
        assert message == "Hello world"
        assert category in header

    def test_parse_line_skip_patterns(self):
        """Test that system messages are skipped."""
        from main import TranslatedFileWatcher

        # Create a mock app instance without GUI
        with patch('main.ctk.CTk'):
            app = TranslatedFileWatcher()

        # Test skip patterns
        skip_lines = [
            "CHAT| Join channel",
            "CHAT| Leave channel",
            "CHAT| System",
        ]

        for line in skip_lines:
            result = app._parse_line(line, "General")
            assert result is None

    def test_extract_second_bracket(self):
        """Test extraction of ship/item links."""
        from main import TranslatedFileWatcher

        # Create a mock app instance without GUI
        with patch('main.ctk.CTk'):
            app = TranslatedFileWatcher()

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
