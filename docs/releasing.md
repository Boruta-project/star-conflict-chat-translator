# Releasing a New Version

Releases are built by GitHub Actions (`.github/workflows/release.yml`) when a version tag
is pushed. The workflow creates a **draft** release; nothing is public until you publish it.

## 1. Prepare

1. Set the new version in **both** places:
   - `APP_VERSION` in `main.py`
   - `version` in `pyproject.toml`
2. In `CHANGELOG.md`, rename `## [Unreleased]` to `## [1.4.1] - YYYY-MM-DD` (your version
   and date). This section becomes the release notes.
3. If the release has news for players, update `remote/welcome.json` (see `remote/README.md`).
4. Check locally:

   ```bash
   python scripts/release_tools.py check-version v1.4.1
   pytest
   ```

5. Commit and push to `main`. Wait for **Tests and build** to pass on GitHub.

## 2. Tag

```bash
git tag -a v1.4.1 -m "SC Chat Translator 1.4.1"
git push origin v1.4.1
git push upstream main v1.4.1     # keep Boruta-project in sync
```

## 3. Publish

The **Release** workflow:

1. stops if the tag, `main.py`, `pyproject.toml` and `CHANGELOG.md` disagree;
2. runs all tests (Windows and Ubuntu, Python 3.10–3.14);
3. builds the exe and smoke-tests it without Python on `PATH`;
4. creates a draft release with the exe, `SHA256SUMS.txt` and the CHANGELOG section.

Open **Releases**, check the draft (you can download the exe and try it), then click
**Publish release**.

## If something fails

- **Version check failed**: fix the version or CHANGELOG, commit, then move the tag:
  `git tag -fa v1.4.1 -m "..."` and `git push -f origin v1.4.1`. This is only safe
  before the release is published.
- **Tests or smoke test failed**: fix on `main` and move the tag the same way.
- You can also rebuild a draft for an existing tag: **Actions → Release → Run workflow**,
  enter the tag. Note that the tests in that run use the selected branch.

## Building without GitHub

`python scripts/build_exe.py` produces the same exe locally
([building-executables.md](building-executables.md)); upload it to a release by hand.
