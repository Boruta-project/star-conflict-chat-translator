# Building Windows Executables (One-Folder and One-File)

This guide covers building standalone Windows executables of the app with PyInstaller, in both distribution modes, plus a real gotcha you will hit if you skip the DLL step below.

## One-folder vs. one-file

| | One-folder (`--onedir`) | One-file (`--onefile`) |
|---|---|---|
| Output | A folder containing the `.exe` plus an `_internal/` directory | A single `.exe` |
| Startup speed | Fast — files are already on disk | Slower — it extracts itself to a temp folder on every launch |
| Distribution | Must ship the whole folder together | Just one file to send around |
| Best for | Normal use, faster iteration while testing | Quick sharing, USB sticks, "just one file" requests |

Both modes produce the same app; pick based on how it'll be distributed.

## Prerequisites

From the project root, with the project's virtual environment active:

```bash
pip install -r requirements.txt
pip install -r requirements-build.txt
```

`requirements-build.txt` includes `pyinstaller`. Confirm it's available:

```bash
python -m PyInstaller --version
```

## The `vcruntime140_1.dll` gotcha (read this before building)

PyInstaller's dependency scanner does not reliably detect that `python311.dll` (or whichever Python 3.x you're building with) depends on **two** Visual C++ runtime DLLs, not one: `vcruntime140.dll` and `vcruntime140_1.dll`. It bundles the first automatically but often misses the second.

**Symptom if you skip this**: the built exe fails to start with an error like:

```
_internal\python311.dll
LoadLibrary: The specified module could not be found
```

This will pass silently if you test on the same machine that has Python installed system-wide with that DLL on `PATH` — the exe will appear to work for you and fail for anyone else. **Always test with a clean `PATH`** (see [Verifying the build](#verifying-the-build) below) rather than trusting a quick local run.

**Fix**: explicitly bundle the missing DLL. Find your Python installation's copy — same folder as `python.exe`:

```powershell
# Windows: locate it
Get-ChildItem "$(python -c 'import sys; print(sys.base_prefix)')\vcruntime140_1.dll"
```

Pass it to PyInstaller with `--add-binary "<full path to vcruntime140_1.dll>;."` in both commands below. The example commands already include this — just update the path if your Python installation lives somewhere else.

## Building the one-folder version

From the project root:

```bash
python -m PyInstaller ^
  --windowed ^
  --onedir ^
  --noconfirm ^
  --name "SC_Chat_Translator_v1.4.0_Windows" ^
  --icon "assets\logo.ico" ^
  --add-data "assets;assets" ^
  --add-data "game_dictionary.json;." ^
  --add-binary "C:\Users\<you>\AppData\Local\Programs\Python\Python311\vcruntime140_1.dll;." ^
  --distpath "dist" ^
  --specpath "build_pyinstaller" ^
  --workpath "build_pyinstaller" ^
  main.py
```

(`^` is the Windows `cmd` line-continuation character; if using PowerShell or a POSIX shell, replace with a backtick or backslash respectively, or put it all on one line.)

**Output**: `dist/SC_Chat_Translator_v1.4.0_Windows/` — contains the `.exe` and an `_internal/` folder. Distribute the whole folder; the `.exe` alone will not run.

## Building the one-file version

Identical command, with `--onedir` replaced by `--onefile`:

```bash
python -m PyInstaller ^
  --windowed ^
  --onefile ^
  --noconfirm ^
  --name "SC_Chat_Translator_v1.4.0_Windows" ^
  --icon "assets\logo.ico" ^
  --add-data "assets;assets" ^
  --add-data "game_dictionary.json;." ^
  --add-binary "C:\Users\<you>\AppData\Local\Programs\Python\Python311\vcruntime140_1.dll;." ^
  --distpath "dist" ^
  --specpath "build_pyinstaller" ^
  --workpath "build_pyinstaller" ^
  main.py
```

**Output**: `dist/SC_Chat_Translator_v1.4.0_Windows.exe` — a single file, safe to run alongside the one-folder build (different filename, no conflict).

Note: when it runs, you'll see two processes in Task Manager under this name — a small bootloader process and the actual extracted app. This is normal onefile behavior, not a bug.

## Verifying the build

Don't just double-click it on your dev machine and call it done — that machine already has everything the exe needs available globally, which can hide missing-dependency bugs (exactly what happened with `vcruntime140_1.dll` above). Test one of:

- Run it on a different machine or a fresh user account without Python installed.
- Or, on your own machine, temporarily strip your Python installation from `PATH` for the test (PowerShell):
  ```powershell
  $exe = "dist\SC_Chat_Translator_v1.4.0_Windows.exe"   # or the one-folder .exe
  $original = $env:Path
  $env:Path = ($original -split ';' | Where-Object { $_ -notlike '*Python*' }) -join ';'
  Start-Process $exe
  # ... check it opens correctly ...
  $env:Path = $original
  ```

If it fails to start, note the exact error — DLL loading errors almost always name the specific `.dll` that's missing, which tells you what to add via `--add-binary`.

## Cleaning up

Build artifacts are already covered by `.gitignore` (`build/`, `dist/`, `*.spec`) and safe to delete freely between builds:

```bash
rm -rf dist build_pyinstaller
```

(The project also has a separate `build/` folder containing maintained `.spec` files and older automation scripts (`build/build.py`, `build/build_windows.spec`, `scripts/build.py`) — those currently reference an older version string and were not used for the commands above. This guide's commands are the current, verified path; treat the older scripts as a future cleanup item if you want a single source of truth.)

## Other platforms

The commands above are Windows-specific (`;` as the `--add-data`/`--add-binary` separator, `.ico` icon). On Linux/macOS:
- Use `:` instead of `;` as the separator.
- macOS needs a `.icns` icon instead of `.ico`.
- The `vcruntime140_1.dll` issue is Windows-only (it's a Visual C++ runtime file) — not applicable on Linux/macOS.

See `build/build_linux.spec` and `build/build_macos.spec` for platform-specific spec files (unverified as part of this guide — apply the same "test with a clean environment" principle before trusting them).
