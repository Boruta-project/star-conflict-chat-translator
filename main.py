import sys, os
import time
import threading
import tkinter as tk
import customtkinter as ctk
from PIL import Image
import json
import logging
from logging.handlers import RotatingFileHandler
from translate import Translator as MyMemoryTranslator
from translate.exceptions import TranslationError
from pathlib import Path
from tkinter import filedialog
from datetime import datetime
import re
import sqlite3
import csv
import pyperclip  # copy translated user entry to clipboard
import webbrowser  # for opening links
import requests  # used by `translate`; needed here to recognise network errors
from collections import OrderedDict
from typing import NamedTuple

# --- Libraries for HTTP fetch ---
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# -----------------------
# Global configuration
# -----------------------

APP_VERSION = "1.4.0"
APP_AUTHOR = "Hystrix"
AUTHOR_EMAIL = "borutaproject@gmail.com"

# Default application window geometry
DEFAULT_WINDOW_WIDTH = 480
DEFAULT_WINDOW_HEIGHT = 536

BUTTON_HEIGHT = 20

# App-wide font sizes — help section uses its own (not reduced)
APP_FONT_SIZE = 11        # body: labels, entries, buttons
APP_FONT_SIZE_SMALL = 9   # hints and captions
APP_FONT_SIZE_GROUP = 12  # settings group headings (regular weight, as in 1.1.3)

# Help window dimensions (relative to main window)
HELP_WINDOW_WIDTH_RATIO = 0.8  # 80% of main window width
HELP_WINDOW_HEIGHT_RATIO = 1.0  # 100% of main window height

# Status bar layout ratios
STATUS_LABEL_RATIO = 0.9  # 90% for status label
HELP_BUTTON_RATIO = 0.1   # 10% for help button

# Link styling
LINK_COLOR = "#4A90E2"  # Blue for clickable links
LINK_CURSOR = "hand2"   # Hand cursor for links

# Help content styling (kept at comfortable reading size — not reduced)
HELP_SECTION_SPACING = 7   # Spacing between sections
HELP_CONTENT_PADDING = 10  # Padding for content areas

# GUI configuration
GUI_RESIZABLE = True   # Window is resizable; minimum size enforced in __init__

# UI size presets — controls fonts and window dimensions; applied live via _apply_ui_preset()
UI_PRESETS = {
    "Small":  {"font": 11, "font_small": 9,  "font_group": 12,
               "width": 480, "height": 536, "tab_w": 95,  "tab_h": 18},
    "Medium": {"font": 12, "font_small": 10, "font_group": 13,
               "width": 560, "height": 640, "tab_w": 110, "tab_h": 20},
    "Large":  {"font": 13, "font_small": 11, "font_group": 14,
               "width": 640, "height": 720, "tab_w": 125, "tab_h": 22},
}
UI_PRESET_DEFAULT = "Small"

# Project links
PROJECT_REPOSITORY_URL = "https://github.com/jacek-mar/star-conflict-chat-translator"

# Remote welcome message and community dictionary are plain files in the repository's
# main branch (see remote/README.md); edits reach users after a push, within the
# remote_fetch_interval (1 hour) plus GitHub's raw-file cache (~5 minutes).
# SC_TRANSLATOR_REMOTE_BASE overrides it for testing (see scripts/run_sandbox.py).
REMOTE_CONTENT_BASE_URL = os.environ.get(
    "SC_TRANSLATOR_REMOTE_BASE",
    "https://raw.githubusercontent.com/jacek-mar/star-conflict-chat-translator/main",
).rstrip("/")
DEFAULT_REMOTE_WELCOME_URL = f"{REMOTE_CONTENT_BASE_URL}/remote/welcome.json"
DEFAULT_REMOTE_DICTIONARY_URL = f"{REMOTE_CONTENT_BASE_URL}/game_dictionary.json"
# Former jsonsilo.com endpoints (≤ v1.3.0); saved settings pointing here are migrated.
LEGACY_REMOTE_DICTIONARY_URLS = (
    "https://api.jsonsilo.com/public/245adbbb-9613-47ab-96bb-0e3e40385700",
)
USER_MANUAL_URL = f"{PROJECT_REPOSITORY_URL}/blob/main/docs/user-guide.md"
TRANSLATION_SERVICE_INFO_URL = f"{PROJECT_REPOSITORY_URL}/blob/main/docs/translation-service.md"
RELEASES_URL = f"{PROJECT_REPOSITORY_URL}/releases"
ISSUES_URL = f"{PROJECT_REPOSITORY_URL}/issues"

DEFAULT_SETTINGS = {
    "last_language": "English",
    "manual_translate_lang": "ru",
    # Optional, empty by default (anonymous MyMemory quota: 5,000 chars/day). Setting a
    # personal email (Settings → Translation Service) raises it to 50,000 chars/day —
    # see docs/design-translate-library-migration.md. Never hard-code a shared email;
    # each user should use their own, or none.
    "mymemory_email": "",
    # Channels NOT translated (opt-out list: empty = translate all, new channels are on)
    "untranslated_channels": [],
    "languages": {
        "English": "en",
        "Spanish": "es",
        "French": "fr",
        "German": "de",
        "Italian": "it",
        "Polish": "pl",
        "Portuguese": "pt",
        "Russian": "ru",
        "Japanese": "ja",
        "Chinese (Simplified)": "zh-cn",
        "Arabic": "ar",
        "Hindi": "hi"
    },
    "manual_languages": {
        "EN": "en",
        "ES": "es",
        "FR": "fr",
        "DE": "de",
        "IT": "it",
        "PL": "pl",
        "PT": "pt",
        "RU": "ru",
        "JA": "ja",
        "ZH": "zh-cn",
        "AR": "ar",
        "HI": "hi"
    },
    "game_logs_path": None,   # Will be filled at runtime
    "welcome_counter": 0,
    "welcome_message_color": "DodgerBlue",
    "remote_welcome_id": "0000",
    "app_version": APP_VERSION,
    "allow_remote_dictionary": False,
    "remote_dictionary_url": DEFAULT_REMOTE_DICTIONARY_URL,
    "remote_dictionary_overrides_local": False,  # when True remote entries replace local ones on conflict
    "remote_dict_version": "",  # last fetched remote dict version/etag for conditional fetch
    "last_notified_version": APP_VERSION,
    "last_remote_fetch": 0,
    "remote_fetch_interval": 3600,  # 1 hour in seconds
    "show_extended_welcome": False,  # Flag to show extended message after version update
    # Extended welcome message fields (populated from remote)
    "remote_welcome_message": "",
    "remote_whats_new": None,
    "remote_download_url": "",
    "remote_notes": "",
    "ui_preset": "Small",       # UI size preset: Small / Medium / Large
}

STATUS_DEFAULT_TEXT = "Processing chat.log..."
STATUS_NO_CHAT_LOG_TEXT = "Waiting for chat.log – check the logs folder in Settings"

MANUAL_TRANSLATE_LANG = "ru"  # Temporary, example: Spanish
MANUAL_TRANSLATE_PROMPT = "Want to translate something?"

# --- Chat categories/patterns to keep ---
CHAT_CATEGORIES = {
    "#trading>[": "Trading",
    "#general_ENGLISH>[": "English",
    "#general_RUSSIAN>[": "Russian",
    "#general_CHINESE>[": "Chinese",
    "#general_GERMAN>[": "German",
    "#general_ITALIAN>[": "Italian",
    "#general_FRENCH>[": "French",
    "#general_SPANISH>[": "Spanish",
    "#general_JAPANESE>[": "Japanese",
    "#general_PORTUGUESE>[": "Portuguese",
    "#general_TURKISH>[": "Turkish",
    "##general_POLISH>[": "Polish",
    "##general_HUNGARIAN>[": "Hungarian",
    "#general_CZECH>[": "Czech",
    "#general_UKRAINIAN>[": "Ukrainian",
    "#battle_": "Battle",
    "#squad_": "Squad",
    "#clan_": "Clan",
    "PRIVATE From": "Priv_from",
    "PRIVATE To": "Priv_to",
}

COLOR_CATEGORIES = {
    "Trading": "lightgrey",
    "English": "lightblue",
    "Russian": "lightblue",
    "Chinese": "lightblue",
    "German": "lightblue",
    "Italian": "lightblue",
    "French": "lightblue",
    "Spanish": "lightblue",
    "Japanese": "lightblue",
    "Portuguese": "lightblue",
    "Turkish": "lightblue",
    "Polish": "lightblue",
    "Hungarian": "lightblue",
    "Czech": "lightblue",
    "Ukrainian": "lightblue",
    "Battle": "CornflowerBlue",
    "Squad": "DarkOrange",
    "Clan": "LimeGreen",
    "Priv_from": "MediumOrchid",
    "Priv_to": "MediumOrchid",
}

# Channels that can be excluded from translation (Settings → Translated Channels).
# Names are CHAT_CATEGORIES values. Unticked channels are still displayed and saved;
# only the translation request is skipped.
CHANNEL_GROUPS = (
    ("Channels", ("Battle", "Squad", "Clan", "Trading", "Priv_from", "Priv_to")),
    ("General chats", ("English", "Russian", "Chinese", "German", "Italian", "French",
                       "Spanish", "Japanese", "Portuguese", "Turkish", "Polish",
                       "Hungarian", "Czech", "Ukrainian")),
)
CHANNEL_LABELS = {"Priv_from": "Private (received)", "Priv_to": "Private (sent)"}

# Colors used to highlight different languages in the chat
LANGUAGE_COLORS = [
    "lightgreen", "darkblue", "purple", "brown",
    "teal", "darkred", "orange", "navy",
    "maroon", "darkmagenta", "darkcyan", "olive"
]

# Default color for welcome message (if no remote override)
DEFAULT_WELCOME_COLOR = "DodgerBlue"

# Strings that indicate system/technical lines we don't want to display.
SKIP_PATTERNS = [
    "CHAT| Join channel",
    "CHAT| Leave channel",
    "CHAT| Channel created",
    "CHAT| Channel destroyed",
    "CHAT| System",
]

# Default local dictionary used if the user's game_dictionary.json is missing or empty.
DEFAULT_DICTIONARY = {
    "xpam": "temple",
    "cnc": "thank you",
    "co+": "spec ops +",
    "Co+": "spec ops +",
    "[Link 2 D: Ship_race3_m_t5_craftuniq]": "[Tornado]",
    "[Link 2 D: Ship_race3_L_T5_PREMIUM]": "[Mammoth]",
    "[link 2 d:Ship_Race3_M_T5_CraftUniq]": "[Tornado]",
    "[link 2 d:Ship_Race3_L_T5_Premium]": "[Mammoth]",
    "[link 11 d:Relics_craft_part]": "[Synthetic polycrystal]",
    "[link 11 d:pve_resource]": "[Insignia]",
    "[link 2 d:Ship_Race5_L_ENGINEER_Rank8]": "[Waz'Got]",
    "со+": "spec ops+",
    "[LINK 1 D: Weapon_Corrosivegun_T5_Rel]": "[Tai'thaq 17]",
    "[link 1 d:Weapon_CorrosiveGun_T5_Rel]": "[Tai'thaq 17]",
    "[link 11 d:Ship_Race2_S_T5_Uniq_part]": "[Special part of the ship “Kusarigama”]"
}

# Fallback welcome text (shown if remote welcome is unavailable)
DEFAULT_WELCOME_TEXT = (
    "This tool helps translate and manage in-game chat messages.\n"
    "It was created to improve the game experience for players from different countries.\n"
    "It is still in development and may contain minor bugs. Released under the MiT license. \n"
    "The application uses a free translation service and does not interfere with the game code.\n"
    "Check your preferences in the Settings tab.\n\n"
    "Feel free to share your feedback about this program with me.\n"
    )

# EXPERIMENTAL (see docs/design-translate-library-migration.md): translation runs
# through the `translate` package's MyMemory backend rather than Google. Google's free
# scraping endpoints started blocking automated queries platform-wide in September 2026,
# and deep-translator (the previous backend) is dormant with no fix. MyMemory is a
# separate, independent service unaffected by that. Its own free-tier limits: ~500
# chars/request, 5,000 chars/day anonymous (raised to 50,000/day with a registered
# email — see the optional "mymemory_email" setting; never hard-code an email here, as
# that would make every install of this app share one pool). from_lang="autodetect" is
# MyMemory's own real (server-verified) auto-detect sentinel — not "auto".
_MYMEMORY_AUTODETECT = "autodetect"

# MyMemory doesn't publish a hard per-second cap the way Google's endpoint did, but
# spacing calls out is still cheap, good API etiquette, and covers every call site
# (main-thread startup sequence and the background chat-watch loop alike) with one
# mechanism.
_translate_lock = threading.Lock()
_last_translate_call_ts = 0.0
_MIN_SECONDS_BETWEEN_TRANSLATE_CALLS = 0.3


