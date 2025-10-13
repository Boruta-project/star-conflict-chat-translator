import sys, os
import time
import threading
import tkinter as tk
import customtkinter as ctk
from PIL import Image
import json
import logging
from logging.handlers import RotatingFileHandler
from googletrans import Translator
from pathlib import Path
from tkinter import filedialog
from datetime import datetime
import re
import sqlite3
import csv
import pyperclip  # copy translated user entry to clipboard
import webbrowser  # for opening links
import asyncio

# --- Libraries for HTTP fetch ---
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# -----------------------
# Global configuration
# -----------------------

APP_VERSION = "1.1.3"
APP_AUTHOR = "Hystrix"
AUTHOR_EMAIL = "borutaproject@gmail.com"

# Default application window geometry
DEFAULT_WINDOW_WIDTH = 640
DEFAULT_WINDOW_HEIGHT = 670

BUTTON_HEIGHT = 22

# Help window dimensions (relative to main window)
HELP_WINDOW_WIDTH_RATIO = 0.8  # 80% of main window width
HELP_WINDOW_HEIGHT_RATIO = 1.0  # 100% of main window height

# Status bar layout ratios
STATUS_LABEL_RATIO = 0.9  # 90% for status label
HELP_BUTTON_RATIO = 0.1   # 10% for help button

# Link styling
LINK_COLOR = "#4A90E2"  # Blue for clickable links
LINK_CURSOR = "hand2"   # Hand cursor for links

# Help content styling
HELP_SECTION_SPACING = 10  # Spacing between sections eg 15
HELP_CONTENT_PADDING = 15  # Padding for content areas eg 20

# GUI configuration
GUI_RESIZABLE = False  # Set to False by default for consistent layout

DEFAULT_REMOTE_WELCOME_URL = "https://api.jsonsilo.com/public/d03caeff-8d84-4b55-bd8c-4b9ad6e7d372"
DEFAULT_REMOTE_DICTIONARY_URL = "https://api.jsonsilo.com/public/245adbbb-9613-47ab-96bb-0e3e40385700"

# Project links
PROJECT_REPOSITORY_URL = "https://github.com/boruta-project/star-conflict-chat-translator"
USER_MANUAL_URL = "https://sites.google.com/view/sc-chat-translator/"

DEFAULT_SETTINGS = {
    "last_language": "English",
    "manual_translate_lang": "ru",
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
    "last_notified_version": APP_VERSION,
    "last_remote_fetch": 0,
    "remote_fetch_interval": 3600,  # 1 hour in seconds
    "show_extended_welcome": False,  # Flag to show extended message after version update
    # Extended welcome message fields (populated from remote)
    "remote_welcome_message": "",
    "remote_whats_new": None,
    "remote_download_url": "",
    "remote_notes": ""
}

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
    "The application uses the Google Translation engine and does not interfere with the game code.\n"
    "Check your preferences in the Settings tab.\n\n"
    "Feel free to share your feedback about this program with me.\n"
    )

