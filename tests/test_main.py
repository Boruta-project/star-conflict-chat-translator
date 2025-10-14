"""
Unit tests for the main application module.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import from main.py in the root directory
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

    @patch('main.ctk.CTk')
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

    def test_manual_language_mappings(self):
        """Test manual translation language mappings."""
        # Test without GUI initialization to avoid display issues in CI
        from main import DEFAULT_SETTINGS
        manual_languages = DEFAULT_SETTINGS["manual_languages"]
        assert 'EN' in manual_languages
        assert 'RU' in manual_languages
        assert manual_languages['EN'] == 'en'
        assert manual_languages['RU'] == 'ru'


class TestChatCategories:
    """Test chat message categorization."""

    def test_chat_category_detection(self):
        """Test detection of different chat categories."""
        # Test the categorization function directly without GUI
        from main import CHAT_CATEGORIES

        # Test trading category
        assert "#trading>" in CHAT_CATEGORIES
        assert CHAT_CATEGORIES["#trading>["] == "Trading"

        # Test battle category
        assert "#battle_" in CHAT_CATEGORIES
        assert CHAT_CATEGORIES["#battle_"] == "Battle"

        # Test clan category
        assert "#clan_" in CHAT_CATEGORIES
        assert CHAT_CATEGORIES["#clan_"] == "Clan"

        # Test squad category
        assert "#squad_" in CHAT_CATEGORIES
        assert CHAT_CATEGORIES["#squad_"] == "Squad"


if __name__ == "__main__":
    pytest.main([__file__])
