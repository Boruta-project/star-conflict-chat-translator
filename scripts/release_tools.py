"""Release helpers used by .github/workflows/release.yml (also usable locally).

    python scripts/release_tools.py check-version v1.4.0
        Fails unless the tag, APP_VERSION in main.py, the version in pyproject.toml
        and a "## [1.4.0]" section in CHANGELOG.md all agree.

    python scripts/release_tools.py notes 1.4.0 dist/release-notes.md
        Writes that CHANGELOG section as release notes, with links made absolute.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO_BLOB = "https://github.com/jacek-mar/star-conflict-chat-translator/blob/main/"


def versions():
    main_py = (ROOT / "main.py").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    return (
        re.search(r'^APP_VERSION = "([^"]+)"', main_py, re.M).group(1),
        re.search(r'^version = "([^"]+)"', pyproject, re.M).group(1),
    )


def changelog_section(version):
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    m = re.search(rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else None


def check_version(tag):
    version = tag.lstrip("v")
    app, project = versions()
    problems = []
    if app != version:
        problems.append(f"main.py APP_VERSION is {app}, tag is {tag}")
    if project != version:
        problems.append(f"pyproject.toml version is {project}, tag is {tag}")
    if not changelog_section(version):
        problems.append(f"CHANGELOG.md has no '## [{version}]' section")
    if problems:
        sys.exit("Version check failed:\n- " + "\n- ".join(problems))
    print(f"Version {version}: main.py, pyproject.toml and CHANGELOG.md agree")


def notes(version, out):
    section = changelog_section(version)
    if section is None:
        sys.exit(f"CHANGELOG.md has no '## [{version}]' section")
    # Relative links in CHANGELOG.md point into the repository
    section = re.sub(r"\]\((?!https?://|#)([^)]+)\)", rf"]({REPO_BLOB}\1)", section)
    exe = f"SC_Chat_Translator_v{version}_Windows.exe"
    section += (
        "\n\n### Download\n"
        f"- **Windows**: `{exe}` (single file, no installation needed). "
        "Settings, chat history and the game dictionary from earlier versions are kept.\n"
        "- `SHA256SUMS.txt`: checksum to verify the download.\n"
    )
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(section + "\n", encoding="utf-8")
    print(f"Release notes written to {out}")


def main(argv):
    if len(argv) == 2 and argv[0] == "check-version":
        check_version(argv[1])
    elif len(argv) == 3 and argv[0] == "notes":
        notes(argv[1], argv[2])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