def _throttle_translate_call():
    """Block just long enough to keep translate calls spaced out app-wide."""
    global _last_translate_call_ts
    with _translate_lock:
        wait = _last_translate_call_ts + _MIN_SECONDS_BETWEEN_TRANSLATE_CALLS - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last_translate_call_ts = time.monotonic()


# MyMemory refuses to "translate" text it auto-detects as already being in the target
# language — e.g. short/ambiguous chat slang ("ping 200 xd") can be detected as matching
# whatever language the user's target already is. Rather than a no-op, it raises this
# exact error. That's not a real failure: the correct output IS the original text.
_MYMEMORY_SAME_LANGUAGE_MESSAGE = "PLEASE SELECT TWO DISTINCT LANGUAGES"


def _translate_text(text, target_lang, email=""):
    """Translate text via MyMemory (through the `translate` package), auto-detecting source."""
    _throttle_translate_call()
    try:
        return MyMemoryTranslator(to_lang=target_lang, from_lang=_MYMEMORY_AUTODETECT, email=email).translate(text)
    except TranslationError as e:
        if _MYMEMORY_SAME_LANGUAGE_MESSAGE in str(e).upper():
            return text
        raise


# --- Translation errors, quota pause and cache ---
# Short labels shown in the chat instead of raw exceptions (which used to include the
# full request URL). Technical details go to app.log only.
TRANSLATION_ERROR_LABELS = {
    "quota": "[not translated – daily limit reached]",
    "network": "[not translated – translation service unreachable]",
    "too_long": "[not translated – message too long for the free service]",
    "other": "[not translated – translation error, see App Log]",
}

_MYMEMORY_QUOTA_MARKERS = ("TOO MANY REQUESTS", "YOU USED ALL AVAILABLE FREE TRANSLATIONS", "MYMEMORY WARNING")
_MYMEMORY_LENGTH_MARKER = "QUERY LENGTH LIMIT EXCEEDED"
# e.g. "...NEXT AVAILABLE IN  10 HOURS 32 MINUTES 50 SECONDS..."
_MYMEMORY_RESET_RE = re.compile(
    r"NEXT AVAILABLE IN\s+(?:(\d+)\s*HOURS?)?\s*(?:(\d+)\s*MINUTES?)?\s*(?:(\d+)\s*SECONDS?)?"
)
_DEFAULT_QUOTA_PAUSE_SECONDS = 10 * 60   # when MyMemory doesn't say when the quota resets
_MAX_QUOTA_PAUSE_SECONDS = 24 * 3600
_TRANSLATION_CACHE_SIZE = 1000

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _is_valid_email(value):
    return bool(_EMAIL_RE.match(value or ""))


def _parse_quota_reset_seconds(text):
    """Seconds until MyMemory's quota resets, parsed from its warning text, or None."""
    m = _MYMEMORY_RESET_RE.search(text.upper())
    if not m or not any(m.groups()):
        return None
    hours, minutes, seconds = (int(g) if g else 0 for g in m.groups())
    total = hours * 3600 + minutes * 60 + seconds
    return max(60, min(total, _MAX_QUOTA_PAUSE_SECONDS))


def _translation_error_text(exc):
    """Collect everything an exception tells us: message, HTTP body, MyMemory JSON."""
    parts = [str(exc)]
    response = getattr(exc, "response", None)
    if response is not None:
        try:
            parts.append(response.text or "")
        except Exception:
            pass
    data = getattr(exc, "json", None)  # set by translate's MyMemory provider
    if isinstance(data, dict):
        parts.append(str(data.get("responseDetails", "")))
    return " ".join(parts)


def _classify_translation_error(exc):
    """Return (kind, retry_after_seconds) — kind is a TRANSLATION_ERROR_LABELS key."""
    text = _translation_error_text(exc).upper()
    status = getattr(getattr(exc, "response", None), "status_code", None)
    if status == 429 or text.startswith("429 ") or any(m in text for m in _MYMEMORY_QUOTA_MARKERS):
        return "quota", _parse_quota_reset_seconds(text)
    if _MYMEMORY_LENGTH_MARKER in text:
        return "too_long", None
    if isinstance(exc, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
        return "network", None
    return "other", None


def _has_letters(text):
    """True if text contains a letter of any script. Text without letters (numbers,
    punctuation, emoji) has nothing to translate and is shown unchanged."""
    return any(ch.isalpha() for ch in text)


class TranslationOutcome(NamedTuple):
    text: str               # translation, unchanged original, or a short error label
    ok: bool                # False → text is a TRANSLATION_ERROR_LABELS label
    kind: str = "ok"        # ok / cached / skipped / quota / network / too_long / other
    detail: str = ""        # technical error detail for app.log
    new_pause: bool = False  # True only on the call that started a quota pause


class TranslationService:
    """Wraps _translate_text with an LRU cache, the no-letters skip and a quota pause.

    Never changes what is displayed for a successful translation; it only avoids
    requests whose result is already known or that would certainly fail.
    """

    def __init__(self, cache_size=_TRANSLATION_CACHE_SIZE, clock=time.time):
        self._cache = OrderedDict()
        self._cache_size = cache_size
        self._lock = threading.Lock()
        self._clock = clock
        self.paused_until = 0.0

    def is_paused(self):
        return self._clock() < self.paused_until

    def resume(self):
        self.paused_until = 0.0

    def translate(self, text, target_lang, email=""):
        if not _has_letters(text):
            return TranslationOutcome(text, True, "skipped")

        key = (text, target_lang)
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return TranslationOutcome(self._cache[key], True, "cached")

        if self.is_paused():
            return TranslationOutcome(TRANSLATION_ERROR_LABELS["quota"], False, "quota")

        try:
            result = _translate_text(text, target_lang, email=email)
            if not result:
                raise TranslationError("Empty translation returned")
            if result.upper().startswith("MYMEMORY WARNING"):
                # Quota warning delivered as a "translation" — never show it as one.
                raise TranslationError(result)
        except Exception as e:
            kind, retry_after = _classify_translation_error(e)
            new_pause = False
            if kind == "quota":
                self.paused_until = self._clock() + (retry_after or _DEFAULT_QUOTA_PAUSE_SECONDS)
                new_pause = True
            return TranslationOutcome(TRANSLATION_ERROR_LABELS[kind], False, kind, str(e), new_pause)

        with self._lock:
            self._cache[key] = result
            self._cache.move_to_end(key)
            while len(self._cache) > self._cache_size:
                self._cache.popitem(last=False)
        return TranslationOutcome(result, True, "ok")


# --- Star Conflict log folder ---
# The game moved its profile and logs from Documents\My Games to %LOCALAPPDATA%\Targem
# (first seen 2026-10-09). Both are checked; the new location wins.
def _local_appdata_dir():
    return os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Local")


def _new_game_logs_path():
    return os.path.join(_local_appdata_dir(), "Targem", "StarConflict", "logs")


def _legacy_game_logs_path():
    return os.path.join(os.path.expanduser("~"), "Documents", "My Games", "StarConflict", "logs")


def _same_path(a, b):
    return os.path.normcase(os.path.normpath(a)) == os.path.normcase(os.path.normpath(b))


def _latest_session_time(logs_folder):
    """Modification time of the newest game session folder, or None if there is none."""
    try:
        times = [f.stat().st_mtime for f in Path(logs_folder).iterdir() if f.is_dir()]
    except OSError:
        return None
    return max(times) if times else None


def compare_versions(remote_ver: str, local_ver: str) -> int:
    """
    Compare two version strings.
    Returns:
        1 if remote > local
        0 if equal
        -1 if remote < local
    """
    def parse_version(ver):
        return tuple(int(x) for x in ver.split('.') if x.isdigit())
    try:
        remote = parse_version(remote_ver)
        local = parse_version(local_ver)
        if remote > local:
            return 1
        elif remote < local:
            return -1
        else:
            return 0
    except:
        return 0


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert") or (0, 0, 0, 0)
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)   # Remove window decorations
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw, text=self.text, justify="left",
            background="lightyellow", relief="solid", borderwidth=1,
            font=("tahoma", "8", "normal")
        )
        label.pack(ipadx=5, ipady=2)

    def hide_tip(self, event=None):
        tw = self.tip_window
        if tw:
            tw.destroy()
        self.tip_window = None


