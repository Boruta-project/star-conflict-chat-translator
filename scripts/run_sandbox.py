"""
Run the app against a throw-away copy of your data, so testing never changes your real
settings, chat history or game logs.

    venv\\Scripts\\python scripts\\run_sandbox.py --app-data <copy of ScTranslationApp> \\
        --game-data <copy of Targem\\StarConflict> [--legacy-logs] [--local-remote] [--fresh]

  --app-data      folder with settings.json / database / game_dictionary.json
                  (default: start with no settings, like a new install)
  --game-data     Star Conflict folder containing logs\\ (placed at the new location,
                  %LOCALAPPDATA%\\Targem\\StarConflict)
  --legacy-logs   point settings at the old Documents\\My Games path, to test the
                  automatic switch to the new folder
  --local-remote  serve remote\\welcome.json and game_dictionary.json from this checkout
                  (http://localhost:8765) instead of GitHub — for testing before a push
  --fresh         delete the previous sandbox first

While the app runs, simulate chat by appending lines to the newest chat.log, e.g.:
    12:00:00.000     CHAT| <        #trading>[ Tester] Привет всем
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SANDBOX = REPO / ".sandbox"   # git-ignored
REMOTE_PORT = 8765


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--app-data", type=Path)
    parser.add_argument("--game-data", type=Path)
    parser.add_argument("--legacy-logs", action="store_true")
    parser.add_argument("--local-remote", action="store_true")
    parser.add_argument("--fresh", action="store_true")
    args = parser.parse_args()

    home = SANDBOX / "home"
    local_appdata = home / "AppData" / "Local"
    if args.fresh and SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    local_appdata.mkdir(parents=True, exist_ok=True)

    app_dir = local_appdata / "ScTranslationApp"
    if args.app_data and not app_dir.exists():
        shutil.copytree(args.app_data, app_dir)

    new_game_dir = local_appdata / "Targem" / "StarConflict"
    if args.game_data and not new_game_dir.exists():
        shutil.copytree(args.game_data, new_game_dir)

    settings_path = app_dir / "settings.json"
    if settings_path.exists():
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        if args.legacy_logs:
            legacy = home / "Documents" / "My Games" / "StarConflict" / "logs"
            old_session = legacy / "2000.01.01 00.00.00.000"
            old_session.mkdir(parents=True, exist_ok=True)
            (old_session / "chat.log").touch()
            os.utime(old_session, (946684800, 946684800))  # older than any real session
            settings["game_logs_path"] = str(legacy)
        else:
            settings["game_logs_path"] = str(new_game_dir / "logs")
        settings["last_remote_fetch"] = 0  # fetch remote content on this start
        settings_path.write_text(json.dumps(settings, indent=4), encoding="utf-8")

    env = dict(os.environ, USERPROFILE=str(home), HOME=str(home), LOCALAPPDATA=str(local_appdata))
    server = None
    if args.local_remote:
        server = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(REMOTE_PORT), "--bind", "127.0.0.1"],
            cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        env["SC_TRANSLATOR_REMOTE_BASE"] = f"http://127.0.0.1:{REMOTE_PORT}"

    print(f"Sandbox profile: {home}")
    print(f"App log:         {app_dir / 'logs' / 'app.log'}")
    try:
        subprocess.run([sys.executable, str(REPO / "main.py")], cwd=REPO, env=env)
    finally:
        if server:
            server.terminate()


if __name__ == "__main__":
    main()
