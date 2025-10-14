"""
Unit tests for the main application module.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from sc_translator.main import compare_versions, TranslatedFileWatcher
except ImportError:
    # Fallback for direct testing from main.py
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from main import compare_versions, TranslatedFileWatcher


class TestVersionComparison:
    """Test version comparison functionality."""

    def test_equal_versions(self):
        """Test comparing identical versions."""
        assert compare_versions("1.0.0", "1.0.0") == 0

    def test_newer_version(self):
        """Test comparing when remote is newer."""
        assert compare_versions("1.1.0", "1.0.0") == 1

    def test_older_version(self):
        """Test comparing when remote is older."""
        assert compare_versions("1.0.0", "1.1.0") == -1

    @pytest.mark.parametrize("version1,version2,expected", [
        ("1.0.0", "1.0.0", 0),
        ("1.1.0", "1.0.0", 1),
        ("1.0.0", "1.1.0", -1),
        ("2.0.0", "1.9.9", 1),
        ("1.0.10", "1.0.2", 1),
    ])
    def test_version_comparison_parametrized(self, version1, version2, expected):
        """Test version comparison with various inputs."""
        assert compare_versions(version1, version2) == expected


class TestTranslatedFileWatcher:
    """Test the main application class."""

    @patch('sc_translator.main.ctk.CTk')
    def test_initialization(self, mock_ctk):
        """Test application initialization."""
        app = TranslatedFileWatcher()
        assert app is not None
        assert hasattr(app, 'settings')
        assert hasattr(app, 'game_dictionary')

    def test_language_mappings(self):
        """Test language code mappings."""
        app = TranslatedFileWatcher()
        assert 'English' in app.languages
        assert 'Russian' in app.languages
        assert app.languages['English'] == 'en'
        assert app.languages['Russian'] == 'ru'

    @patch('sc_translator.main.ctk.CTk')
    def test_manual_language_mappings(self, mock_ctk):
        """Test manual translation language mappings."""
        app = TranslatedFileWatcher()
        assert 'EN' in app.manual_languages
        assert 'RU' in app.manual_languages
        assert app.manual_languages['EN'] == 'en'
        assert app.manual_languages['RU'] == 'ru'


class TestChatCategories:
    """Test chat message categorization."""

    @patch('sc_translator.main.ctk.CTk')
    def test_chat_category_detection(self, mock_ctk):
        """Test detection of different chat categories."""
        app = TranslatedFileWatcher()

        # Test trading category
        assert app._categorize_line("#trading>Test message") == "Trading"

        # Test battle category
        assert app._categorize_line("#battle_123>Test message") == "Battle"

        # Test clan category
        assert app._categorize_line("#clan_abc>Test message") == "Clan"

        # Test squad category
        assert app._categorize_line("#squad_xyz>Test message") == "Squad"

        # Test unknown category
        assert app._categorize_line("#unknown>Test message") is None


if __name__ == "__main__":
    pytest.main([__file__])