class TranslatedFileWatcher(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Logger (initialize early to avoid issues with remote fetches) ---
        self.logger, self.app_log_path = self._init_logger()
        self.logger.info("Application started")

        # GUI configuration
        self.title("SC Chat Translator "+APP_VERSION)
        self.resizable(GUI_RESIZABLE, GUI_RESIZABLE)

        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.help_icon_img = ctk.CTkImage(
        light_image=Image.open(resource_path("assets/help_blue.png")),  # 16x16 or 24x24 PNG
        dark_image=Image.open(resource_path("assets/help_blue.png")),   # same image for both themes
        size=(16, 16)
        )
        self.iconbitmap(resource_path("assets/logo.ico"))

        # --- Settings & Dictionary load/create ---
        self.settings_path = self._get_settings_path()
        self.dictionary_path = self._get_dictionary_path()
        self.settings = self._load_settings()
        self.translation_service = TranslationService()
        self._status_shows_pause = False
        self._logs_path_migrated = self._migrate_game_logs_path()

        # --- Apply UI preset: geometry + font globals (must be before any widget creation) ---
        _p = UI_PRESETS.get(self.settings.get("ui_preset", UI_PRESET_DEFAULT),
                            UI_PRESETS[UI_PRESET_DEFAULT])
        self.geometry(f"{_p['width']}x{_p['height']}")
        self.minsize(_p['width'], _p['height'])
        # Load local dictionary only — remote fetch happens in background thread after startup
        self.game_dictionary = self._load_local_dictionary()
        self._rebuild_dict_patterns()

        self.settings.setdefault("welcome_counter", 0)

        # --- DB init ---
        self.db_path = self._get_db_path()
        self._init_database()

        # --- Paths / translator / state ---
        self.parent_folder = Path(self.settings["game_logs_path"])
        self.stop_flag = False
        self.current_logfile = None
        self.session_id = None

        self.languages = self.settings["languages"]
        self.manual_languages = self.settings["manual_languages"]
        self.target_lang = self.languages[self.settings["last_language"]]
        self.manual_translate_lang = self.settings["manual_translate_lang"]

        # --- Shared font objects (updated in-place by _apply_ui_preset) ---
        # Also update module globals so future one-off CTkFont() calls use correct size
        global APP_FONT_SIZE, APP_FONT_SIZE_SMALL, APP_FONT_SIZE_GROUP
        APP_FONT_SIZE       = _p["font"]
        APP_FONT_SIZE_SMALL = _p["font_small"]
        APP_FONT_SIZE_GROUP = _p["font_group"]
        self._fnt      = ctk.CTkFont(size=APP_FONT_SIZE)
        self._fnt_grp  = ctk.CTkFont(size=APP_FONT_SIZE_GROUP)
        self._fnt_hint = ctk.CTkFont(size=APP_FONT_SIZE_SMALL)

        # --- Status Bar with Help Button ---
        self.status_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.status_frame.pack(fill="x", padx=8, pady=3)

        # Status label
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text=STATUS_DEFAULT_TEXT,
            anchor="w",
            font=self._fnt
        )
        self.status_label.pack(side="left", fill="x", expand=True)

        # Help button
        self.help_button = ctk.CTkButton(
            self.status_frame,
            image=self.help_icon_img,
            text="",
            width=int(DEFAULT_WINDOW_WIDTH * HELP_BUTTON_RATIO),
            height=BUTTON_HEIGHT,
            command=self._toggle_help_content
        )
        self.help_button.pack(side="right", padx=(4, 0))

        # --- Main Content Container ---
        self.main_content_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.main_content_frame.pack(fill="both", expand=True, padx=0, pady=6)

        # --- Tabs ---
        self.tabview = ctk.CTkTabview(self.main_content_frame)
        self.tabview.pack(fill="both", expand=True, padx=0, pady=0)

        self.tab1 = self.tabview.add("Chat")
        self.tab_history = self.tabview.add("History")
        self.tab_log = self.tabview.add("App Log")
        self.tab3 = self.tabview.add("Settings")

        for button in self.tabview._segmented_button._buttons_dict.values():
            button.configure(width=_p["tab_w"], height=_p["tab_h"])

        # --- Help Content Frame (initially hidden) ---
        self.help_content_frame = ctk.CTkScrollableFrame(self.main_content_frame)
        self.help_content_frame.pack(fill="both", expand=True, padx=0, pady=0)
        self.help_content_frame.pack_forget()  # Hide initially

        # --- Chat Text areas ---
        self.text_area_tab1 = ctk.CTkTextbox(
            self.tab1, wrap=tk.WORD, font=self._fnt
        )
        self.text_area_tab1.pack(expand=True, fill="both", padx=6, pady=6)

        # # --- User translation output area ---
        # self.text_area_tab1.tag_config("manual_header", foreground="gold")  # or any color
        # self.text_area_tab1.tag_config("version_update", foreground="gold")

        # --- Welcome message shown at startup ---
        self._insert_hardcoded_message()

        # --- Schedule remote fetch in background (non-blocking startup) ---
        # Remote welcome/version check and dictionary sync run after the window is shown.
        threading.Thread(target=self._remote_startup_fetch, daemon=True).start()

        if self.settings["welcome_counter"] < 11:
            # Check if we should show extended message (new version detected)
            show_extended = self.settings.get("show_extended_welcome", False)

            if show_extended:
                # Show extended message with all fields (whats_new, changes, notes, download_url)
                self._insert_extended_welcome_message()
                self.settings["show_extended_welcome"] = False  # reset so it only shows once
                self.logger.info(f"Showing extended welcome message (counter: {self.settings['welcome_counter'] + 1}/10)")
            else:
                # Show normal welcome message (only welcome_message)
                self._insert_welcome_message()
                self.logger.info(f"Showing normal welcome message (counter: {self.settings['welcome_counter'] + 1}/10)")

            self.settings["welcome_counter"] += 1
            self._save_settings()

        self._insert_hardcoded_message(
            msg="> Brgds.,   Hystrix.\n>\n",
            tag="hardcoded_tip",
        )
        
        self._insert_hardcoded_message(
            msg="",
            tag="hardcoded_tip",
        )

        # --- User translation output area ---
        self.text_area_tab1.tag_config("manual_header", foreground="gold")  # or any color
        self.text_area_tab1.tag_config("translation_notice", foreground="gold")

        if self._logs_path_migrated:
            self._insert_message_tab1(
                "ℹ Star Conflict now keeps its chat logs in a new folder. Switched to:\n"
                f"   {self.settings['game_logs_path']}\n",
                "translation_notice",
            )

        # Tags
        self.text_area_tab1.tag_config("original", foreground="lightgrey")
        self.text_area_tab1.tag_config("info", foreground="blue")

        # Category color tags
        for cat, color in COLOR_CATEGORIES.items():
            self.text_area_tab1.tag_config(cat, foreground=color)

        # Language color tags
        self.language_colors = LANGUAGE_COLORS
        for (lang_name, lang_code), color in zip(self.languages.items(), self.language_colors):
            # Syntax highlighting based on languages is disabled, 
            # Remove the line below if you want to enable it [not in the settings]
            color = "lightgreen"

            self.text_area_tab1.tag_config(f"translated_{lang_code}", foreground=color)

        # --- Manual Translation Input at bottom of Chat tab ---
        bottom_frame = ctk.CTkFrame(self.tab1)
        bottom_frame.pack(fill="x", padx=6, pady=(0, 6))

        # Dynamic placeholder translation
        placeholder_hint = self._safe_translate(MANUAL_TRANSLATE_PROMPT, self.target_lang)
        self.manual_entry = ctk.CTkEntry(
            bottom_frame,
            placeholder_text=placeholder_hint,
            font=self._fnt
        )
        self.manual_entry.pack(side="left", padx=(4, 6), pady=4, expand=True, fill="x")

        # Button showing short language code
        self.btn_translate = ctk.CTkButton(
            bottom_frame,
            text=self._get_short_code_for_lang(self.manual_translate_lang),
            width=40,
            height=BUTTON_HEIGHT,
            font=self._fnt,
            command=self._manual_translate
        )
        self.btn_translate.pack(side="left", padx=(0, 4), pady=4)

        # Bind Enter key to trigger translation
        self.manual_entry.bind("<Return>", lambda e: self._manual_translate())

        
        # --- History tab ---
        top_hist = ctk.CTkFrame(self.tab_history)
        top_hist.pack(fill="x", padx=6, pady=(6, 0))

        ctk.CTkLabel(
            top_hist, text="Date:",
            font=self._fnt
        ).pack(side="left", padx=(6, 3), pady=6)

        self.history_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.history_date_entry = ctk.CTkEntry(
            top_hist, textvariable=self.history_date_var,
            width=115, font=self._fnt
        )
        self.history_date_entry.pack(side="left", padx=(0, 6), pady=6)

        self.btn_load_date = ctk.CTkButton(
            top_hist, text="Load Date",
            height=BUTTON_HEIGHT, font=self._fnt,
            command=self._load_history_for_date
        )
        self.btn_load_date.pack(side="left", padx=(0, 4), pady=6)

        self.btn_load_last_session = ctk.CTkButton(
            top_hist, text="Last Session",
            height=BUTTON_HEIGHT, font=self._fnt,
            command=self._load_history_last_session
        )
        self.btn_load_last_session.pack(side="left", padx=(0, 4), pady=6)

        self.history_text = ctk.CTkTextbox(
            self.tab_history, wrap=tk.WORD,
            font=self._fnt
        )
        self.history_text.pack(expand=True, fill="both", padx=6, pady=6)
        self.history_text.configure(state="disabled")


        # --- App Log tab ---
        top_log = ctk.CTkFrame(self.tab_log)
        top_log.pack(fill="x", padx=6, pady=(6, 0))

        self.btn_open_log = ctk.CTkButton(
            top_log, text="Open Log File",
            height=BUTTON_HEIGHT, font=self._fnt,
            command=self._open_app_log_file
        )
        self.btn_open_log.pack(side="left", padx=6, pady=6)

        self.app_log_text = ctk.CTkTextbox(
            self.tab_log, wrap=tk.WORD,
            font=self._fnt
        )
        self.app_log_text.pack(expand=True, fill="both", padx=6, pady=6)
        self.app_log_text.configure(state="disabled")


        # --- Settings tab — scrollable container ---
        settings_scroll = ctk.CTkScrollableFrame(self.tab3)
        settings_scroll.pack(fill="both", expand=True, padx=3, pady=3)

        # Convenience aliases — all settings widgets share these instances
        # so _apply_ui_preset() can update them all via .configure()
        _fnt      = self._fnt
        _fnt_grp  = self._fnt_grp
        _fnt_hint = self._fnt_hint

        # ── Group 1: Translation Languages ──────────────────────────────────────
        grp_lang = ctk.CTkFrame(settings_scroll)
        grp_lang.pack(fill="x", padx=5, pady=(6, 3))

        ctk.CTkLabel(grp_lang, text="Translation Languages", font=_fnt_grp
                     ).pack(anchor="w", padx=7, pady=(4, 2))

        lang_row = ctk.CTkFrame(grp_lang, fg_color="transparent")
        lang_row.pack(fill="x", padx=7, pady=(0, 3))

        # Chat translation language
        ctk.CTkLabel(lang_row, text="Chat →", font=_fnt).pack(side="left", padx=(0, 3))
        self.language_var = tk.StringVar(value=self.settings["last_language"])
        self.language_menu = ctk.CTkOptionMenu(
            lang_row,
            values=list(self.languages.keys()),
            variable=self.language_var,
            command=self._change_language,
            height=BUTTON_HEIGHT,
            width=130,
            font=_fnt,
        )
        self.language_menu.pack(side="left", padx=(0, 8))
        ToolTip(self.language_menu, "Select the language into which the game chat should be translated")

        # Manual translation language
        ctk.CTkLabel(lang_row, text="Manual →", font=_fnt).pack(side="left", padx=(0, 3))
        self.manual_lang_var = tk.StringVar(value=self._get_short_code_for_lang(self.manual_translate_lang))
        self.manual_lang_menu = ctk.CTkOptionMenu(
            lang_row,
            values=list(self.manual_languages.keys()),
            variable=self.manual_lang_var,
            command=self._change_manual_language,
            height=BUTTON_HEIGHT,
            width=75,
            font=_fnt,
        )
        self.manual_lang_menu.pack(side="left")
        ToolTip(self.manual_lang_menu, "Select the language for manual text translation input")

        # Apply + Open Settings on the same row
        action_row = ctk.CTkFrame(grp_lang, fg_color="transparent")
        action_row.pack(fill="x", padx=7, pady=(0, 5))

        ctk.CTkButton(
            action_row, text="Apply Changes",
            height=BUTTON_HEIGHT, font=_fnt,
            command=self._apply_settings_changes
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            action_row, text="Open Settings File",
            height=BUTTON_HEIGHT, font=_fnt,
            command=self._open_settings_file
        ).pack(side="left")

        # ── Group 1b: Translation Service ───────────────────────────────────────
        grp_service = ctk.CTkFrame(settings_scroll)
        grp_service.pack(fill="x", padx=5, pady=3)

        ctk.CTkLabel(grp_service, text="Translation Service (MyMemory)", font=_fnt_grp
                     ).pack(anchor="w", padx=7, pady=(4, 2))

        email_row = ctk.CTkFrame(grp_service, fg_color="transparent")
        email_row.pack(fill="x", padx=7, pady=(0, 3))

        self.mymemory_email_var = tk.StringVar(value=self.settings.get("mymemory_email", ""))
        self.mymemory_email_entry = ctk.CTkEntry(
            email_row, textvariable=self.mymemory_email_var,
            placeholder_text="Your email (optional)", font=_fnt
        )
        self.mymemory_email_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))

        ctk.CTkButton(
            email_row, text="Save",
            height=BUTTON_HEIGHT, width=45, font=_fnt,
            command=self._save_mymemory_email
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            email_row, text="Clear",
            height=BUTTON_HEIGHT, width=45, font=_fnt,
            command=self._clear_mymemory_email
        ).pack(side="left")

        # Packed only while it has text (see _set_email_status), so it leaves no gap
        self.mymemory_email_status = ctk.CTkLabel(grp_service, text="", text_color="gray", font=_fnt_hint)

        self._email_hint_label = ctk.CTkLabel(
            grp_service,
            text="Optional: raises the free daily limit from 5,000 to 50,000 characters.\n"
                 "Use your own address — it is stored only in settings.json and sent only to MyMemory.",
            font=_fnt_hint, text_color="gray", justify="left"
        )
        self._email_hint_label.pack(anchor="w", padx=7, pady=(0, 1))

        service_info_link = ctk.CTkLabel(
            grp_service,
            text="Why does an email raise the limit? Why not Google Translate? — Read more",
            font=_fnt_hint, text_color=LINK_COLOR, cursor=LINK_CURSOR
        )
        service_info_link.pack(anchor="w", padx=7, pady=(0, 5))
        service_info_link.bind("<Button-1>", lambda e: self._open_link(TRANSLATION_SERVICE_INFO_URL))
        ToolTip(service_info_link, "Opens the explanation on GitHub in your web browser")

        # ── Group 1c: Translated Channels ───────────────────────────────────────
        grp_channels = ctk.CTkFrame(settings_scroll)
        grp_channels.pack(fill="x", padx=5, pady=3)

        ctk.CTkLabel(grp_channels, text="Translated Channels", font=_fnt_grp
                     ).pack(anchor="w", padx=7, pady=(4, 2))

        self.channel_vars = {}
        for group_title, names in CHANNEL_GROUPS:
            ctk.CTkLabel(grp_channels, text=f"{group_title}:", font=_fnt_hint, text_color="gray"
                         ).pack(anchor="w", padx=7)
            grid = ctk.CTkFrame(grp_channels, fg_color="transparent")
            grid.pack(fill="x", padx=7, pady=(0, 3))
            for i, name in enumerate(names):
                var = tk.BooleanVar(value=self._is_channel_translated(name))
                self.channel_vars[name] = var
                ctk.CTkCheckBox(
                    grid, text=CHANNEL_LABELS.get(name, name), variable=var, font=_fnt,
                    checkbox_width=14, checkbox_height=14, border_width=2,
                    command=lambda n=name, v=var: self._set_channel_translated(n, v.get()),
                ).grid(row=i // 3, column=i % 3, sticky="w", padx=(0, 6), pady=1)

        channel_btns = ctk.CTkFrame(grp_channels, fg_color="transparent")
        channel_btns.pack(fill="x", padx=7, pady=(0, 3))
        ctk.CTkButton(
            channel_btns, text="Translate all", height=BUTTON_HEIGHT, width=90, font=_fnt,
            command=lambda: self._set_all_channels_translated(True)
        ).pack(side="left", padx=(0, 4))
        ctk.CTkButton(
            channel_btns, text="Translate none", height=BUTTON_HEIGHT, width=90, font=_fnt,
            command=lambda: self._set_all_channels_translated(False)
        ).pack(side="left")

        ctk.CTkLabel(
            grp_channels,
            text="Unticked channels are still shown in the chat, just not translated.\n"
                 "Fewer translated channels use less of the free daily limit.",
            font=_fnt_hint, text_color="gray", justify="left"
        ).pack(anchor="w", padx=7, pady=(0, 1))

        channels_info_link = ctk.CTkLabel(
            grp_channels, text="How channels affect the daily limit — Read more",
            font=_fnt_hint, text_color=LINK_COLOR, cursor=LINK_CURSOR
        )
        channels_info_link.pack(anchor="w", padx=7, pady=(0, 5))
        channels_info_link.bind(
            "<Button-1>", lambda e: self._open_link(TRANSLATION_SERVICE_INFO_URL + "#translate-only-the-channels-you-need")
        )

        # ── Group 2: Game Logs Path ──────────────────────────────────────────────
        grp_path = ctk.CTkFrame(settings_scroll)
        grp_path.pack(fill="x", padx=5, pady=3)

        ctk.CTkLabel(grp_path, text="Star Conflict Logs Folder", font=_fnt_grp
                     ).pack(anchor="w", padx=7, pady=(4, 2))

        self.game_path_var = tk.StringVar(value=str(self.parent_folder))
        self.game_path_entry = ctk.CTkEntry(
            grp_path, textvariable=self.game_path_var, font=_fnt
        )
        self.game_path_entry.pack(fill="x", padx=7, pady=(0, 3))

        path_btns = ctk.CTkFrame(grp_path, fg_color="transparent")
        path_btns.pack(fill="x", padx=7, pady=(0, 5))

        ctk.CTkButton(
            path_btns, text="Browse",
            height=BUTTON_HEIGHT, font=_fnt,
            command=self._browse_game_folder
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            path_btns, text="Save Path",
            height=BUTTON_HEIGHT, font=_fnt,
            command=self._save_game_path
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            path_btns, text="Reset to Default",
            height=BUTTON_HEIGHT, font=_fnt,
            command=self._reset_game_path
        ).pack(side="left")

        # ── Group 3: Game Dictionary ─────────────────────────────────────────────
        grp_dict = ctk.CTkFrame(settings_scroll)
        grp_dict.pack(fill="x", padx=5, pady=3)

        ctk.CTkLabel(grp_dict, text="Game Dictionary", font=_fnt_grp
                     ).pack(anchor="w", padx=7, pady=(4, 2))

        dict_top_row = ctk.CTkFrame(grp_dict, fg_color="transparent")
        dict_top_row.pack(fill="x", padx=7, pady=(0, 3))

        ctk.CTkButton(
            dict_top_row, text="Open Dictionary File",
            height=BUTTON_HEIGHT, font=_fnt,
            command=self._open_dictionary_file
        ).pack(side="left")

        # Add-entry row: Key field + Translation field + Add + Reload — all on one line
        ctk.CTkLabel(grp_dict, text="Add entry:", font=_fnt).pack(anchor="w", padx=7)

        self.dict_entry_frame = ctk.CTkFrame(grp_dict, fg_color="transparent")
        self.dict_entry_frame.pack(fill="x", padx=7, pady=(2, 3))

        self.dict_key_entry = ctk.CTkEntry(
            self.dict_entry_frame, placeholder_text="Key",
            width=100, font=_fnt
        )
        self.dict_key_entry.pack(side="left", padx=(0, 4))

        self.dict_value_entry = ctk.CTkEntry(
            self.dict_entry_frame, placeholder_text="Translation", font=_fnt
        )
        self.dict_value_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))

        ctk.CTkButton(
            self.dict_entry_frame, text="Add",
            height=BUTTON_HEIGHT, width=45, font=_fnt,
            command=self._add_dictionary_entry
        ).pack(side="left", padx=(0, 4))

        ctk.CTkButton(
            self.dict_entry_frame, text="Reload",
            height=BUTTON_HEIGHT, width=55, font=_fnt,
            command=self._reload_dictionary
        ).pack(side="left")

        ctk.CTkLabel(
            grp_dict,
            text="Key = game term  ·  Translation = replacement in chat",
            font=_fnt_hint, text_color="gray"
        ).pack(anchor="w", padx=7, pady=(0, 5))

        # ── Group 4: Remote Dictionary ───────────────────────────────────────────
        grp_remote = ctk.CTkFrame(settings_scroll)
        grp_remote.pack(fill="x", padx=5, pady=(3, 6))

        ctk.CTkLabel(grp_remote, text="Remote Dictionary", font=_fnt_grp
                     ).pack(anchor="w", padx=7, pady=(4, 2))

        self.remote_dict_var = tk.BooleanVar(value=self.settings.get("allow_remote_dictionary", False))
        remote_switch = ctk.CTkSwitch(
            grp_remote,
            text="Enable remote dictionary sync",
            variable=self.remote_dict_var,
            command=self._toggle_remote_dictionary,
            onvalue=True, offvalue=False,
            font=_fnt,
        )
        remote_switch.pack(anchor="w", padx=7, pady=(0, 2))
        ToolTip(
            remote_switch,
            "Download community dictionary entries and merge them with your local dictionary.\n"
            "Local entries always take priority unless 'Remote overrides local' is enabled."
        )

        self.remote_override_var = tk.BooleanVar(
            value=self.settings.get("remote_dictionary_overrides_local", False)
        )
        override_switch = ctk.CTkSwitch(
            grp_remote,
            text="Remote overrides local on conflict",
            variable=self.remote_override_var,
            command=self._toggle_remote_override,
            onvalue=True, offvalue=False,
            font=_fnt,
        )
        override_switch.pack(anchor="w", padx=7, pady=(0, 3))
        ToolTip(
            override_switch,
            "When enabled, community dictionary entries replace your local ones on key conflicts.\n"
            "Disable to keep your custom translations safe."
        )

        sync_row = ctk.CTkFrame(grp_remote, fg_color="transparent")
        sync_row.pack(fill="x", padx=7, pady=(0, 3))

        self.btn_sync_dict = ctk.CTkButton(
            sync_row, text="Sync Now",
            height=BUTTON_HEIGHT, font=_fnt,
            command=self._sync_remote_dictionary_now
        )
        self.btn_sync_dict.pack(side="left", padx=(0, 8))

        self.dict_sync_status = ctk.CTkLabel(sync_row, text="", text_color="gray", font=_fnt_hint)
        self.dict_sync_status.pack(side="left")

        ctk.CTkLabel(
            grp_remote,
            text="Fetched at most once per hour (rate-limited).",
            font=_fnt_hint, text_color="gray"
        ).pack(anchor="w", padx=7, pady=(0, 5))

        # ── Group 5: Appearance ──────────────────────────────────────────────────
        grp_appearance = ctk.CTkFrame(settings_scroll)
        grp_appearance.pack(fill="x", padx=5, pady=(3, 6))

        ctk.CTkLabel(grp_appearance, text="Appearance", font=_fnt_grp
                     ).pack(anchor="w", padx=7, pady=(4, 2))

        appearance_row = ctk.CTkFrame(grp_appearance, fg_color="transparent")
        appearance_row.pack(fill="x", padx=7, pady=(0, 3))

        ctk.CTkLabel(appearance_row, text="UI Size:", font=_fnt).pack(side="left", padx=(0, 6))

        self.ui_preset_var = tk.StringVar(value=self.settings.get("ui_preset", UI_PRESET_DEFAULT))
        self.ui_preset_menu = ctk.CTkOptionMenu(
            appearance_row,
            values=list(UI_PRESETS.keys()),
            variable=self.ui_preset_var,
            command=self._apply_ui_preset,
            height=BUTTON_HEIGHT,
            width=100,
            font=_fnt,
        )
        self.ui_preset_menu.pack(side="left")
        ToolTip(self.ui_preset_menu, "Change font size and window dimensions. Takes effect immediately.")

        ctk.CTkLabel(
            grp_appearance,
            text="Small = compact  ·  Medium = comfortable  ·  Large = accessible",
            font=_fnt_hint, text_color="gray"
        ).pack(anchor="w", padx=7, pady=(0, 5))

        # --- Threads for watchers ---
        threading.Thread(target=self._watch_latest_chat, daemon=True).start()
        threading.Thread(target=self._tail_app_log, daemon=True).start()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------------- Welcome message ----------------    

    def _insert_hardcoded_message(self, msg=None, tag="hardcoded_welcome", color=DEFAULT_WELCOME_COLOR):
        """Insert a hardcoded or custom message with translation and styling."""
        if msg is None:
            msg = f"> Welcome to StarConflict Chat Translator ver. {APP_VERSION}"

        try:
            translated = self._safe_translate(msg, self.target_lang) + "\n"
        except Exception as e:
            translated = msg
            self.logger.error(f"Hardcoded message translation failed: {e}")

        self.text_area_tab1.configure(state="normal")
        self.text_area_tab1.insert("end", translated, tag)
        self.text_area_tab1.configure(state="disabled")

        # Configure default or custom color
        self.text_area_tab1.tag_config(tag, foreground=color)

    def _insert_welcome_message(self):
        """Insert welcome message - shows ONLY welcome_message for 10 times, no extended content"""
        welcome_color = self.settings.get("welcome_message_color", DEFAULT_WELCOME_COLOR)

        # Check if we have remote welcome message stored
        remote_welcome_msg = self.settings.get("remote_welcome_message", "").strip()

        if remote_welcome_msg:
            # Show ONLY the welcome_message (no extended content like whats_new, notes, download_url)
            try:
                translated_text = self._safe_translate(remote_welcome_msg, self.target_lang)
            except Exception as e:
                translated_text = remote_welcome_msg  # fallback if translation fails
                self.logger.error(f"Welcome message translation failed: {e}")

            # Insert into chat area
            self.text_area_tab1.configure(state="normal")
            self.text_area_tab1.insert("end", "> " + translated_text + "\n", "welcome_tag")
            self.text_area_tab1.configure(state="disabled")

            # Style
            self.text_area_tab1.tag_config("welcome_tag", foreground=welcome_color)
        else:
            # Fallback to default welcome text
            default_text = DEFAULT_WELCOME_TEXT
            try:
                translated_text = self._safe_translate(default_text, self.target_lang)
            except Exception as e:
                translated_text = default_text  # fallback if translation fails
                self.logger.error(f"Default welcome text translation failed: {e}")

            # Insert into chat area
            self.text_area_tab1.configure(state="normal")
            self.text_area_tab1.insert("end", "> " + translated_text + "\n", "welcome_tag")
            self.text_area_tab1.configure(state="disabled")

            # Style
            self.text_area_tab1.tag_config("welcome_tag", foreground=welcome_color)

    def _insert_extended_welcome_message(self):
        """Insert extended welcome message with all fields (whats_new, changes, notes, download_url)"""
        welcome_color = self.settings.get("welcome_message_color", DEFAULT_WELCOME_COLOR)

        # Get all stored remote fields
        remote_welcome_msg = self.settings.get("remote_welcome_message", "").strip()
        remote_whats_new = self.settings.get("remote_whats_new")
        remote_download_url = self.settings.get("remote_download_url", "").strip()
        remote_notes = self.settings.get("remote_notes", "").strip()

        self.text_area_tab1.configure(state="normal")

        # Display elements in specified order: welcome_message, whats_new -> changes, download_link, notes

        # 1. Welcome message (main content - always present in extended mode)
        if remote_welcome_msg:
            try:
                translated = self._safe_translate(remote_welcome_msg, self.target_lang)
                self.text_area_tab1.insert("end", "> " + translated + "\n", "welcome_tag")
            except Exception as e:
                self.logger.error(f"Welcome message translation failed: {e}")
                self.text_area_tab1.insert("end", "> " + remote_welcome_msg + "\n", "welcome_tag")

        # 2. What's new -> changes (if present and not empty)
        if remote_whats_new and remote_whats_new.get('changes'):
            changes = remote_whats_new['changes']
            if changes:
                self.text_area_tab1.insert("end", "> What's new:\n", "welcome_tag")
                for change in changes:
                    if change and change.strip():  # Only process non-empty changes
                        try:
                            translated = self._safe_translate(change.strip(), self.target_lang)
                            self.text_area_tab1.insert("end", f"> {translated}\n", "welcome_tag")
                        except Exception as e:
                            self.logger.error(f"Change translation failed: {e}")
                            self.text_area_tab1.insert("end", f"> {change.strip()}\n", "welcome_tag")
                            # self.text_area_tab1.insert("end", f"> • {change.strip()}\n", "welcome_tag")

        # 3. Download link (if present and not empty)
        if remote_download_url:
            try:
                translated_label = self._safe_translate("Download:", self.target_lang)
                self.text_area_tab1.insert("end", f"> {translated_label} {remote_download_url}\n", "welcome_tag")
            except Exception as e:
                self.logger.error(f"Download label translation failed: {e}")
                self.text_area_tab1.insert("end", f"> Download: {remote_download_url}\n", "welcome_tag")

        # 4. Notes (if present and not empty)
        if remote_notes:
            try:
                translated_label = self._safe_translate("Notes:", self.target_lang)
                translated_notes = self._safe_translate(remote_notes, self.target_lang)
                self.text_area_tab1.insert("end", f"> {translated_label} {translated_notes}\n", "welcome_tag")
            except Exception as e:
                self.logger.error(f"Notes translation failed: {e}")
                self.text_area_tab1.insert("end", f"> Notes: {remote_notes}\n", "welcome_tag")

        self.text_area_tab1.configure(state="disabled")

        # Style with remote color
        self.text_area_tab1.tag_config("welcome_tag", foreground=welcome_color)

    def _insert_version_update_message(self, data):
        """Insert version update notification with proper translation and styling"""
        version = data.get('version', 'unknown')
        msg = f"A new version {version} is available!\n"

        whats_new = data.get('whats_new', {})
        if whats_new and whats_new.get('changes'):
            msg += "What's new:\n"
            for change in whats_new['changes']:
                if change and change.strip():
                    msg += f"- {change}\n"

        download_url = data.get('download_url', '').strip()
        if download_url:
            msg += f"Download: {download_url}\n"

        notes = data.get('notes', '').strip()
        if notes:
            msg += f"Notes: {notes}\n"

        # Translate the entire message
        try:
            translated_msg = self._safe_translate(msg, self.target_lang)
        except Exception as e:
            self.logger.error(f"Version update message translation failed: {e}")
            translated_msg = msg

        # Insert version update notification into chat
        self.text_area_tab1.configure(state="normal")
        self.text_area_tab1.insert("end", translated_msg, "version_update")
        self.text_area_tab1.configure(state="disabled")
        self.text_area_tab1.see("end")
        self.text_area_tab1.tag_config("version_update", foreground="gold")

    def _toggle_help_content(self):
        """Switch between normal content and help content"""
        if self.help_content_frame.winfo_ismapped():
            # Currently showing help - switch to normal content
            self.help_content_frame.pack_forget()
            self.tabview.pack(fill="both", expand=True, padx=0, pady=0)
            self.status_label.configure(text="Processing chat.log...")
        else:
            # Currently showing normal content - switch to help
            self.tabview.pack_forget()
            self.help_content_frame.pack(fill="both", expand=True, padx=0, pady=0)
            self.status_label.configure(text="Help & About")
            # Create help content if not already created
            if not hasattr(self, '_help_content_created'):
                self._create_help_content()
                self._help_content_created = True

    def _create_help_content(self):
        """Create the comprehensive help content structure"""

        # Application Information Section
        app_info_frame = ctk.CTkFrame(self.help_content_frame)
        app_info_frame.pack(fill="x", pady=HELP_SECTION_SPACING)

        ctk.CTkLabel(
            app_info_frame,
            text=f"Star Conflict Chat Translator\nVersion: {APP_VERSION}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10, padx=HELP_CONTENT_PADDING)

        ctk.CTkLabel(
            app_info_frame,
            text=f"Author: {APP_AUTHOR}\nEmail: {AUTHOR_EMAIL}",
            font=ctk.CTkFont(size=12)
        ).pack(pady=(0, 5), padx=HELP_CONTENT_PADDING)

        # License Information
        license_text = """MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy 
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software."""

        ctk.CTkLabel(
            app_info_frame,
            text="License: MIT License",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(5, 5), padx=HELP_CONTENT_PADDING, anchor="w")

        license_label = ctk.CTkLabel(
            app_info_frame,
            text=license_text,
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        license_label.pack(pady=(0, 5), padx=HELP_CONTENT_PADDING, anchor="w")

        # Links Section
        links_frame = ctk.CTkFrame(self.help_content_frame)
        links_frame.pack(fill="x", pady=HELP_SECTION_SPACING)

        ctk.CTkLabel(
            links_frame,
            text="Links:",
            font=ctk.CTkFont(size=14, weight="bold")
        # ).pack(pady=(15, 10), padx=HELP_CONTENT_PADDING, anchor="w")
        ).pack(pady=(1, 2), padx=HELP_CONTENT_PADDING, anchor="w")

        # Project Repository Link
        self.project_link = ctk.CTkLabel(
            links_frame,
            text="• Project Repository",
            font=ctk.CTkFont(size=12),
            text_color=LINK_COLOR,
            cursor=LINK_CURSOR
        )
        self.project_link.pack(pady=1, padx=HELP_CONTENT_PADDING, anchor="w")
        self.project_link.bind("<Button-1>", lambda e: self._open_link(PROJECT_REPOSITORY_URL))

        # User Manual Link
        self.manual_link = ctk.CTkLabel(
            links_frame,
            text="• User Manual",
            font=ctk.CTkFont(size=12),
            text_color=LINK_COLOR,
            cursor=LINK_CURSOR
        )
        self.manual_link.pack(pady=1, padx=HELP_CONTENT_PADDING, anchor="w")
        self.manual_link.bind("<Button-1>", lambda e: self._open_link(USER_MANUAL_URL))

        # Releases / Download Link
        self.releases_link = ctk.CTkLabel(
            links_frame,
            text="• Releases / Download",
            font=ctk.CTkFont(size=12),
            text_color=LINK_COLOR,
            cursor=LINK_CURSOR
        )
        self.releases_link.pack(pady=1, padx=HELP_CONTENT_PADDING, anchor="w")
        self.releases_link.bind("<Button-1>", lambda e: self._open_link(RELEASES_URL))

        # Issues Link
        self.issues_link = ctk.CTkLabel(
            links_frame,
            text="• Report an Issue",
            font=ctk.CTkFont(size=12),
            text_color=LINK_COLOR,
            cursor=LINK_CURSOR
        )
        self.issues_link.pack(pady=1, padx=HELP_CONTENT_PADDING, anchor="w")
        self.issues_link.bind("<Button-1>", lambda e: self._open_link(ISSUES_URL))

        # Contact information moved to application info section

        # Version Check Section
        version_frame = ctk.CTkFrame(self.help_content_frame)
        version_frame.pack(fill="x", pady=HELP_SECTION_SPACING)

        ctk.CTkLabel(
            version_frame,
            text="Version Check:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(5, 5), padx=HELP_CONTENT_PADDING, anchor="w")

        # Check Updates Link
        self.check_updates_link = ctk.CTkLabel(
            version_frame,
            text="Check for Updates",
            font=ctk.CTkFont(size=12),
            text_color=LINK_COLOR,
            cursor=LINK_CURSOR
        )
        self.check_updates_link.pack(pady=(0, 10), padx=HELP_CONTENT_PADDING, anchor="w")
        self.check_updates_link.bind("<Button-1>", lambda e: self._check_version_in_help())

        # Status Label
        self.version_status_label = ctk.CTkLabel(
            version_frame,
            text="Ready to check...",
            font=ctk.CTkFont(size=12)
        )
        self.version_status_label.pack(pady=(0, 10), padx=HELP_CONTENT_PADDING, anchor="w")

        # Update Information Labels (initially empty)
        self.update_info_frame = ctk.CTkFrame(version_frame, fg_color='transparent')
        self.update_info_frame.pack(fill="x", padx=HELP_CONTENT_PADDING, pady=(0, 8))

        self.update_title_label = ctk.CTkLabel(
            self.update_info_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.update_title_label.pack(anchor="w")

        self.update_changes_label = ctk.CTkLabel(
            self.update_info_frame,
            text="",
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        self.update_changes_label.pack(anchor="w", pady=(2, 0))

        self.update_download_label = ctk.CTkLabel(
            self.update_info_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=LINK_COLOR,
            cursor=LINK_CURSOR
        )
        self.update_download_label.pack(anchor="w", pady=(2, 0))

        self.update_notes_label = ctk.CTkLabel(
            self.update_info_frame,
            text="",
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        self.update_notes_label.pack(anchor="w", pady=(2, 0))

    # Safer wrapper around translator.translate [hardcoded messages only]
    def _safe_translate(self, text, dest):
        try:
            if not text:
                return text
            if dest == "en":
                # Every string passed here is a hardcoded or remote-fetched UI/welcome
                # string authored in English — translating English to English is a
                # no-op MyMemory rejects outright ("PLEASE SELECT TWO DISTINCT
                # LANGUAGES"), so skip the round-trip. Does not apply to _manual_translate
                # or live chat translation, where the source language is genuinely
                # unknown and English-to-English is a legitimate possible outcome.
                return text
            outcome = self.translation_service.translate(
                text, dest, email=self.settings.get("mymemory_email", "")
            )
            if outcome.ok:
                return outcome.text
            if outcome.detail:
                self.logger.warning(f"Translation failed ({outcome.kind}): {outcome.detail}")
            if outcome.new_pause:
                self._announce_translation_pause()
        except Exception as e:
            self.logger.warning(f"Translation failed: {e}")
        return text


    def _translate_for_display(self, text, target_lang):
        """Translate chat/manual text; returns a TranslationOutcome whose .text is safe to
        show (a translation, the unchanged original, or a short error label)."""
        outcome = self.translation_service.translate(
            text, target_lang, email=self.settings.get("mymemory_email", "")
        )
        if outcome.ok:
            if self._status_shows_pause and not self.translation_service.is_paused():
                self._status_shows_pause = False
                self._set_status(STATUS_DEFAULT_TEXT)
        elif outcome.detail:  # requests skipped during a pause have no detail — don't log each
            self.logger.error(f"Translation error ({outcome.kind}): {outcome.detail}")
        if outcome.new_pause:
            self._announce_translation_pause()
        return outcome

    def _announce_translation_pause(self):
        """One chat notice + status bar text per quota pause (not one per message)."""
        until = datetime.fromtimestamp(self.translation_service.paused_until)
        minutes = max(1, round((self.translation_service.paused_until - time.time()) / 60))
        wait = f"about {minutes} min" if minutes < 90 else f"about {round(minutes / 60)} h"
        msg = (
            f"⚠ Translation paused: the free MyMemory limit has been reached "
            f"(resumes in {wait}, ~{until:%H:%M}). Chat messages are still shown, untranslated."
        )
        if not self.settings.get("mymemory_email"):
            msg += ("\n   Tip: add your email in Settings → Translation Service to raise the "
                    "limit from 5,000 to 50,000 characters/day.")
        self.logger.warning(f"Translation paused until {until:%Y-%m-%d %H:%M:%S} (quota reached)")
        self._insert_message_tab1(msg + "\n", "translation_notice")
        self._status_shows_pause = True
        self._set_status(f"Translation paused – free daily limit reached (until ~{until:%H:%M})")

    def _set_status(self, text):
        try:
            self.status_label.configure(text=text)
        except Exception:
            pass

    # ------------- Translated channels --------------
    def _is_channel_translated(self, category):
        return category not in self.settings.get("untranslated_channels", [])

    def _set_channel_translated(self, category, translate):
        off = [c for c in self.settings.get("untranslated_channels", []) if c != category]
        if not translate:
            off.append(category)
        self.settings["untranslated_channels"] = off  # always a new list (not the default's)
        self._save_settings()
        self.logger.info(f"Channel {category}: translation {'on' if translate else 'off'}")

    def _set_all_channels_translated(self, translate):
        for var in self.channel_vars.values():
            var.set(translate)
        self.settings["untranslated_channels"] = (
            [] if translate else [c for _, names in CHANNEL_GROUPS for c in names]
        )
        self._save_settings()
        self.logger.info(f"All channels: translation {'on' if translate else 'off'}")

    def _set_email_status(self, text):
        self.mymemory_email_status.configure(text=text)
        if not self.mymemory_email_status.winfo_manager():
            self.mymemory_email_status.pack(anchor="w", padx=7, before=self._email_hint_label)

    def _save_mymemory_email(self):
        email = self.mymemory_email_var.get().strip()
        if not email:
            self._clear_mymemory_email()
            return
        if not _is_valid_email(email):
            self._set_email_status("That doesn't look like an email address — not saved.")
            return
        self.settings["mymemory_email"] = email
        self._save_settings()
        self.translation_service.resume()  # the higher quota applies immediately
        self._set_email_status("Saved. Higher daily limit is active.")
        self.logger.info("MyMemory email saved (higher daily limit)")  # never log the address

    def _clear_mymemory_email(self):
        self.mymemory_email_var.set("")
        self.settings["mymemory_email"] = ""
        self._save_settings()
        self._set_email_status("Cleared. Using the anonymous daily limit.")
        self.logger.info("MyMemory email cleared")

    def _manual_translate(self):
        text = self.manual_entry.get().strip()
        if not text:
            return

        outcome = self._translate_for_display(text, self.manual_translate_lang)
        translated = outcome.text

        # Copy to clipboard (never copy an error label)
        if outcome.ok:
            try:
                pyperclip.copy(translated)
            except Exception as e:
                self.logger.warning(f"Clipboard copy failed: {e}")

        # Insert into chat area (but NOT DB)
        header_line = f"[Manual Translation → {self.manual_translate_lang.upper()}]"
        self._insert_message_tab1(header_line, "manual_header")
        self._insert_message_tab1(">   '" + text + "'", "original")
        self._insert_message_tab1("→ " + translated, f"translated_{self.manual_translate_lang}")
        self._insert_message_tab1("")

        # Clear entry
        self.manual_entry.delete(0, "end")


    # ---------------- Paths / Files ----------------
    def _get_settings_path(self):
        user_home = os.path.expanduser("~")
        app_folder = os.path.join(user_home, "AppData", "Local", "ScTranslationApp")
        os.makedirs(app_folder, exist_ok=True)
        return os.path.join(app_folder, "settings.json")

    def _get_dictionary_path(self):
        user_home = os.path.expanduser("~")
        app_folder = os.path.join(user_home, "AppData", "Local", "ScTranslationApp")
        return os.path.join(app_folder, "game_dictionary.json")

    def _get_default_logs_path(self):
        """New game location if present, else the legacy one if present, else the new one."""
        new_path, legacy_path = _new_game_logs_path(), _legacy_game_logs_path()
        if os.path.isdir(new_path):
            return new_path
        if os.path.isdir(legacy_path):
            return legacy_path
        return new_path

    def _migrate_game_logs_path(self):
        """Move a saved legacy default logs path to the game's new location — only if the
        user never chose a custom folder and the new folder has a newer game session."""
        saved = self.settings.get("game_logs_path")
        new_path, legacy_path = _new_game_logs_path(), _legacy_game_logs_path()
        if not saved or not _same_path(saved, legacy_path) or not os.path.isdir(new_path):
            return False
        new_latest = _latest_session_time(new_path)
        legacy_latest = _latest_session_time(legacy_path)
        if new_latest is None or (legacy_latest is not None and legacy_latest >= new_latest):
            return False
        self.settings["game_logs_path"] = new_path
        self._save_settings()
        self.logger.info(f"Game logs path migrated from {legacy_path} to {new_path}")
        return True

    def _get_db_path(self):
        user_home = os.path.expanduser("~")
        db_dir = os.path.join(user_home, "AppData", "Local", "ScTranslationApp", "database")
        os.makedirs(db_dir, exist_ok=True)
        return os.path.join(db_dir, "chat_history.db")

    def _fetch_remote_dictionary(self):
        """Download remote dictionary JSON if enabled and interval has elapsed."""
        if not self.settings.get("allow_remote_dictionary", False):
            return {}
        if not self._should_fetch_remote():
            return {}

        url = self.settings.get("remote_dictionary_url", "")
        data = self._fetch_remote_json(url)
        if not data:
            self.logger.warning("Remote dictionary fetch failed or empty.")
            return {}
        if not isinstance(data, dict):
            self.logger.warning("Remote dictionary is not a dict.")
            return {}
        return data

    def _merge_dictionaries(self, base: dict, remote: dict):
        """Merge remote dictionary into base.
        By default local entries take precedence (case-insensitive key comparison).
        When settings['remote_dictionary_overrides_local'] is True, remote entries
        replace local ones on conflict so the community dictionary always wins.
        """
        override = self.settings.get("remote_dictionary_overrides_local", False)
        merged = dict(base)
        base_keys_lower = {k.lower(): k for k in base.keys()}

        for key, val in remote.items():
            existing_key = base_keys_lower.get(key.lower())
            if existing_key is None:
                # New key — always add
                merged[key] = val
            elif override:
                # Conflict and override enabled — remote wins, keep remote casing
                del merged[existing_key]
                merged[key] = val
            # else: local wins, do nothing
        return merged
    
    def _load_settings(self):
        """Load settings.json or create with defaults if not found."""
        if not os.path.exists(self.settings_path):
            # First run → set logs path dynamically
            DEFAULT_SETTINGS["game_logs_path"] = self._get_default_logs_path()
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_SETTINGS, f, indent=4)
            return DEFAULT_SETTINGS.copy()
        else:
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    settings = json.load(f)

                # Ensure backwards compatibility: fill any missing keys with defaults
                for key, value in DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = value

                # BF-5: Reset ghost last_notified_version.
                # If a test/intermediate remote value was ever written that is higher than
                # the current APP_VERSION, it would permanently suppress update notifications.
                # Detect and correct it on first run of this version.
                stored_notified = settings.get("last_notified_version", APP_VERSION)
                if compare_versions(stored_notified, APP_VERSION) == 1:
                    self.logger.info(
                        f"Resetting ghost last_notified_version {stored_notified!r} → {APP_VERSION}"
                    )
                    settings["last_notified_version"] = APP_VERSION
                    settings["welcome_counter"] = 0

                # The remote dictionary moved from jsonsilo.com to the GitHub repository.
                # Only the old default is replaced; a custom URL is left alone.
                if settings.get("remote_dictionary_url") in LEGACY_REMOTE_DICTIONARY_URLS:
                    settings["remote_dictionary_url"] = DEFAULT_REMOTE_DICTIONARY_URL
                    self.logger.info("Remote dictionary URL migrated to the GitHub repository")

                return settings
            except Exception as e:
                print(f"[ERROR] Failed to load settings, using defaults: {e}")
                return DEFAULT_SETTINGS.copy()

    def _save_settings(self):
        """Save current settings to file, ensuring new defaults are included."""
        try:
            for key, value in DEFAULT_SETTINGS.items():
                if key not in self.settings:
                    self.settings[key] = value

            # Always reflect the current binary version (never frozen at install-time value)
            self.settings["app_version"] = APP_VERSION

            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"[ERROR] Failed to save settings: {e}")

    # ---- fetch/check helper ----
    def _fetch_remote_json(self, url: str, timeout: float = 3.0):
        """Return dict from URL or None on any error."""
        if not url:
            return None
        try:
            req = Request(url, headers={"User-Agent": f"SC-Translator/{APP_VERSION}"})
            with urlopen(req, timeout=timeout) as resp:
                if resp.status != 200:
                    return None
                raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw)
        except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as e:
            self.logger.warning(f"Remote fetch failed ({url[:60]}): {e}")
            return None

    def _should_fetch_remote(self):
        """Check if we should attempt remote fetch based on time interval."""
        last_fetch = self.settings.get("last_remote_fetch", 0)
        interval = self.settings.get("remote_fetch_interval", 3600)  # 1 hour default
        current_time = time.time()

        if current_time - last_fetch > interval:
            return True
        return False

    def _update_fetch_time(self):
        """Update the last fetch timestamp."""
        self.settings["last_remote_fetch"] = int(time.time())
        self._save_settings()

    def _check_remote_welcome(self):
        """
        Check for remote welcome message and version updates.
        Handles backward compatibility with old JSON format.
        Rate-limited by _should_fetch_remote() to once per remote_fetch_interval (default 1 hour).
        Safe to call from a background thread; any GUI update must go through self.after().
        """
        if not self._should_fetch_remote():
            self.logger.info("Skipping remote fetch — interval not elapsed")
            return False

        url = DEFAULT_REMOTE_WELCOME_URL
        data = self._fetch_remote_json(url)

        # Update fetch timestamp after the attempt (success or failure)
        self._update_fetch_time()

        if not data:
            self.logger.warning("No data received from remote welcome URL")
            return False

        # Handle if data is list (new format)
        if isinstance(data, list) and data:
            data = data[0]

        # Get welcome message (now the main content is in 'welcome_message')
        welcome_msg = data.get('welcome_message', '').strip()
        new_color = str(data.get("color", "DodgerBlue")).strip() or "DodgerBlue"
        new_id = str(data.get("id", "")).strip()

        self.logger.info(f"Remote data received: id={new_id}, msg_len={len(welcome_msg)}, color={new_color}")

        # Initialize update flags
        welcome_update_needed = False
        version_update_needed = False

        # Check for welcome update
        if new_id:
            prev_id = str(self.settings.get("remote_welcome_id", "0000"))
            try:
                is_newer_id = int(new_id) > int(prev_id)
                is_older_id = int(new_id) < int(prev_id)
            except ValueError:
                is_newer_id = (new_id != prev_id)
                is_older_id = False

            # Check if content has changed (even if ID is the same)
            current_welcome = self.settings.get("remote_welcome_message", "").strip()
            current_whats_new = self.settings.get("remote_whats_new")
            current_download_url = self.settings.get("remote_download_url", "").strip()
            current_notes = self.settings.get("remote_notes", "").strip()

            new_whats_new = data.get('whats_new')
            new_download_url = data.get('download_url', '').strip()
            new_notes = data.get('notes', '').strip()

            # Check if any content has changed
            welcome_changed = welcome_msg != current_welcome
            whats_new_changed = new_whats_new != current_whats_new
            download_changed = new_download_url != current_download_url
            notes_changed = new_notes != current_notes

            content_changed = welcome_changed or whats_new_changed or download_changed or notes_changed

            # Check if welcome update is needed
            welcome_update_needed = ((is_newer_id or is_older_id) or content_changed) and welcome_msg.strip()
        else:
            prev_id = "N/A"
            welcome_update_needed = False

        # Check for version update
        remote_version = data.get('version', '').strip()
        if remote_version and compare_versions(remote_version, APP_VERSION) == 1:
            last_notified = self.settings.get('last_notified_version', APP_VERSION)
            version_update_needed = (remote_version != last_notified)

        # Apply updates if needed
        updates_applied = False

        if welcome_update_needed:
            self.logger.info(f"Updating remote welcome: id {self.settings.get('remote_welcome_id', '0000')} -> {new_id}, content_changed={content_changed}")
            self.settings["remote_welcome_id"] = new_id
            self.settings["welcome_message_color"] = new_color
            self.settings["remote_welcome_message"] = welcome_msg
            self.settings["remote_whats_new"] = new_whats_new
            self.settings["remote_download_url"] = new_download_url
            self.settings["remote_notes"] = new_notes
            updates_applied = True

        if version_update_needed:
            self.logger.info(f"New version detected: {remote_version} > {APP_VERSION}")
            self.settings["show_extended_welcome"] = True
            self.settings['last_notified_version'] = remote_version
            updates_applied = True

        # If any updates were applied, reset counter and save
        if updates_applied:
            self.settings["welcome_counter"] = 0
            self._save_settings()

            # Show version update notification if version was updated
            if version_update_needed:
                self._insert_version_update_message(data)
                self.logger.info(f"Version update notified: {remote_version}")

            self.logger.info(f"Settings updated - welcome: {welcome_update_needed}, version: {version_update_needed}")
            return True
        else:
            self.logger.info(f"No updates needed - welcome: {welcome_update_needed}, version: {version_update_needed}")
            return False

    def _load_local_dictionary(self):
        """Load only the local game_dictionary.json — no network calls."""
        if not os.path.exists(self.dictionary_path):
            default_dict = DEFAULT_DICTIONARY.copy()
            with open(self.dictionary_path, "w", encoding="utf-8") as f:
                json.dump(default_dict, f, indent=4)
            return default_dict
        with open(self.dictionary_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_dictionary(self):
        """Load local dictionary and merge with remote if enabled and interval elapsed."""
        base_dict = self._load_local_dictionary()
        remote_dict = self._fetch_remote_dictionary()
        return self._merge_dictionaries(base_dict, remote_dict)

    def _remote_startup_fetch(self):
        """Runs in a background daemon thread after the window is shown.
        Fetches remote welcome/version data and optionally the remote dictionary.
        All GUI updates are marshalled back to the main thread via self.after().
        """
        self._check_remote_welcome()
        if self.settings.get("allow_remote_dictionary", False):
            remote = self._fetch_remote_dictionary()
            if remote:
                self.after(0, self._apply_remote_dictionary_result, remote)

    def _apply_remote_dictionary_result(self, remote_dict):
        """Called on the main thread after a successful background dictionary fetch.
        Merges remote entries into the in-memory dictionary and persists new entries to disk
        so they are available on the next offline start.
        """
        base_dict = self._load_local_dictionary()
        merged = self._merge_dictionaries(base_dict, remote_dict)
        self.game_dictionary = merged
        self._rebuild_dict_patterns()

        # Persist merged result so offline starts benefit from remote entries too
        try:
            with open(self.dictionary_path, "w", encoding="utf-8") as f:
                json.dump(merged, f, ensure_ascii=False, indent=4)
            self.logger.info(
                f"Remote dictionary merged and saved: {len(remote_dict)} remote entries, "
                f"{len(merged)} total in {self.dictionary_path}"
            )
            # UI-6: update sync status label if it exists (Settings tab)
            if hasattr(self, "dict_sync_status"):
                from datetime import datetime as _dt
                self.dict_sync_status.configure(
                    text=f"Last sync: {_dt.now().strftime('%H:%M')}  ({len(remote_dict)} entries)",
                    text_color="lightgreen"
                )
        except Exception as e:
            self.logger.error(f"Failed to persist merged dictionary: {e}")
            if hasattr(self, "dict_sync_status"):
                self.dict_sync_status.configure(text="Sync failed", text_color="red")

    def _sync_remote_dictionary_now(self):
        """Force an immediate remote dictionary fetch, bypassing the rate-limit interval.
        Called from the 'Sync Now' button. Runs the fetch in a background thread
        and updates the UI status label when done.
        """
        if not self.settings.get("allow_remote_dictionary", False):
            self.status_label.configure(text="Remote dictionary is disabled in settings")
            return

        self.dict_sync_status.configure(text="Syncing...", text_color="gray")
        self.btn_sync_dict.configure(state="disabled")

        def _do_sync():
            url = self.settings.get("remote_dictionary_url", "")
            data = self._fetch_remote_json(url)
            if data and isinstance(data, dict):
                self.after(0, self._apply_remote_dictionary_result, data)
                # status label updated inside _apply_remote_dictionary_result
            else:
                self.after(0, lambda: self.dict_sync_status.configure(
                    text="Sync failed — check connection", text_color="red"))
            self.after(0, lambda: self.btn_sync_dict.configure(state="normal"))

        threading.Thread(target=_do_sync, daemon=True).start()

    # ---------------- Logger ----------------
    def _init_logger(self):
        user_home = os.path.expanduser("~")
        log_folder = os.path.join(user_home, "AppData", "Local", "ScTranslationApp", "logs")
        os.makedirs(log_folder, exist_ok=True)
        log_path = os.path.join(log_folder, "app.log")

        logger = logging.getLogger("ScTranslationApp")
        logger.setLevel(logging.INFO)

        handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)

        if not logger.handlers:
            logger.addHandler(handler)
        return logger, log_path

    # ---------------- Database ----------------
    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                category TEXT,
                username TEXT,
                message TEXT,
                translated TEXT,
                lang TEXT,
                session_id TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _db_insert_message(self, ts, category, username, message, translated, lang, session_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO messages (timestamp, category, username, message, translated, lang, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (ts, category, username, message, translated, lang, session_id))
            conn.commit()
        except Exception as e:
            self.logger.error(f"DB insert error: {e}")
        finally:
            conn.close()

    # ---------------- Dictionary substitution ----------------
    def _rebuild_dict_patterns(self):
        """Pre-compile regex patterns for all dictionary keys.
        Call whenever self.game_dictionary is replaced.
        """
        self._dict_patterns = [
            (re.compile(re.escape(k), re.IGNORECASE), v)
            for k, v in self.game_dictionary.items()
        ]

    def _apply_game_dictionary(self, text):
        """Apply all dictionary substitutions to text using cached compiled patterns."""
        if not hasattr(self, "_dict_patterns"):
            self._rebuild_dict_patterns()
        processed = text
        for pattern, replacement in self._dict_patterns:
            processed = pattern.sub(replacement, processed)
        return processed

    # ---------------- Settings actions ----------------
    def _open_settings_file(self):
        try:
            os.startfile(self.settings_path)
        except Exception as e:
            self.logger.error(f"Failed to open settings file: {e}")

    def _open_dictionary_file(self):
        try:
            os.startfile(self.dictionary_path)
        except Exception as e:
            self.logger.error(f"Failed to open dictionary file: {e}")

    def _add_dictionary_entry(self):
        """Add a new key→value entry to the local dictionary file, then reload into memory."""
        key = self.dict_key_entry.get().strip()
        value = self.dict_value_entry.get().strip()

        if not key or not value:
            self.status_label.configure(text="Enter both Key and Value to add an entry")
            return

        try:
            # Load current local file, add/overwrite the entry, save back
            local_dict = self._load_local_dictionary()
            local_dict[key] = value
            with open(self.dictionary_path, "w", encoding="utf-8") as f:
                json.dump(local_dict, f, ensure_ascii=False, indent=4)

            # Reload in-memory dictionary (local file only; remote will re-merge on next fetch)
            self.game_dictionary = self._load_local_dictionary()
            self._rebuild_dict_patterns()
            self.logger.info(f"Dictionary entry added: {key!r} → {value!r}")
            self.status_label.configure(text=f"Added: {key} → {value}")
        except Exception as e:
            self.logger.error(f"Failed to add dictionary entry: {e}")
            self.status_label.configure(text="Failed to add dictionary entry")
        finally:
            self.dict_key_entry.delete(0, "end")
            self.dict_value_entry.delete(0, "end")

    def _reload_dictionary(self):
        """Reload dictionary from disk (local file only)."""
        try:
            self.game_dictionary = self._load_local_dictionary()
            self._rebuild_dict_patterns()
            self.logger.info("Game dictionary reloaded from disk")
            self.status_label.configure(text="Dictionary reloaded from disk")
        except Exception as e:
            self.logger.error(f"Failed to reload dictionary: {e}")
            self.status_label.configure(text="Failed to reload dictionary")

    # Keep for backward compatibility with any calls from _apply_settings_changes
    def _update_dictionary_entry(self):
        """Legacy combined handler — delegates to _add_dictionary_entry or _reload_dictionary."""
        key = self.dict_key_entry.get().strip()
        value = self.dict_value_entry.get().strip()
        if key and value:
            self._add_dictionary_entry()
        else:
            self._reload_dictionary()

    def _apply_settings_changes(self):
        self.settings = self._load_settings()
        self.game_dictionary = self._load_local_dictionary()
        self._rebuild_dict_patterns()
        self.languages = self.settings["languages"]
        self.language_menu.configure(values=list(self.languages.keys()))
        self.language_var.set(self.settings["last_language"])
        self.target_lang = self.languages[self.settings["last_language"]]

        # Update manual translation language
        self.manual_translate_lang = self.settings["manual_translate_lang"]
        self.manual_languages = self.settings["manual_languages"]
        self.manual_lang_menu.configure(values=list(self.manual_languages.keys()))
        self.manual_lang_var.set(self._get_short_code_for_lang(self.manual_translate_lang))
        self.btn_translate.configure(text=self._get_short_code_for_lang(self.manual_translate_lang))

        # Sync UI toggle states with reloaded settings
        self.remote_dict_var.set(self.settings.get("allow_remote_dictionary", False))
        self.remote_override_var.set(self.settings.get("remote_dictionary_overrides_local", False))

        self.parent_folder = Path(self.settings["game_logs_path"])
        self.game_path_var.set(str(self.parent_folder))

        # Sync UI preset selector
        self.ui_preset_var.set(self.settings.get("ui_preset", UI_PRESET_DEFAULT))

        self.mymemory_email_var.set(self.settings.get("mymemory_email", ""))

        self.logger.info("Settings & dictionary reloaded")

    def _apply_ui_preset(self, preset_name: str) -> None:
        """Apply a UI size preset immediately: update fonts, window geometry, persist."""
        global APP_FONT_SIZE, APP_FONT_SIZE_SMALL, APP_FONT_SIZE_GROUP
        preset = UI_PRESETS.get(preset_name)
        if preset is None:
            return
        # Update globals so future one-off CTkFont() calls (e.g. close-confirm popup) use correct size
        APP_FONT_SIZE       = preset["font"]
        APP_FONT_SIZE_SMALL = preset["font_small"]
        APP_FONT_SIZE_GROUP = preset["font_group"]
        # Update shared font objects in-place — all referencing widgets repaint immediately
        self._fnt.configure(size=preset["font"])
        self._fnt_grp.configure(size=preset["font_group"])
        self._fnt_hint.configure(size=preset["font_small"])
        # Resize window (minsize first to avoid geometry being rejected by old minimum)
        w, h = preset["width"], preset["height"]
        self.minsize(w, h)
        self.geometry(f"{w}x{h}")
        # Resize tab segment buttons
        for btn in self.tabview._segmented_button._buttons_dict.values():
            btn.configure(width=preset["tab_w"], height=preset["tab_h"])
        # Persist
        self.settings["ui_preset"] = preset_name
        self._save_settings()
        self.logger.info(f"UI preset changed to '{preset_name}'")

    def _change_language(self, choice):
        self.target_lang = self.languages[choice]
        self.settings["last_language"] = choice
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4)
        self.logger.info(f"Language changed to {choice} ({self.target_lang})")

        # Updating dynamically the placeholder for user translated entry hint
        try:
            new_hint = self._safe_translate("Want to translate something?", self.target_lang)
        except Exception:
            new_hint = "Want to translate something?"
        self.manual_entry.configure(placeholder_text=new_hint)

    def _get_short_code_for_lang(self, lang_code):
        """Get the short code (e.g., 'ES') for a given language code (e.g., 'es')"""
        for short_code, code in self.manual_languages.items():
            if code == lang_code:
                return short_code
        return "EN"  # fallback

    def _change_manual_language(self, choice):
        # choice is already a short code like "ES", "PL", etc.
        if choice in self.manual_languages:
            lang_code = self.manual_languages[choice]
            self.manual_translate_lang = lang_code
            self.settings["manual_translate_lang"] = lang_code
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            self.logger.info(f"Manual translation language changed to {choice} ({lang_code})")
            # Update button text to show short code
            self.btn_translate.configure(text=choice)

    # ---------------- CSV Export ----------------
    def _export_history_to_csv(self):
        try:
            export_path = os.path.join(os.path.dirname(self.settings_path), "history_export.csv")
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT timestamp, category, username, message, translated, lang, session_id FROM messages ORDER BY timestamp ASC")
            rows = cur.fetchall()
            conn.close()

            with open(export_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["timestamp", "category", "username", "message", "translated", "lang", "session_id"])
                writer.writerows(rows)
            self.logger.info(f"History exported to CSV: {export_path}")
        except Exception as e:
            self.logger.error(f"CSV export failed: {e}")

    def _categorize_line(self, line: str):
        line_lower = line.lower()
        for key, category in CHAT_CATEGORIES.items():
            if key.lower() in line_lower:
                return category
        return None

    def _extract_second_bracket(self, display_line: str):
        parts = display_line.split("[")
        if len(parts) > 2:  # means at least two brackets exist
            return "" + parts[2].split("]")[0] + ""
        return None

    def _parse_line(self, line: str, category: str):
        raw_upper = line.upper()
        if any(pat.upper() in raw_upper for pat in SKIP_PATTERNS):
            return None  # skip system/technical messages

        # Extract username inside [ ]
        username_match = re.search(r"\[(.*?)\]", line)
        if username_match:
            raw_username = username_match.group(1)
            username = raw_username.lstrip()  
            # removing trailing spaces
            username = username.strip()
        else:
            username = "NotThePlayer"
    
        # Extract message text after the first ']'
        parts = line.split("]", 1)
        message_text = parts[1].strip() if len(parts) > 1 else line.strip()

        # Current app timestamp (not game timestamp)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Build separate lines
        header_line = f"[{timestamp}] [{category}] [{username}]:"
        message_line = message_text

        return timestamp, username, message_text, header_line, message_line

    # ---------------- Chat log watching ----------------
    def _get_latest_logfile(self):
        if not self.parent_folder.exists():
            return None
        subfolders = [f for f in self.parent_folder.iterdir() if f.is_dir()]
        if not subfolders:
            return None
        latest_folder = max(subfolders, key=lambda f: f.stat().st_ctime)
        log_file = latest_folder / "chat.log"
        return log_file if log_file.exists() else None

    def _watch_latest_chat(self):
        file_handle = None
        waiting_shown = False
        while not self.stop_flag:
            logfile = self._get_latest_logfile()
            # Tell the user when there is nothing to watch (e.g. wrong logs folder),
            # but never overwrite a translation-pause message.
            if logfile is None and file_handle is None and not waiting_shown:
                waiting_shown = True
                if not self._status_shows_pause:
                    self._set_status(STATUS_NO_CHAT_LOG_TEXT)
            elif logfile is not None and waiting_shown:
                waiting_shown = False
                if not self._status_shows_pause:
                    self._set_status(STATUS_DEFAULT_TEXT)
            if logfile and logfile != self.current_logfile:
                self.current_logfile = logfile
                if file_handle:
                    file_handle.close()
                try:
                    file_handle = open(self.current_logfile, "r", encoding="utf-8", errors="replace")
                    file_handle.seek(0, os.SEEK_END)
                    self.session_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-{os.path.basename(os.path.dirname(self.current_logfile))}"
                    self.logger.info(f"Switched to logfile {self.current_logfile}")
                except Exception as e:
                    self.logger.error(f"Error opening logfile {logfile}: {e}")
                    time.sleep(1)
                    continue

            if file_handle:
                line = file_handle.readline()
                if line:
                    category = self._categorize_line(line)
                    if category:
                        parsed = self._parse_line(line, category)
                        if not parsed:  # filtered system/noise line
                           continue

                        ts, username, message_text, header_line, message_line = parsed
                        processed_message = self._apply_game_dictionary(message_text)

                        if self._is_channel_translated(category):
                            translated = self._translate_for_display(processed_message, self.target_lang).text
                        else:
                            translated = ""  # channel unticked in Settings: shown, not translated

                        tag_name = f"translated_{self.target_lang}"

                        # Insert header with category-based color
                        self._insert_message_tab1(header_line, category)

                        # Insert the original message
                        self._insert_message_tab1(">   '" +message_line +"'", "original" )

                        # Insert the translated line (or just the spacing line)
                        if translated:
                            self._insert_message_tab1("→ " + translated + "\n", tag_name)
                        else:
                            self._insert_message_tab1("", "original")

                        # Save to DB
                        self._db_insert_message(ts, category, username, message_text, translated, self.target_lang, self.session_id)
                else:
                    time.sleep(0.3)
            else:
                time.sleep(2)

        if file_handle:
            file_handle.close()

    # ---------------- App Log tail ----------------
    def _tail_app_log(self):
        pointer = 0
        while not self.stop_flag:
            try:
                with open(self.app_log_path, "r", encoding="utf-8", errors="replace") as f:
                    f.seek(pointer)
                    lines = f.readlines()
                    pointer = f.tell()
                if lines:
                    self.app_log_text.configure(state="normal")
                    for line in lines:
                        self.app_log_text.insert(tk.END, line)
                    self.app_log_text.see(tk.END)
                    self.app_log_text.configure(state="disabled")
            except Exception:
                pass
            time.sleep(1)

    # ---------------- History Tab helpers ----------------
    def _load_history_for_date(self):
        date_str = self.history_date_var.get().strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT timestamp, category, username, message, translated FROM messages WHERE date(timestamp)=? ORDER BY timestamp ASC", (date_str,))
        rows = cur.fetchall()
        conn.close()

        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", tk.END)
        for r in rows:
            ts, cat, user, msg, trans = r
            self.history_text.insert(tk.END, f"[{ts}] [{cat}] [{user}]: {msg}\n→ {trans}\n\n")
        self.history_text.configure(state="disabled")

    def _load_history_last_session(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT session_id FROM messages ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        if row:
            last_sess = row[0]
            cur.execute("SELECT timestamp, category, username, message, translated FROM messages WHERE session_id=? ORDER BY timestamp ASC", (last_sess,))
            rows = cur.fetchall()
        else:
            rows = []
        conn.close()

        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", tk.END)
        for r in rows:
            ts, cat, user, msg, trans = r
            self.history_text.insert(tk.END, f"[{ts}] [{cat}] [{user}]: {msg}\n→ {trans}\n\n")
        self.history_text.configure(state="disabled")

    # ---------------- Insert helpers ----------------
    def _insert_message_tab1(self, text, tag=None):
        # Unlock → insert → scroll → lock
        self.text_area_tab1.configure(state="normal")
        self.text_area_tab1.insert("end", text + "\n", tag)
        self.text_area_tab1.see("end")
        self.text_area_tab1.configure(state="disabled")

    # ------------- Remote dictionary helpers --------------
    def _toggle_remote_dictionary(self):
        self.settings["allow_remote_dictionary"] = self.remote_dict_var.get()
        self._save_settings()
        self.logger.info(f"Remote dictionary {'enabled' if self.remote_dict_var.get() else 'disabled'}")

    def _toggle_remote_override(self):
        self.settings["remote_dictionary_overrides_local"] = self.remote_override_var.get()
        self._save_settings()
        self.logger.info(
            f"Remote dictionary override {'enabled' if self.remote_override_var.get() else 'disabled'}"
        )

    # ---------------- Misc ----------------
    def _browse_game_folder(self):
        folder = filedialog.askdirectory(title="Select StarConflict logs folder")
        if folder:
            self.game_path_var.set(folder)

    def _save_game_path(self):
        new_path = self.game_path_var.get()
        if os.path.isdir(new_path):
            self.settings["game_logs_path"] = new_path
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            self.parent_folder = Path(new_path)
            self.logger.info(f"Game logs path changed to {new_path}")
        else:
            self.logger.warning("Invalid game logs path entered")

    def _reset_game_path(self):
        default_path = self._get_default_logs_path()
        self.settings["game_logs_path"] = default_path
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4)
        self.parent_folder = Path(default_path)
        self.game_path_var.set(str(default_path))
        self.logger.info("Game logs path reset to default")

    def _open_app_log_file(self):
        try:
            os.startfile(self.app_log_path)
        except Exception:
            pass

    def _prevent_move(self, event):
        """Prevent the main window from being moved while popup is active."""
        if event.widget == self:
            # If dimensions haven't changed, it's a move - restore position
            if event.width == self.winfo_width() and event.height == self.winfo_height():
                if event.x != self._original_x or event.y != self._original_y:
                    self.geometry(f"+{self._original_x}+{self._original_y}")

    def _show_close_confirmation(self):
        """Show close confirmation popup with minimize, close, cancel options."""
        # Freeze the main window position
        self._original_x = self.winfo_x()
        self._original_y = self.winfo_y()
        self._freeze_handler = self.bind('<Configure>', self._prevent_move)

        popup = ctk.CTkToplevel(self)
        popup.title("Close Confirmation")
        popup.geometry("300x150")
        popup.resizable(False, False)

        # Center the popup on the main window
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_w = self.winfo_width()
        main_h = self.winfo_height()
        popup_w = 300
        popup_h = 150
        popup_x = main_x + (main_w - popup_w) // 2
        popup_y = main_y + (main_h - popup_h) // 2
        popup.geometry(f"{popup_w}x{popup_h}+{popup_x}+{popup_y}")

        # Always on top and modal
        popup.attributes("-topmost", True)
        popup.transient(self)
        popup.grab_set()

        # Handle X button as cancel
        popup.protocol("WM_DELETE_WINDOW", lambda: [popup.destroy(), self._unfreeze_window()])

        # Label
        label = ctk.CTkLabel(popup, text="Are you sure you want to close the application?",
                             font=ctk.CTkFont(size=APP_FONT_SIZE))
        label.pack(pady=20, padx=20)

        # Button frame
        button_frame = ctk.CTkFrame(popup, fg_color='transparent')
        button_frame.pack(pady=(0, 20))

        # Minimize button
        minimize_btn = ctk.CTkButton(button_frame, text="Minimize", width=80,
                                   font=ctk.CTkFont(size=APP_FONT_SIZE),
                                   command=lambda: [self.iconify(), popup.destroy(), self._unfreeze_window()])
        minimize_btn.pack(side="left", padx=5)

        # Close button
        close_btn = ctk.CTkButton(button_frame, text="Close", width=80,
                                  font=ctk.CTkFont(size=APP_FONT_SIZE), command=self._close_app)
        close_btn.pack(side="left", padx=5)

        # Cancel button
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", width=80,
                                 font=ctk.CTkFont(size=APP_FONT_SIZE),
                                 command=lambda: [popup.destroy(), self._unfreeze_window()])
        cancel_btn.pack(side="left", padx=5)

    def _unfreeze_window(self):
        """Restore normal window behavior after popup closes."""
        if hasattr(self, '_freeze_handler'):
            self.unbind('<Configure>', self._freeze_handler)
            delattr(self, '_freeze_handler')
            if hasattr(self, '_original_x'):
                delattr(self, '_original_x')
            if hasattr(self, '_original_y'):
                delattr(self, '_original_y')

    def _close_app(self):
        """Properly close the application."""
        self.stop_flag = True
        self.logger.info("Application closed")
        self.destroy()

    def _on_close(self):
        self._show_close_confirmation()

    def _check_version_in_help(self):
        """Check for updates and display results in help section"""
        self.version_status_label.configure(text="Checking for updates...")
        # Temporarily change link color to indicate it's processing
        self.check_updates_link.configure(text_color="gray")

        try:
            # Force version check (bypass interval)
            data = self._fetch_remote_json(DEFAULT_REMOTE_WELCOME_URL)

            if not data:
                self._show_help_version_result("Unable to check for updates. Please try again later.")
                return

            # Handle array format
            if isinstance(data, list) and data:
                data = data[0]

            remote_version = data.get('version', '').strip()
            if not remote_version:
                self._show_help_version_result("Version information not available.")
                return

            comparison = compare_versions(remote_version, APP_VERSION)
            if comparison == 1:
                # New version available
                self._show_help_update_info_from_data(data)
            else:
                self._show_help_version_result(f"You have the latest version ({APP_VERSION})")

        except Exception as e:
            self._show_help_version_result(f"Error checking for updates: {str(e)}")
        finally:
            # Restore link color
            self.check_updates_link.configure(text_color=LINK_COLOR)

    def _show_help_version_result(self, message):
        """Display version check result in help section"""
        self.version_status_label.configure(text=message)
        self.update_title_label.configure(text="")
        self.update_changes_label.configure(text="")
        self.update_download_label.configure(text="")
        self.update_notes_label.configure(text="")

    def _show_help_update_info_from_data(self, data):
        """Display update information in help section from remote data"""
        self.version_status_label.configure(text="Update Available!")

        version = data.get('version', 'Unknown')
        whats_new = data.get('whats_new', {})
        download_url = data.get('download_url', '')
        notes = data.get('notes', '')

        # Update title
        self.update_title_label.configure(text=f"New version {version} is available!")

        # Update changes
        if whats_new and whats_new.get('changes'):
            changes_text = "What's new:\n" + "\n".join(f"• {change}" for change in whats_new['changes'])
            self.update_changes_label.configure(text=changes_text)
        else:
            self.update_changes_label.configure(text="")

        # Update download link
        if download_url:
            self.update_download_label.configure(text=f"Download: {download_url}")
            self.update_download_label.bind("<Button-1>", lambda e: self._open_link(download_url))
        else:
            self.update_download_label.configure(text="")

        # Update notes
        if notes:
            self.update_notes_label.configure(text=f"Notes: {notes}")
        else:
            self.update_notes_label.configure(text="")

    def _open_link(self, url):
        """Open URL in default browser"""
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Failed to open link: {e}")

    def _open_email(self, email):
        """Open email client with address"""
        try:
            webbrowser.open(f"mailto:{email}")
        except Exception as e:
            print(f"Failed to open email: {e}")

def resource_path(rel_path: str) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller build.
    rel_path: path relative to project (e.g. 'assets/logo.ico')
    """
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel_path)

SMOKE_TEST_FILES = ("assets/logo.ico", "assets/help_blue.png", "game_dictionary.json")


def smoke_test():
    """Check that this build can start, without opening the app or using the network.

    Used by scripts/build_exe.py on the packaged exe: verifies the bundled files, that
    the third-party libraries import, and that Tk can create a window. Returns a list
    of problems (empty = OK).
    """
    problems = []
    for rel in SMOKE_TEST_FILES:
        if not os.path.isfile(resource_path(rel)):
            problems.append(f"missing bundled file: {rel}")
    try:
        with open(resource_path("game_dictionary.json"), encoding="utf-8") as f:
            json.load(f)
        Image.open(resource_path("assets/help_blue.png")).load()
        MyMemoryTranslator(to_lang="en", from_lang=_MYMEMORY_AUTODETECT)
        root = ctk.CTk()
        root.withdraw()
        ctk.CTkLabel(root, text="ok", font=ctk.CTkFont(size=11)).pack()
        root.update()
        root.destroy()
    except Exception as e:
        problems.append(f"{type(e).__name__}: {e}")
    return problems


def main():
    """Entry point for the `sc-chat-translator` console script (see pyproject.toml)."""
    if "--smoke-test" in sys.argv:
        # A windowed exe has no console, so the result goes to a file when one is given.
        problems = smoke_test()
        report = f"SC Chat Translator {APP_VERSION}: " + ("; ".join(problems) or "OK")
        idx = sys.argv.index("--smoke-test")
        if idx + 1 < len(sys.argv):
            with open(sys.argv[idx + 1], "w", encoding="utf-8") as f:
                f.write(report + "\n")
        else:
            print(report)
        sys.exit(1 if problems else 0)
    app = TranslatedFileWatcher()
    app.mainloop()


if __name__ == "__main__":
    main()
