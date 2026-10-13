# Building the Windows Executable

The app is released as a single Windows file: `SC_Chat_Translator_v<version>_Windows.exe`.
It is built from one definition, [`packaging/sc_chat_translator.spec`](../packaging/sc_chat_translator.spec),
by one script, [`scripts/build_exe.py`](../scripts/build_exe.py). GitHub Actions runs the same
script, so a local build and a CI build are made the same way.

## Build

From the project root, on Windows, in a virtual environment with **Python 3.12**
(the version releases are built with):

```bash
pip install -r requirements-lock.txt -r requirements-build.txt
python scripts/build_exe.py
```

Output in `dist/`:

| File | |
|---|---|
| `SC_Chat_Translator_v<version>_Windows.exe` | the app; `<version>` is `APP_VERSION` from `main.py` |
| `SHA256SUMS.txt` | checksum for the release page |

Work files go to `build_pyinstaller/`. Both folders are git-ignored.

## What the script checks

After building, the script starts the exe with `--smoke-test`:

- **with Python removed from `PATH`** and a temporary, empty user profile, as on a
  player's PC;
- the exe checks that its bundled files exist (`assets/`, `game_dictionary.json`), that the
  libraries load (CustomTkinter, Pillow, `translate`), and that it can open a Tk window;
- it uses no network and does not touch real settings;
- a non-zero exit code fails the build.

You can run the same check on any build: `SC_Chat_Translator_v1.4.0_Windows.exe --smoke-test report.txt`.

## Why the build is pinned

Earlier releases broke because library versions changed underneath the build
(`googletrans` versions, Google's endpoint changes). Now:

- `requirements-lock.txt` pins every runtime library to a tested version;
- `requirements-build.txt` pins PyInstaller;
- the weekly **Dependency check** workflow tests the newest library versions separately,
  so a breaking library release shows up there first, not in a release.

## The `vcruntime140_1.dll` detail

`python3xx.dll` needs two Visual C++ runtime DLLs: `vcruntime140.dll` and
`vcruntime140_1.dll`. PyInstaller does not always bundle the second one, and the exe then
fails on PCs without Python (`LoadLibrary: The specified module could not be found`),
while still working on the developer's PC. The spec file adds it from the Python
installation explicitly, and the smoke test (without Python on `PATH`) catches it if it
is ever missing again.

## Only Windows

Star Conflict players on Linux or macOS run the app from source
([installation.md](installation.md)); CI runs the tests on Ubuntu as well.
