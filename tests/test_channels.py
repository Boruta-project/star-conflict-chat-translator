"""Tests for the opt-out channel translation filter (Settings → Translated Channels)."""
import json
from unittest.mock import MagicMock

import main


def _saved(app):
    with open(app.settings_path, encoding="utf-8") as f:
        return json.load(f)


def test_every_chat_category_has_a_checkbox():
    in_settings = {c for _, names in main.CHANNEL_GROUPS for c in names}
    assert in_settings == set(main.CHAT_CATEGORIES.values())


def test_all_channels_translated_by_default(headless_app):
    assert main.DEFAULT_SETTINGS["untranslated_channels"] == []
    for category in main.CHAT_CATEGORIES.values():
        assert headless_app._is_channel_translated(category)


def test_unticking_a_channel_is_saved_and_reversible(headless_app):
    headless_app._set_channel_translated("Trading", False)
    assert not headless_app._is_channel_translated("Trading")
    assert headless_app._is_channel_translated("Battle")
    assert _saved(headless_app)["untranslated_channels"] == ["Trading"]

    headless_app._set_channel_translated("Trading", True)
    assert headless_app._is_channel_translated("Trading")
    assert _saved(headless_app)["untranslated_channels"] == []


def test_default_settings_list_is_never_modified(headless_app):
    headless_app.settings["untranslated_channels"] = main.DEFAULT_SETTINGS["untranslated_channels"]
    headless_app._set_channel_translated("Clan", False)
    assert main.DEFAULT_SETTINGS["untranslated_channels"] == []


def test_translate_none_and_all(headless_app):
    headless_app.channel_vars = {c: MagicMock() for c in main.CHAT_CATEGORIES.values()}

    headless_app._set_all_channels_translated(False)
    assert not any(headless_app._is_channel_translated(c) for c in main.CHAT_CATEGORIES.values())
    for var in headless_app.channel_vars.values():
        var.set.assert_called_with(False)

    headless_app._set_all_channels_translated(True)
    assert all(headless_app._is_channel_translated(c) for c in main.CHAT_CATEGORIES.values())
    assert _saved(headless_app)["untranslated_channels"] == []
