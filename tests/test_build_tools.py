"""Tests for the build/release tooling: the exe smoke test and scripts/release_tools.py."""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import main  # noqa: E402
import release_tools  # noqa: E402


class TestSmokeTest:
    def test_reports_missing_bundled_files(self, monkeypatch, tmp_path):
        monkeypatch.setattr(main, "resource_path", lambda rel: str(tmp_path / rel))
        problems = main.smoke_test()
        for rel in main.SMOKE_TEST_FILES:
            assert f"missing bundled file: {rel}" in problems

    def test_main_exits_nonzero_and_writes_report_on_failure(self, monkeypatch, tmp_path):
        report = tmp_path / "smoke.txt"
        monkeypatch.setattr(main, "smoke_test", lambda: ["missing bundled file: x"])
        monkeypatch.setattr(sys, "argv", ["main.py", "--smoke-test", str(report)])
        with pytest.raises(SystemExit) as exc:
            main.main()
        assert exc.value.code == 1
        assert "missing bundled file: x" in report.read_text(encoding="utf-8")

    def test_main_exits_zero_when_ok(self, monkeypatch, tmp_path):
        report = tmp_path / "smoke.txt"
        monkeypatch.setattr(main, "smoke_test", lambda: [])
        monkeypatch.setattr(sys, "argv", ["main.py", "--smoke-test", str(report)])
        with pytest.raises(SystemExit) as exc:
            main.main()
        assert exc.value.code == 0
        assert report.read_text(encoding="utf-8").strip().endswith(": OK")


class TestReleaseTools:
    def test_current_versions_agree(self):
        app, project = release_tools.versions()
        assert app == project == main.APP_VERSION
        release_tools.check_version(f"v{app}")  # must not exit

    def test_check_version_rejects_mismatched_tag(self):
        with pytest.raises(SystemExit) as exc:
            release_tools.check_version("v0.0.1")
        assert "APP_VERSION" in str(exc.value)

    def test_notes_use_changelog_section_with_absolute_links(self, tmp_path):
        out = tmp_path / "notes.md"
        release_tools.notes(main.APP_VERSION, str(out))
        text = out.read_text(encoding="utf-8")
        assert f"SC_Chat_Translator_v{main.APP_VERSION}_Windows.exe" in text
        assert "](docs/" not in text  # relative links were made absolute