def run_async_translation(coro):
    """Helper to run async translation coroutines, handling event loop issues."""
    try:
        return asyncio.run(coro)
    except RuntimeError as e:
        if "Event loop is closed" in str(e) or "There is no current event loop" in str(e):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
        else:
            raise


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

        # Load and save settings to guarantee consistency
        self.settings_path = self._get_settings_path()   #
        self.settings = self._load_settings()            # load settings (creates file on first run)
        self._save_settings()                            # ensure settings file has all defaults

        # --- Logger (initialize early to avoid issues with remote fetches) ---
        self.logger, self.app_log_path = self._init_logger()
        self.logger.info("Application started")

        # GUI configuration
        self.title("SC Chat Translator "+APP_VERSION)
        # self.geometry("640x670") - optimal application window size
        self.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
        self.resizable(GUI_RESIZABLE, GUI_RESIZABLE)  # Use global setting

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
        self.game_dictionary = self._load_dictionary()

        self.settings.setdefault("welcome_counter", 0)

        # --- DB init ---
        self.db_path = self._get_db_path()
        self._init_database()

        # --- Paths / translator / state ---
        self.parent_folder = Path(self.settings["game_logs_path"])
        self.translator = Translator()
        self.stop_flag = False
        self.current_logfile = None
        self.session_id = None

        self.languages = self.settings["languages"]
        self.manual_languages = self.settings["manual_languages"]
        self.target_lang = self.languages[self.settings["last_language"]]
        self.manual_translate_lang = self.settings["manual_translate_lang"]

        # --- Status Bar with Help Button ---
        self.status_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.status_frame.pack(fill="x", padx=10, pady=5)

        # Status label (90% width)
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Processing chat.log...",
            anchor="w"
        )
        self.status_label.pack(side="left", fill="x", expand=True)

        # Help button (10% width)
        self.help_button = ctk.CTkButton(
            self.status_frame,
            image=self.help_icon_img,
            text="",
            width=int(DEFAULT_WINDOW_WIDTH * HELP_BUTTON_RATIO * 0.1),  # Small button
            height=BUTTON_HEIGHT,
            command=self._toggle_help_content
        )
        self.help_button.pack(side="right", padx=(5, 0))

        # --- Main Content Container ---
        self.main_content_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.main_content_frame.pack(fill="both", expand=True, padx=0, pady=10)

        # --- Tabs ---
        self.tabview = ctk.CTkTabview(self.main_content_frame, width=625, height=575)
        self.tabview.pack(fill="both", expand=True, padx=0, pady=0)

        self.tab1 = self.tabview.add("Chat")
        self.tab_history = self.tabview.add("History")
        self.tab_log = self.tabview.add("App Log")
        self.tab3 = self.tabview.add("Settings")

        for button in self.tabview._segmented_button._buttons_dict.values():
            button.configure(width=125, height=20)

        # --- Help Content Frame (initially hidden) ---
        self.help_content_frame = ctk.CTkScrollableFrame(self.main_content_frame)
        self.help_content_frame.pack(fill="both", expand=True, padx=0, pady=0)
        self.help_content_frame.pack_forget()  # Hide initially

        # --- Chat Text areas ---
        self.text_area_tab1 = ctk.CTkTextbox(self.tab1, wrap=tk.WORD)
        self.text_area_tab1.pack(expand=True, fill="both", padx=10, pady=10)

        # # --- User translation output area ---
        # self.text_area_tab1.tag_config("manual_header", foreground="gold")  # or any color
        # self.text_area_tab1.tag_config("version_update", foreground="gold")

        # --- Welcome message shown at startup ---
        self._insert_hardcoded_message()

        # --- Check remote welcome first ---
        self._check_remote_welcome()  # may reset welcome_counter and set override text

        if self.settings["welcome_counter"] < 11:
            # Check if we should show extended message (new version detected)
            show_extended = self.settings.get("show_extended_welcome", False)

            if show_extended:
                # Show extended message with all fields (whats_new, changes, notes, download_url)
                self._insert_extended_welcome_message()
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
        bottom_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Dynamic placeholder translation
        placeholder_hint = self._safe_translate(MANUAL_TRANSLATE_PROMPT, self.target_lang)
        self.manual_entry = ctk.CTkEntry(bottom_frame, placeholder_text=placeholder_hint, width=500)
        self.manual_entry.pack(side="left", padx=(5, 10), pady=5, expand=True, fill="x")

        # Button showing short language code
        self.btn_translate = ctk.CTkButton(
            bottom_frame,
            text=self._get_short_code_for_lang(self.manual_translate_lang),
            width=50,
            command=self._manual_translate
        )
        self.btn_translate.pack(side="left", padx=(0, 5), pady=5)

        # Bind Enter key to trigger translation
        self.manual_entry.bind("<Return>", lambda e: self._manual_translate())

        
        # --- History tab ---
        top_hist = ctk.CTkFrame(self.tab_history)
        top_hist.pack(fill="x", padx=10, pady=(10, 0))

        ctk.CTkLabel(top_hist, text="Date (YYYY-MM-DD):").pack(side="left", padx=(10, 5), pady=10)
        self.history_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.history_date_entry = ctk.CTkEntry(top_hist, textvariable=self.history_date_var, width=160)
        self.history_date_entry.pack(side="left", padx=(0, 10), pady=10)

        self.btn_load_date = ctk.CTkButton(top_hist, text="Load Date", command=self._load_history_for_date)
        self.btn_load_date.pack(side="left", padx=5, pady=10)

        self.btn_load_last_session = ctk.CTkButton(top_hist, text="Load Last Session", command=self._load_history_last_session)
        self.btn_load_last_session.pack(side="left", padx=5, pady=10)

        self.history_text = ctk.CTkTextbox(self.tab_history, wrap=tk.WORD)
        self.history_text.pack(expand=True, fill="both", padx=10, pady=10)
        self.history_text.configure(state="disabled")


        # --- App Log tab ---
        top_log = ctk.CTkFrame(self.tab_log)
        top_log.pack(fill="x", padx=10, pady=(10, 0))

        self.btn_open_log = ctk.CTkButton(top_log, text="Open Log File", command=self._open_app_log_file)
        self.btn_open_log.pack(side="left", padx=10, pady=10)

        self.app_log_text = ctk.CTkTextbox(self.tab_log, wrap=tk.WORD)
        self.app_log_text.pack(expand=True, fill="both", padx=10, pady=10)
        self.app_log_text.configure(state="disabled")


        # --- Settings tab ---
        # Single centered label above the columns
        ctk.CTkLabel(self.tab3, text="Translation languages").pack(pady=(10, 5))

        # Create main container for two-column layout
        main_container = ctk.CTkFrame(self.tab3, fg_color='transparent')
        main_container.pack(fill="both", expand=False, padx=10, pady=(0, 10))

        # Left column
        left_column = ctk.CTkFrame(main_container)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 2))

        # Right column
        right_column = ctk.CTkFrame(main_container)
        right_column.pack(side="right", fill="both", expand=True, padx=(2, 0))

        # Left column content
        # Chat translation language picker
        row = ctk.CTkFrame(left_column)
        row.pack(pady=3, padx=(0, 20))

        icon = ctk.CTkLabel(row, image=self.help_icon_img, text="", cursor="question_arrow")
        icon.pack(side="left", padx=(0, 9))

        self.language_var = tk.StringVar(value=self.settings["last_language"])
        self.language_menu = ctk.CTkOptionMenu(
            row,
            values=list(self.languages.keys()),
            variable=self.language_var,
            command=self._change_language,
            height=BUTTON_HEIGHT,
        )
        self.language_menu.pack(side="left", padx=(0, 5))

        ToolTip(icon, "Select the language into which the game chat should be translated")

        # Open Settings File button
        row = ctk.CTkFrame(left_column)
        row.pack(pady=3, padx=(0, 20))

        icon = ctk.CTkLabel(row, image=self.help_icon_img, text="", cursor="question_arrow")
        icon.pack(side="left", padx=(0, 9))

        btn = ctk.CTkButton(row, text="Open Settings File", height=BUTTON_HEIGHT, command=self._open_settings_file)
        btn.pack(side="left", padx=(0, 5))

        ToolTip(icon, "Manually change the language settings in the JSON file using the default editor.")

        # Right column content
        # Manual translation language picker
        row = ctk.CTkFrame(right_column)
        row.pack(pady=3, padx=(0, 20))

        icon = ctk.CTkLabel(row, image=self.help_icon_img, text="", cursor="question_arrow")
        icon.pack(side="left", padx=(0, 9))

        self.manual_lang_var = tk.StringVar(value=self._get_short_code_for_lang(self.manual_translate_lang))
        self.manual_lang_menu = ctk.CTkOptionMenu(
            row,
            values=list(self.manual_languages.keys()),
            variable=self.manual_lang_var,
            command=self._change_manual_language,
            height=BUTTON_HEIGHT,
        )
        self.manual_lang_menu.pack(side="left", padx=(0, 5))

        ToolTip(icon, "Select the language for manual text translation input")

        # Apply Changes button
        row = ctk.CTkFrame(right_column)
        row.pack(pady=3, padx=(0, 20))

        icon = ctk.CTkLabel(row, image=self.help_icon_img, text="", cursor="question_arrow")
        icon.pack(side="left", padx=(0, 9))

        btn = ctk.CTkButton(row, text="Apply Changes", height=BUTTON_HEIGHT, command=self._apply_settings_changes)
        btn.pack(side="left", padx=(0, 5))

        ToolTip(icon, "Reloads settings and dictionary from disk without restarting the app.")


        # Game logs section
        ctk.CTkLabel(self.tab3, text="StarConflict game logs folder:").pack(pady=(10, 5))

        self.game_path_var = tk.StringVar(value=str(self.parent_folder))
        self.game_path_entry = ctk.CTkEntry(self.tab3, textvariable=self.game_path_var, width=600)
        self.game_path_entry.pack(pady=5)

        # Third button - Browse with Tooltip to the left
        row = ctk.CTkFrame(self.tab3)
        row.pack(pady=3, padx=(0, 20))   # shift entire row 20px to the left

        icon = ctk.CTkLabel(row, image=self.help_icon_img, text="", cursor="question_arrow")
        icon.pack(side="left", padx=(0, 9))

        # Main button
        btn = ctk.CTkButton(row, text="Browse", height=BUTTON_HEIGHT, command=self._browse_game_folder)
        btn.pack(side="left", padx=(0, 5))
        
        # Tooltip bound to the icon only
        ToolTip(icon, "If the application is unable to locate the game folder automatically,\n" \
        " select the folder named 'logs' where Star Conflict saves its chat.log files manually.")

        # Fourth button - Save Path with Tooltip to the left
        row = ctk.CTkFrame(self.tab3)
        row.pack(pady=3, padx=(0, 20))   # shift entire row 20px to the left

        icon = ctk.CTkLabel(row, image=self.help_icon_img, text="", cursor="question_arrow")
        icon.pack(side="left", padx=(0, 9))

        # Main button
        btn = ctk.CTkButton(row, text="Save Path", height=BUTTON_HEIGHT, command=self._save_game_path)
        btn.pack(side="left", padx=(0, 5))
        
        # Tooltip bound to the icon only
        ToolTip(icon, "Save the previously selected path to the game's 'logs' folder.")

        # Fifth button - Reset to Default Path with Tooltip to the left
        row = ctk.CTkFrame(self.tab3)
        row.pack(pady=3, padx=(0, 20))   # shift entire row 20px to the left

        icon = ctk.CTkLabel(row, image=self.help_icon_img, text="", cursor="question_arrow")
        icon.pack(side="left", padx=(0, 9))

        # Main button
        btn = ctk.CTkButton(row, text="Reset to Default Path", height=BUTTON_HEIGHT, command=self._reset_game_path)
        btn.pack(side="left", padx=(0, 5))
        
        # Tooltip bound to the icon only
        ToolTip(icon, "Reset the default path to the game folder named 'logs'.")

        # NEW: Export History to CSV
        # self.export_csv_button = ctk.CTkButton(self.tab3, text="Export History to CSV", command=self._export_history_to_csv)
        # self.export_csv_button.pack(pady=15)

        # Open Game Dictionary
        ctk.CTkLabel(self.tab3, text="Change custom dictionary settings:").pack(pady=(10, 5))

        # Sixth button - Open Game Dictionary with Tooltip to the left
        row = ctk.CTkFrame(self.tab3)
        row.pack(pady=3, padx=(0, 20))   # shift entire row 20px to the left

        icon = ctk.CTkLabel(row, image=self.help_icon_img, text="", cursor="question_arrow")
        icon.pack(side="left", padx=(0, 9))

        # Main button
        btn = ctk.CTkButton(row, text="Open Game Dictionary", height=BUTTON_HEIGHT, command=self._open_dictionary_file)
        btn.pack(side="left", padx=(0, 5))
        
        # Tooltip bound to the icon only
        ToolTip(icon, "Open the custom game dictionary to manually make changes to this file.")

        # Entry fields for adding/updating dictionary entries with frame for side-by-side entries.

        ctk.CTkLabel(self.tab3, text="Add new entries to the custom dictionary").pack(pady=(5, 5)) 

        self.dict_entry_frame = ctk.CTkFrame(self.tab3)
        self.dict_entry_frame.pack(pady=5)

        self.dict_key_entry = ctk.CTkEntry(self.dict_entry_frame, placeholder_text="Key", width=120)
        self.dict_key_entry.pack(side="left", padx=5)

        self.dict_value_entry = ctk.CTkEntry(self.dict_entry_frame, placeholder_text="Value", width=200)
        self.dict_value_entry.pack(side="left", padx=5)

        # Seventh button - Update / Reload Dictionary with Tooltip to the left
        row = ctk.CTkFrame(self.tab3)
        row.pack(pady=3, padx=(0, 20))   # shift entire row 20px to the left

        icon = ctk.CTkLabel(row, image=self.help_icon_img, text="", cursor="question_arrow")
        icon.pack(side="left", padx=(0, 9))

        # Main button
        btn = ctk.CTkButton(row, text="Update / Reload Dictionary", height=BUTTON_HEIGHT, command=self._update_dictionary_entry)
        btn.pack(side="left", padx=(0, 5))
        
        # Tooltip bound to the icon only    
        ToolTip(icon, "Confirm and reload the settings of the changes made in the game dictionary.")

        # Remote dictionary option
        self.remote_dict_var = tk.BooleanVar(value=self.settings.get("allow_remote_dictionary", False))

        row = ctk.CTkFrame(self.tab3)
        row.pack(pady=3, padx=(0, 20))

        icon = ctk.CTkLabel(row, image=self.help_icon_img, text="", cursor="question_arrow")
        icon.pack(side="left", padx=(0, 9))

        remote_switch = ctk.CTkSwitch(
            row,
            text="Allow remote dictionary download",
            variable=self.remote_dict_var,
            command=self._toggle_remote_dictionary,
            onvalue=True,
            offvalue=False
        )
        remote_switch.pack(side="left", padx=(0, 5))

        # Tooltip for help icon
        ToolTip(icon, "Enable or disable downloading a remote dictionary. When enabled,\n"
                    "the app will merge entries from the remote dictionary into your local one.")


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

        # redundant chat message message
        # Insert into chat with proper styling
        # self.text_area_tab1.configure(state="normal")
        # self.text_area_tab1.insert("end", translated_msg, "version_update")
        # self.text_area_tab1.configure(state="disabled")
        # self.text_area_tab1.see("end")
        # Ensure tag is configured
        # self.text_area_tab1.tag_config("version_update", foreground="gold") #???

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
            translator = Translator()
            result = run_async_translation(translator.translate(text, dest=dest))
            if result and hasattr(result, "text"):
                return result.text
        except Exception as e:
            self.logger.warning(f"Translation failed: {e}")
        return text


    def _manual_translate(self):
        text = self.manual_entry.get().strip()
        if not text:
            return

        try:
            translator = Translator()
            result = run_async_translation(translator.translate(text, dest=self.manual_translate_lang))
            translated = result.text
        except Exception as e:
            translated = f"[Translation error: {e}]"
            self.logger.error(f"Manual translation error: {e}")

        # Copy to clipboard
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
        user_home = os.path.expanduser("~")
        return os.path.join(user_home, "Documents", "My Games", "StarConflict", "logs")

    def _get_db_path(self):
        user_home = os.path.expanduser("~")
        db_dir = os.path.join(user_home, "AppData", "Local", "ScTranslationApp", "database")
        os.makedirs(db_dir, exist_ok=True)
        return os.path.join(db_dir, "chat_history.db")

    def _fetch_remote_dictionary(self):
        """Download remote dictionary JSON if enabled."""
        if not self.settings.get("allow_remote_dictionary", False):
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
        """Merge remote dictionary into base without overwriting (case-insensitive)."""
        merged = dict(base)  # copy base
        base_keys_lower = {k.lower() for k in base.keys()}

        for key, val in remote.items():
            if key.lower() not in base_keys_lower:
                merged[key] = val
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

                # Ensure backwards compatibility
                for key, value in DEFAULT_SETTINGS.items():
                    if key not in settings:
                        settings[key] = value

                # Special handling for manual_languages - ensure it exists
                if "manual_languages" not in settings:
                    settings["manual_languages"] = DEFAULT_SETTINGS["manual_languages"]

                # Ensure last_notified_version exists for backward compatibility
                if "last_notified_version" not in settings:
                    settings["last_notified_version"] = APP_VERSION

                # Ensure remote fetch settings exist for performance optimization
                if "last_remote_fetch" not in settings:
                    settings["last_remote_fetch"] = 0
                if "remote_fetch_interval" not in settings:
                    settings["remote_fetch_interval"] = 3600

                # Handle migration from old welcome_message_override to new structure
                if "welcome_message_override" in settings:
                    # Migrate old content to remote_welcome_message if it's not already set
                    old_content = settings.get("welcome_message_override", "").strip()
                    if old_content and not settings.get("remote_welcome_message"):
                        settings["remote_welcome_message"] = old_content
                    # Remove the old field to clean up
                    del settings["welcome_message_override"]

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
            self.logger.warning(f"Remote welcome fetch failed: {e}")
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
        Includes performance optimization with fetch interval checking.
        """
        # TEMPORARILY DISABLE FETCH INTERVAL FOR DEBUGGING
        # For welcome messages, use a shorter interval (5 minutes) to allow more frequent checks
        # last_fetch = self.settings.get("last_remote_fetch", 0)
        # current_time = time.time()
        # welcome_interval = 300  # 5 minutes for welcome messages

        # if current_time - last_fetch <= welcome_interval:
        #     self.logger.info(f"Skipping remote fetch - last fetch was {current_time - last_fetch:.0f} seconds ago (interval: {welcome_interval}s)")
        #     return False

        url = DEFAULT_REMOTE_WELCOME_URL
        data = self._fetch_remote_json(url)

        # Always update fetch time, even if fetch failed
        self._update_fetch_time()

        if not data:
            self.logger.warning("No data received from remote welcome URL")
            return False

        # Handle if data is list (new format)
        if isinstance(data, list) and data:
            data = data[0]

        self.logger.info(f"=== RAW REMOTE DATA RECEIVED ===")
        self.logger.info(f"Data type: {type(data)}")
        self.logger.info(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
        for key, value in data.items():
            if key == 'welcome_message':
                self.logger.info(f"{key}: (length: {len(str(value))})")
            else:
                self.logger.info(f"{key}: {value}")

        # Get welcome message (now the main content is in 'welcome_message')
        welcome_msg = data.get('welcome_message', '').strip()
        new_color = str(data.get("color", "DodgerBlue")).strip() or "DodgerBlue"
        new_id = str(data.get("id", "")).strip()

        self.logger.info(f"=== PROCESSED DATA ===")
        self.logger.info(f"Remote data: id={new_id}, welcome_msg_length={len(welcome_msg)}, color={new_color}")
        self.logger.info(f"Welcome message preview: '{welcome_msg[:100]}...'")

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

            self.logger.info(f"=== CONTENT COMPARISON DEBUG ===")
            self.logger.info(f"ID comparison: prev_id={prev_id}, new_id={new_id}, is_newer={is_newer_id}, is_older={is_older_id}")
            self.logger.info(f"Welcome changed: '{current_welcome[:30]}...' != '{welcome_msg[:30]}...' = {welcome_changed}")
            self.logger.info(f"Whats new changed: {whats_new_changed}")
            self.logger.info(f"Download changed: {download_changed}")
            self.logger.info(f"Notes changed: {notes_changed}")
            self.logger.info(f"Overall content_changed: {content_changed}")

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

    def _load_dictionary(self):
        # Load local dictionary first
        if not os.path.exists(self.dictionary_path):
            default_dict = DEFAULT_DICTIONARY.copy()
            with open(self.dictionary_path, "w", encoding="utf-8") as f:
                json.dump(default_dict, f, indent=4)
            base_dict = default_dict
        else:
            with open(self.dictionary_path, "r", encoding="utf-8") as f:
                base_dict = json.load(f)

        # Optionally merge remote
        remote_dict = self._fetch_remote_dictionary()
        merged = self._merge_dictionaries(base_dict, remote_dict)
        return merged

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
    def _apply_game_dictionary(self, text):
        processed = text
        for key, replacement in self.game_dictionary.items():
            # Replace ignoring case
            pattern = re.compile(re.escape(key), re.IGNORECASE)
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

    def _update_dictionary_entry(self):
        key = self.dict_key_entry.get().strip()
        value = self.dict_value_entry.get().strip()

        try:
            if key and value:
                # --- Case 1: Add/update dictionary entry
                self.game_dictionary[key] = value

                with open(self.dictionary_path, "w", encoding="utf-8") as f:
                    json.dump(self.game_dictionary, f, ensure_ascii=False, indent=4)

                self.logger.info(f"Dictionary updated: {key} → {value}")
                self.status_label.configure(text=f"Dictionary updated: {key} → {value}")

            else:
                # --- Case 2: Reload dictionary from file
                self.logger.info("Reloading dictionary from file...")
                self.status_label.configure(text="Dictionary reloaded from file")

            # --- In both cases: reload into memory
            self.game_dictionary = self._load_dictionary()

        except Exception as e:
            self.logger.error(f"Failed to update/reload dictionary: {e}")
            self.status_label.configure(text="Failed to update/reload dictionary")

        finally:
            # Always clear fields after action
            self.dict_key_entry.delete(0, "end")
            self.dict_value_entry.delete(0, "end")

    def _reload_dictionary(self):
        try:
            self.game_dictionary = self._load_dictionary()
            self.logger.info("Custom game dictionary reloaded")
            self.status_label.configure(text="Dictionary reloaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to reload dictionary: {e}")
            self.status_label.configure(text="Failed to reload dictionary")

    def _apply_settings_changes(self):
        self.settings = self._load_settings()
        self.game_dictionary = self._load_dictionary()
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

        self.parent_folder = Path(self.settings["game_logs_path"])
        self.game_path_var.set(str(self.parent_folder))
        self.logger.info("Settings & dictionary reloaded")

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
        while not self.stop_flag:
            logfile = self._get_latest_logfile()
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

                        try:
                            translator = Translator()
                            result = run_async_translation(translator.translate(processed_message, dest=self.target_lang))
                            translated = result.text
                        except Exception as e:
                            translated = f"[Translation error: {e}]"
                            self.logger.error(f"Translation error: {e}")

                        tag_name = f"translated_{self.target_lang}"

                        # Insert header with category-based color
                        self._insert_message_tab1(header_line, category)

                        # Insert the original message
                        self._insert_message_tab1(">   '" +message_line +"'", "original" )

                        # Insert the translated line
                        self._insert_message_tab1("→ " + translated + "\n", tag_name)

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

    # ------------- Remote dictionary helper --------------
    def _toggle_remote_dictionary(self):
        self.settings["allow_remote_dictionary"] = self.remote_dict_var.get()
        self._save_settings()
        # reload immediately after switching
        self.game_dictionary = self._load_dictionary()
        self.logger.info(f"Remote dictionary {'enabled' if self.remote_dict_var.get() else 'disabled'}")

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
        label = ctk.CTkLabel(popup, text="Are you sure you want to close the application?")
        label.pack(pady=20, padx=20)

        # Button frame
        button_frame = ctk.CTkFrame(popup, fg_color='transparent')
        button_frame.pack(pady=(0, 20))

        # Minimize button
        minimize_btn = ctk.CTkButton(button_frame, text="Minimize", width=80,
                                   command=lambda: [self.iconify(), popup.destroy(), self._unfreeze_window()])
        minimize_btn.pack(side="left", padx=5)

        # Close button
        close_btn = ctk.CTkButton(button_frame, text="Close", width=80, command=self._close_app)
        close_btn.pack(side="left", padx=5)

        # Cancel button
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", width=80,
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
        self.version_status_label.configure(text="Check complete")
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

if __name__ == "__main__":
    app = TranslatedFileWatcher()
    app.mainloop()
