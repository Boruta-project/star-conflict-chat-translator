"""
Shared test fixtures.

- Every test runs with USERPROFILE/HOME/LOCALAPPDATA pointed at a temporary folder, so
  tests never read or write the developer's real settings.json, database or game logs.
- `headless_app` builds a TranslatedFileWatcher without creating a Tk window. Creating
  real windows repeatedly in one process fails with `image "pyimageN" doesn't exist`.
"""
import copy
import os
import sys
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture(autouse=True)
def isolated_user_dirs(tmp_path, monkeypatch):
    home = tmp_path / "home"
    local_appdata = home / "AppData" / "Local"
    local_appdata.mkdir(parents=True)
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("LOCALAPPDATA", str(local_appdata))
    return home


@pytest.fixture
def headless_app(isolated_user_dirs):
    import main

    app = main.TranslatedFileWatcher.__new__(main.TranslatedFileWatcher)
    app.logger = MagicMock()
    app.settings = copy.deepcopy(main.DEFAULT_SETTINGS)
    app.settings_path = str(isolated_user_dirs / "settings.json")
    app.translation_service = main.TranslationService()
    app._status_shows_pause = False
    app.languages = app.settings["languages"]
    app.manual_languages = app.settings["manual_languages"]
    app.target_lang = "en"
    app.manual_translate_lang = app.settings["manual_translate_lang"]
    app.game_dictionary = {}
    app._rebuild_dict_patterns()
    # Widgets touched by the methods under test
    app.status_label = MagicMock()
    app.text_area_tab1 = MagicMock()
    app.manual_entry = MagicMock()
    app.mymemory_email_var = MagicMock()
    app.mymemory_email_status = MagicMock()
    return app
