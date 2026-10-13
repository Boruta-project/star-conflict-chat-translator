"""Build the Windows exe and check that it starts.

Usage (from the project root, in an environment with requirements-lock.txt and
requirements-build.txt installed):

    python scripts/build_exe.py

Steps:
1. PyInstaller builds dist/SC_Chat_Translator_v<version>_Windows.exe from
   packaging/sc_chat_translator.spec (version = APP_VERSION in main.py).
2. The exe is started with `--smoke-test` and with Python removed from PATH, as on a
   player's PC. It must load its bundled files and libraries and open a Tk window.
3. dist/SHA256SUMS.txt is written for the release page.

The same script runs locally and in GitHub Actions, so a local build is what CI builds.
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
WORK = ROOT / "build_pyinstaller"
SPEC = ROOT / "packaging" / "sc_chat_translator.spec"


def app_version():
    text = (ROOT / "main.py").read_text(encoding="utf-8")
    return re.search(r'^APP_VERSION = "([^"]+)"', text, re.M).group(1)


def build():
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
         "--distpath", str(DIST), "--workpath", str(WORK), str(SPEC)],
        cwd=ROOT, check=True,
    )


def smoke_test(exe):
    """Run the exe the way a player would: no Python on PATH, fresh user profile."""
    with tempfile.TemporaryDirectory() as tmp:
        env = dict(os.environ)
        env["PATH"] = os.pathsep.join(
            p for p in env.get("PATH", "").split(os.pathsep) if "python" not in p.lower()
        )
        home = Path(tmp) / "home"
        (home / "AppData" / "Local").mkdir(parents=True)
        env.update(USERPROFILE=str(home), HOME=str(home),
                   LOCALAPPDATA=str(home / "AppData" / "Local"))
        report = Path(tmp) / "smoke.txt"
        result = subprocess.run([str(exe), "--smoke-test", str(report)],
                                env=env, timeout=180)
        text = report.read_text(encoding="utf-8").strip() if report.exists() else "(no report)"
    print(f"Smoke test: {text}")
    if result.returncode != 0:
        sys.exit(f"Smoke test failed (exit code {result.returncode})")


def write_checksums(files):
    lines = []
    for f in files:
        digest = hashlib.sha256(f.read_bytes()).hexdigest()
        lines.append(f"{digest}  {f.name}")
    # LF line endings, so `sha256sum -c SHA256SUMS.txt` also works on Linux/Git Bash
    (DIST / "SHA256SUMS.txt").write_bytes(("\n".join(lines) + "\n").encode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skip-build", action="store_true",
                        help="only smoke-test an exe that is already in dist/")
    args = parser.parse_args()

    if sys.platform != "win32":
        sys.exit("The release exe is built on Windows only.")

    exe = DIST / f"SC_Chat_Translator_v{app_version()}_Windows.exe"
    if not args.skip_build:
        build()
    if not exe.exists():
        sys.exit(f"Expected {exe} was not produced")
    smoke_test(exe)
    write_checksums([exe])
    print(f"Built {exe.relative_to(ROOT)} ({exe.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
