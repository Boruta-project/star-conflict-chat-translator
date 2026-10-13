# PyInstaller spec for SC Chat Translator — the only build definition.
# Build with:  python scripts/build_exe.py   (wraps PyInstaller and smoke-tests the exe)
# The version comes from APP_VERSION in main.py, so the file name always matches.
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))

with open(os.path.join(ROOT, "main.py"), encoding="utf-8") as f:
    VERSION = re.search(r'^APP_VERSION = "([^"]+)"', f.read(), re.M).group(1)

NAME = f"SC_Chat_Translator_v{VERSION}_Windows"

binaries = []
# python3x.dll needs vcruntime140_1.dll, which PyInstaller does not always pick up;
# without it the exe fails on PCs without Python (docs/building-executables.md).
vcruntime = os.path.join(sys.base_prefix, "vcruntime140_1.dll")
if os.path.isfile(vcruntime):
    binaries.append((vcruntime, "."))

a = Analysis(
    [os.path.join(ROOT, "main.py")],
    pathex=[ROOT],
    binaries=binaries,
    datas=[
        (os.path.join(ROOT, "assets"), "assets"),
        (os.path.join(ROOT, "game_dictionary.json"), "."),
    ],
    hiddenimports=[],
    excludes=["pytest", "_pytest", "matplotlib", "numpy"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=NAME,
    icon=os.path.join(ROOT, "assets", "logo.ico"),
    console=False,
    upx=False,
)
