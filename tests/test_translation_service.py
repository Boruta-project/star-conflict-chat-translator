"""
Tests for v1.4.0 translation handling: error classification, quota pause, cache,
the no-letters skip, the MyMemory email setting and the game log folder migration.
"""
import os
from unittest.mock import MagicMock, patch

import pytest
import requests
from translate.exceptions import TranslationError

import main
from main import (
    TRANSLATION_ERROR_LABELS,
    TranslationService,
    _classify_translation_error,
    _has_letters,
    _is_valid_email,
    _parse_quota_reset_seconds,
)

QUOTA_TEXT = ("MYMEMORY WARNING: YOU USED ALL AVAILABLE FREE TRANSLATIONS FOR TODAY. "
              "NEXT AVAILABLE IN  10 HOURS 32 MINUTES 50 SECONDS VISIT "
              "HTTPS://MYMEMORY.TRANSLATED.NET/DOC/USAGELIMITS.PHP TO TRANSLATE MORE")


def http_429_error(body=""):
    response = requests.Response()
    response.status_code = 429
    response._content = body.encode("utf-8")
    return requests.exceptions.HTTPError(
        "429 Client Error: Too Many Requests for url: "
        "https://api.mymemory.translated.net:443/get?q=%D0%BC&langpair=autodetect%7Cen",
        response=response,
    )


class FakeClock:
    def __init__(self, now=1_000_000.0):
        self.now = now

    def __call__(self):
        return self.now


class TestErrorClassification:

    def test_http_429_is_quota(self):
        assert _classify_translation_error(http_429_error())[0] == "quota"

    def test_http_429_body_gives_reset_time(self):
        kind, retry = _classify_translation_error(http_429_error(QUOTA_TEXT))
        assert kind == "quota"
        assert retry == 10 * 3600 + 32 * 60 + 50

    def test_mymemory_warning_in_translation_error_is_quota(self):
        assert _classify_translation_error(TranslationError(QUOTA_TEXT))[0] == "quota"

    def test_length_limit(self):
        err = TranslationError("QUERY LENGTH LIMIT EXCEEDED. MAX ALLOWED QUERY : 500 CHARS")
        assert _classify_translation_error(err) == ("too_long", None)

    def test_network_errors(self):
        assert _classify_translation_error(requests.exceptions.ConnectionError("x"))[0] == "network"
        assert _classify_translation_error(requests.exceptions.Timeout("x"))[0] == "network"

    def test_other(self):
        assert _classify_translation_error(TranslationError("INVALID LANGUAGE PAIR")) == ("other", None)

    @pytest.mark.parametrize("text, expected", [
        ("NEXT AVAILABLE IN 2 HOURS", 7200),
        ("next available in 15 minutes 3 seconds", 903),
        ("NEXT AVAILABLE IN 5 SECONDS", 60),          # clamped to at least a minute
        ("NEXT AVAILABLE IN 99 HOURS", 24 * 3600),    # clamped to a day
        ("no reset information", None),
    ])
    def test_reset_time_parsing(self, text, expected):
        assert _parse_quota_reset_seconds(text) == expected

    def test_labels_never_contain_url(self):
        for label in TRANSLATION_ERROR_LABELS.values():
            assert "http" not in label.lower()


class TestTranslationService:

    def test_success_and_cache(self):
        service = TranslationService()
        with patch("main._translate_text", return_value="hello") as api:
            first = service.translate("привет", "en")
            second = service.translate("привет", "en")
        assert first.ok and first.text == "hello" and first.kind == "ok"
        assert second.ok and second.text == "hello" and second.kind == "cached"
        api.assert_called_once()

    def test_cache_is_per_target_language(self):
        service = TranslationService()
        with patch("main._translate_text", side_effect=["hello", "hallo"]) as api:
            assert service.translate("привет", "en").text == "hello"
            assert service.translate("привет", "de").text == "hallo"
        assert api.call_count == 2

    def test_cache_evicts_oldest(self):
        service = TranslationService(cache_size=2)
        with patch("main._translate_text", side_effect=lambda t, *a, **k: t.upper()) as api:
            for text in ("a", "b", "c", "a"):
                service.translate(text, "en")
        assert api.call_count == 4  # "a" was evicted by "c", so it is requested again

    def test_failures_are_not_cached(self):
        service = TranslationService()
        with patch("main._translate_text", side_effect=[TranslationError("boom"), "hello"]):
            assert not service.translate("привет", "en").ok
            assert service.translate("привет", "en").text == "hello"

    @pytest.mark.parametrize("text", ["200", "+++", ":)", "...", "1 ?", "🙂👍"])
    def test_text_without_letters_is_not_sent(self, text):
        service = TranslationService()
        with patch("main._translate_text") as api:
            outcome = service.translate(text, "en")
        api.assert_not_called()
        assert outcome.ok and outcome.text == text and outcome.kind == "skipped"

    @pytest.mark.parametrize("text", ["o7", "gg", "x", "ок", "好", "1v1"])
    def test_text_with_any_letter_is_sent(self, text):
        service = TranslationService()
        with patch("main._translate_text", return_value="t") as api:
            service.translate(text, "en")
        api.assert_called_once()

    def test_quota_error_starts_pause_and_blocks_requests(self):
        clock = FakeClock()
        service = TranslationService(clock=clock)
        with patch("main._translate_text", side_effect=http_429_error(QUOTA_TEXT)) as api:
            first = service.translate("привет", "en")
            second = service.translate("как дела", "en")
        assert first.kind == "quota" and first.new_pause and not first.ok
        assert first.text == TRANSLATION_ERROR_LABELS["quota"]
        assert second.kind == "quota" and not second.new_pause and second.detail == ""
        api.assert_called_once()  # no request while paused
        assert service.paused_until == clock.now + 10 * 3600 + 32 * 60 + 50

    def test_quota_without_reset_time_uses_default_pause(self):
        clock = FakeClock()
        service = TranslationService(clock=clock)
        with patch("main._translate_text", side_effect=http_429_error()):
            service.translate("привет", "en")
        assert service.paused_until == clock.now + main._DEFAULT_QUOTA_PAUSE_SECONDS

    def test_requests_resume_after_pause(self):
        clock = FakeClock()
        service = TranslationService(clock=clock)
        with patch("main._translate_text", side_effect=[http_429_error(), "hello"]) as api:
            service.translate("привет", "en")
            clock.now += main._DEFAULT_QUOTA_PAUSE_SECONDS + 1
            outcome = service.translate("привет", "en")
        assert outcome.ok and outcome.text == "hello"
        assert api.call_count == 2

    def test_cached_translations_still_work_during_pause(self):
        service = TranslationService()
        with patch("main._translate_text", side_effect=["hello", http_429_error()]):
            service.translate("привет", "en")
            service.translate("пока", "en")  # starts the pause
            outcome = service.translate("привет", "en")
        assert outcome.ok and outcome.text == "hello"

    def test_resume_ends_pause(self):
        service = TranslationService()
        with patch("main._translate_text", side_effect=[http_429_error(), "hello"]):
            service.translate("привет", "en")
            service.resume()
            assert service.translate("привет", "en").text == "hello"

    def test_warning_returned_as_translation_is_treated_as_quota(self):
        service = TranslationService()
        with patch("main._translate_text", return_value=QUOTA_TEXT):
            outcome = service.translate("привет", "en")
        assert outcome.kind == "quota" and outcome.text == TRANSLATION_ERROR_LABELS["quota"]

    def test_empty_result_is_an_error(self):
        service = TranslationService()
        with patch("main._translate_text", return_value=""):
            outcome = service.translate("привет", "en")
        assert not outcome.ok and outcome.kind == "other"


class TestAppIntegration:

    def test_quota_shows_one_notice_and_short_labels(self, headless_app):
        app = headless_app
        app._insert_message_tab1 = MagicMock()
        with patch("main._translate_text", side_effect=http_429_error(QUOTA_TEXT)):
            first = app._translate_for_display("привет", "en")
            second = app._translate_for_display("как дела", "en")
        assert first.text == second.text == TRANSLATION_ERROR_LABELS["quota"]
        notices = [c for c in app._insert_message_tab1.call_args_list if c.args[1] == "translation_notice"]
        assert len(notices) == 1
        assert "Settings → Translation Service" in notices[0].args[0]  # no email configured
        assert app._status_shows_pause
        app.logger.error.assert_called_once()  # only the real failure is logged

    def test_pause_notice_omits_email_tip_when_email_set(self, headless_app):
        app = headless_app
        app.settings["mymemory_email"] = "player@example.com"
        app._insert_message_tab1 = MagicMock()
        with patch("main._translate_text", side_effect=http_429_error()):
            app._translate_for_display("привет", "en")
        assert "Tip:" not in app._insert_message_tab1.call_args.args[0]

    def test_status_restored_after_pause_ends(self, headless_app):
        app = headless_app
        app._insert_message_tab1 = MagicMock()
        with patch("main._translate_text", side_effect=[http_429_error(), "hello"]):
            app._translate_for_display("привет", "en")
            app.translation_service.resume()
            app._translate_for_display("привет", "en")
        assert not app._status_shows_pause
        app.status_label.configure.assert_called_with(text=main.STATUS_DEFAULT_TEXT)

    def test_manual_translate_error_is_not_copied_to_clipboard(self, headless_app):
        app = headless_app
        app.manual_entry.get.return_value = "привет"
        app._insert_message_tab1 = MagicMock()
        with patch("main._translate_text", side_effect=TranslationError("boom")), \
             patch("main.pyperclip.copy") as clipboard:
            app._manual_translate()
        clipboard.assert_not_called()
        shown = [c.args[0] for c in app._insert_message_tab1.call_args_list]
        assert "→ " + TRANSLATION_ERROR_LABELS["other"] in shown


class TestMyMemoryEmailSetting:

    @pytest.mark.parametrize("value, valid", [
        ("player@example.com", True),
        ("a.b+c@sub.domain.org", True),
        ("", False),
        ("player", False),
        ("player@", False),
        ("player@example", False),
        ("pla yer@example.com", False),
    ])
    def test_validation(self, value, valid):
        assert _is_valid_email(value) == valid

    def test_save_valid_email_persists_and_resumes(self, headless_app):
        app = headless_app
        app.mymemory_email_var.get.return_value = " player@example.com "
        app.translation_service.paused_until = 1e12
        app._save_mymemory_email()
        assert app.settings["mymemory_email"] == "player@example.com"
        assert not app.translation_service.is_paused()
        assert os.path.exists(app.settings_path)

    def test_invalid_email_is_not_saved(self, headless_app):
        app = headless_app
        app.mymemory_email_var.get.return_value = "not-an-email"
        app._save_mymemory_email()
        assert app.settings["mymemory_email"] == ""

    def test_email_is_never_logged(self, headless_app):
        app = headless_app
        app.mymemory_email_var.get.return_value = "player@example.com"
        app._save_mymemory_email()
        logged = " ".join(str(c) for c in app.logger.method_calls)
        assert "player@example.com" not in logged

    def test_clear(self, headless_app):
        app = headless_app
        app.settings["mymemory_email"] = "player@example.com"
        app._clear_mymemory_email()
        assert app.settings["mymemory_email"] == ""


class TestGameLogsLocation:

    @staticmethod
    def make_session(logs_dir, name, mtime):
        session = logs_dir / name
        session.mkdir(parents=True)
        (session / "chat.log").write_text("", encoding="utf-8")
        os.utime(session, (mtime, mtime))

    def test_default_prefers_new_location(self, headless_app, isolated_user_dirs):
        new = isolated_user_dirs / "AppData" / "Local" / "Targem" / "StarConflict" / "logs"
        legacy = isolated_user_dirs / "Documents" / "My Games" / "StarConflict" / "logs"
        new.mkdir(parents=True)
        legacy.mkdir(parents=True)
        assert headless_app._get_default_logs_path() == str(new)

    def test_default_falls_back_to_legacy(self, headless_app, isolated_user_dirs):
        legacy = isolated_user_dirs / "Documents" / "My Games" / "StarConflict" / "logs"
        legacy.mkdir(parents=True)
        assert headless_app._get_default_logs_path() == str(legacy)

    def test_default_when_nothing_exists_is_new_location(self, headless_app):
        assert headless_app._get_default_logs_path() == main._new_game_logs_path()

    def test_migrates_legacy_default_when_new_has_newer_session(self, headless_app, isolated_user_dirs):
        new = isolated_user_dirs / "AppData" / "Local" / "Targem" / "StarConflict" / "logs"
        legacy = isolated_user_dirs / "Documents" / "My Games" / "StarConflict" / "logs"
        self.make_session(legacy, "2026.10.09 11.00.54.478", 1_000)
        self.make_session(new, "2026.10.13 11.12.58.352", 2_000)
        headless_app.settings["game_logs_path"] = str(legacy)
        assert headless_app._migrate_game_logs_path() is True
        assert headless_app.settings["game_logs_path"] == str(new)

    def test_no_migration_when_legacy_is_newer(self, headless_app, isolated_user_dirs):
        new = isolated_user_dirs / "AppData" / "Local" / "Targem" / "StarConflict" / "logs"
        legacy = isolated_user_dirs / "Documents" / "My Games" / "StarConflict" / "logs"
        self.make_session(legacy, "s2", 3_000)
        self.make_session(new, "s1", 2_000)
        headless_app.settings["game_logs_path"] = str(legacy)
        assert headless_app._migrate_game_logs_path() is False
        assert headless_app.settings["game_logs_path"] == str(legacy)

    def test_custom_path_is_never_changed(self, headless_app, isolated_user_dirs, tmp_path):
        new = isolated_user_dirs / "AppData" / "Local" / "Targem" / "StarConflict" / "logs"
        self.make_session(new, "s1", 2_000)
        custom = tmp_path / "my_logs"
        custom.mkdir()
        headless_app.settings["game_logs_path"] = str(custom)
        assert headless_app._migrate_game_logs_path() is False
        assert headless_app.settings["game_logs_path"] == str(custom)

    def test_no_migration_when_new_location_has_no_sessions(self, headless_app, isolated_user_dirs):
        new = isolated_user_dirs / "AppData" / "Local" / "Targem" / "StarConflict" / "logs"
        legacy = isolated_user_dirs / "Documents" / "My Games" / "StarConflict" / "logs"
        new.mkdir(parents=True)
        self.make_session(legacy, "s1", 1_000)
        headless_app.settings["game_logs_path"] = str(legacy)
        assert headless_app._migrate_game_logs_path() is False


class TestRemoteContentOnGitHub:

    REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")

    def test_default_urls_point_to_github_repository(self):
        for url in (main.DEFAULT_REMOTE_WELCOME_URL, main.DEFAULT_REMOTE_DICTIONARY_URL):
            assert url.startswith("https://raw.githubusercontent.com/jacek-mar/star-conflict-chat-translator/main/")
            assert "jsonsilo" not in url

    def test_remote_files_exist_in_repository_and_are_valid(self):
        import json
        base = main.REMOTE_CONTENT_BASE_URL + "/"
        for url in (main.DEFAULT_REMOTE_WELCOME_URL, main.DEFAULT_REMOTE_DICTIONARY_URL):
            path = os.path.join(self.REPO_ROOT, url[len(base):])
            with open(path, encoding="utf-8") as f:
                assert json.load(f)

    def test_welcome_json_has_fields_the_app_reads(self):
        import json
        with open(os.path.join(self.REPO_ROOT, "remote", "welcome.json"), encoding="utf-8") as f:
            data = json.load(f)
        assert data["welcome_message"].strip()
        assert int(data["id"]) > 3  # newer than the last jsonsilo id ("003")
        assert main.compare_versions(data["version"], main.APP_VERSION) <= 0  # never announce an unreleased version
        assert isinstance(data["whats_new"]["changes"], list)

    def _load_with(self, headless_app, saved):
        import json
        with open(headless_app.settings_path, "w", encoding="utf-8") as f:
            json.dump(saved, f)
        return headless_app._load_settings()

    def test_legacy_jsonsilo_dictionary_url_is_migrated(self, headless_app):
        settings = self._load_with(headless_app, {"remote_dictionary_url": main.LEGACY_REMOTE_DICTIONARY_URLS[0]})
        assert settings["remote_dictionary_url"] == main.DEFAULT_REMOTE_DICTIONARY_URL

    def test_custom_dictionary_url_is_kept(self, headless_app):
        custom = "https://example.com/my_dictionary.json"
        settings = self._load_with(headless_app, {"remote_dictionary_url": custom})
        assert settings["remote_dictionary_url"] == custom
