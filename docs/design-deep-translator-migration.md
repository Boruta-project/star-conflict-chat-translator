# Design: Replace `googletrans` with `deep-translator`

| | |
|---|---|
| **Target release** | 1.3.0 |
| **Current release** | 1.2.0 |
| **Status** | Draft — for review, not yet implemented |
| **Date** | 2026-09-26 |

## 1. Background

`googletrans>=4.0.0rc1` is an unofficial, unmaintained wrapper around Google's public web-translate endpoint. It has open, unresolved issues (e.g. [py-googletrans#234](https://github.com/ssut/py-googletrans/issues/234)) where Google changing its internal token-generation logic breaks translation outright, surfacing in this app as `[Translation error: 'NoneType' object has no attribute 'group']` or similar. This is the confirmed root cause of "Google Translate doesn't work anymore" reported for this project. See prior diagnosis in conversation history; not repeated here.

`deep-translator` is the recommended replacement: actively maintained, MIT-licensed, synchronous (no `asyncio` bridging needed), and its `GoogleTranslator` backend has proven more resilient to upstream changes than `googletrans`. It is not magically immune to Google changing its translate page, but unlike `googletrans` it receives prompt community patches when that happens.

## 2. Goals / Non-Goals

**Goals**
- Swap the translation engine with minimal behavioral change to the user (same UI, same fallback-to-original-text-on-error behavior).
- Remove the `asyncio` bridging code that exists solely to support `googletrans`'s async API.
- Fix a real compatibility bug this migration would otherwise introduce (Chinese language code casing — see §6).
- Bump `APP_VERSION` to `1.3.0` and update all dependency/doc/test references.

**Non-goals**
- No redesign of the translation UX or settings schema.
- No new languages or translation providers.
- No retry/backoff or rate-limit handling beyond the existing try/except-and-fall-back-to-original-text pattern (keep the diff small).
- Not switching to a paid/official API.
- Not modifying `src/sc_translator/main.py` as part of this change — see §12 open question.

## 3. Current State Analysis

Dependency: `googletrans>=4.0.0rc1` (venv currently has `4.0.2` installed).

All translation call sites are in **`main.py`** (root — this is the file actually used; see §12 for the stale `src/sc_translator/main.py` duplicate):

| Location | Purpose |
|---|---|
| `main.py:10` | `from googletrans import Translator` |
| `main.py:19` | `import asyncio` — only used to run googletrans' async `.translate()` |
| `main.py:231-244` | `run_async_translation(coro)` — event-loop bridging helper |
| `main.py:345` | `self.translator = Translator()` in `__init__` — **dead code**, never referenced again (grep confirms no other use of `self.translator`) |
| `main.py:1126-1136` | `_safe_translate(self, text, dest)` — used for all hardcoded/welcome/UI-string translations |
| `main.py:1139-1166` | `_manual_translate(self)` — the manual translate box + clipboard copy |
| `main.py:1793-1829` | `_watch_latest_chat(self)` — live chat.log translation loop (the core feature) |

All three real call sites follow the same pattern:
```python
translator = Translator()
result = run_async_translation(translator.translate(text, dest=lang))
translated = result.text
```
wrapped in `try/except Exception`, falling back to the original text (or an `"[Translation error: {e}]"` string in two of the three sites).

`tests/test_translator.py` mocks `main.Translator` and asserts `mock_translator.translate.assert_called_once_with("Hello World", dest="es")` — this test will need updating (§10).

## 4. New Dependency

Add **`deep-translator`**, pin as:
```
deep-translator>=1.11.4,<2.0.0
```
(1.11.4 is the current latest release, June 2023; upper-bound the major version defensively since we haven't reviewed a hypothetical 2.x API.)

Its only transitive dependencies are `requests` and `beautifulsoup4` — both modern, well-maintained, and fine on Python 3.11 (the venv already set up for this project).

## 5. API Mapping

| Concern | `googletrans` (old) | `deep_translator` (new) |
|---|---|---|
| Import | `from googletrans import Translator` | `from deep_translator import GoogleTranslator` |
| Construct | `Translator()` (stateless, `dest` passed per call) | `GoogleTranslator(source="auto", target=<lang>)` — **target is fixed at construction**, so a new instance is still created per call site exactly as today |
| Call | `translator.translate(text, dest=lang)` → coroutine (v4 rc) | `translator.translate(text)` → plain **synchronous** call |
| Result | object with `.text` attribute | plain `str`, returned directly |
| Async bridging | required (`run_async_translation`, `asyncio.run`) | **not needed at all** — delete it |
| Errors | generic `Exception` / `AttributeError` (e.g. broken token parsing) | typed exceptions in `deep_translator.exceptions`: `TranslationNotFound`, `RequestError`, `TooManyRequests`, `LanguageNotSupportedException`, `NotValidPayload` (raised for text >5000 chars — irrelevant here, chat lines are short) |
| Language code matching | lenient | **case-sensitive**, direct dict lookup against Google's own table — see §6 |

Since `deep_translator.translate()` returns a plain string synchronously, every call site gets simpler, not just swapped:

```python
# Before
translator = Translator()
result = run_async_translation(translator.translate(text, dest=dest))
translated = result.text

# After
translated = GoogleTranslator(source="auto", target=_normalize_lang_code(dest)).translate(text)
```

## 6. Compatibility Risk: Chinese language code casing (must fix, not just port)

`DEFAULT_SETTINGS` in `main.py` uses **`"zh-cn"`** (lowercase) in both `languages["Chinese (Simplified)"]` and `manual_languages["ZH"]`.

`deep-translator`'s `GoogleTranslator` validates the `target` argument via case-sensitive matching against its internal Google language table, where Chinese Simplified is registered as **`"zh-CN"`** (capital `CN`). It does **not** lowercase/normalize input before comparing. Passing `"zh-cn"` as-is will raise `LanguageNotSupportedException` on every translation attempt — meaning chat auto-translate *and* manual translate would both break for any user with Chinese selected, immediately after this upgrade.

This can't be fixed by just editing the default dict, either: `_load_settings()` fills in *missing* keys from `DEFAULT_SETTINGS` but never overwrites existing values, so any user who already has `"zh-cn"` written into their `settings.json` (or `game_dictionary`-adjacent config) would keep hitting the bug even after an update to the shipped defaults.

**Fix**: add a small normalization helper applied at the translation-call boundary (not in settings), so it's independent of whatever is already persisted on disk:

```python
_LANG_CODE_FIXUPS = {"zh-cn": "zh-CN"}

def _normalize_lang_code(code: str) -> str:
    return _LANG_CODE_FIXUPS.get(code, code)
```

Apply it to the `target=` argument at all three call sites. This is a one-entry table today; if other mismatches surface later they get added here, without touching settings schema or user files.

## 7. Detailed Code Changes — `main.py`

1. **Imports** — replace line 10, drop line 19:
   ```python
   from deep_translator import GoogleTranslator   # was: from googletrans import Translator
   # `import asyncio` removed entirely — no longer needed
   ```
2. **Remove** `run_async_translation()` (lines 231-244) — no longer needed, nothing else in the file uses `asyncio`.
3. **Add** `_normalize_lang_code()` helper (module-level, near where `run_async_translation` used to live, or as a small static helper) — see §6.
4. **`__init__`** (line 345): delete `self.translator = Translator()` — confirmed dead code, not reused anywhere. Do not replace it with a `GoogleTranslator()` equivalent, since target language varies per call site and instances are constructed locally each time (see next points).
5. **`_safe_translate`** (lines 1126-1136): replace body per the "After" snippet in §5, using `_normalize_lang_code(dest)`.
6. **`_manual_translate`** (lines 1139-1166): same substitution, using `_normalize_lang_code(self.manual_translate_lang)`.
7. **`_watch_latest_chat`** (lines 1793-1829): same substitution, using `_normalize_lang_code(self.target_lang)`.
8. No changes needed to `_get_short_code_for_lang`, `_change_language`, `_change_manual_language`, or the settings schema — they operate on the same string codes as before; only the translation-call boundary changes.

## 8. Dependency File Changes

- **`requirements.txt`**: replace
  ```
  googletrans>=4.0.0rc1
  ```
  with
  ```
  deep-translator>=1.11.4,<2.0.0
  ```
- **`pyproject.toml`**:
  - `[project] dependencies`: same swap as above.
  - `[[tool.mypy.overrides]] module`: replace `"googletrans.*"` with `"deep_translator.*"`.
- No change needed in `requirements-dev.txt` or `requirements-build.txt`.

## 9. Version Bump to 1.3.0

Update `1.2.0` → `1.3.0` in:
- `main.py` — `APP_VERSION = "1.3.0"` (line 29). `settings["app_version"]` and the window title auto-follow this constant, no further code change needed there.
- `pyproject.toml` — `[project] version = "1.3.0"`.
- `README.md` — version references.
- `CHANGELOG.md` — new `## [1.3.0] - 2026-09-26` section, suggested content:
  ```markdown
  ## [1.3.0] - 2026-09-26

  ### Changed
  - Replaced unmaintained `googletrans` dependency with `deep-translator` (`GoogleTranslator`) — fixes translation failures caused by Google's web-endpoint token changes that `googletrans` could no longer handle
  - Translation calls are now synchronous; removed the `asyncio` event-loop bridging (`run_async_translation`) required by `googletrans`' async API

  ### Fixed
  - Chinese (Simplified) translation (`zh-cn`) now normalized to the code deep-translator expects (`zh-CN`) at the translation call boundary — previously would have failed with `LanguageNotSupportedException` under the new backend

  ### Removed
  - `googletrans` dependency, `run_async_translation()` helper, unused `self.translator` instance attribute
  ```
- Not in scope: `build/build_macos.spec`'s example `CFBundleVersion`/`CFBundleShortVersionString` values were already stale at `1.1.3` before this change (pre-existing drift, unrelated to this migration) — flagging for awareness, not fixing here unless requested.

## 10. Documentation Updates

Every file below currently references `googletrans` and needs its code snippets/text swapped to `deep_translator` / `GoogleTranslator`:

| File | What changes |
|---|---|
| `README.md` | Dependencies code block (line ~346); "Googletrans Library" external link (line ~556) → link to deep-translator docs instead |
| `docs/installation.md` | Three `python -c "from googletrans import Translator; ..."` smoke-test one-liners (Windows/Linux/macOS scripts) → `python -c "from deep_translator import GoogleTranslator; print(GoogleTranslator(source='auto', target='es').translate('Hello'))"` |
| `docs/troubleshooting.md` | Quick-diagnosis import test, "Test Google Translate Service" snippet, and the "Manual Testing" component-test snippet |
| `docs/development.md` | Dependencies list, `import tkinter, customtkinter, googletrans` verification one-liner, `pip install customtkinter googletrans pyperclip Pillow`, the `pip install git+https://github.com/ssut/py-googletrans.git` fallback-install tip (no longer applicable), and the exception-handling style example (`except googletrans.exceptions.TranslationError` → `except deep_translator.exceptions.TranslationNotFound` or a broader catch, matching whatever pattern is actually implemented in §7) |
| `docs/user-guide.md` | "Service: googletrans Python library" description and its code sample |

## 11. Test Updates — `tests/test_translator.py`

- Replace `patch('main.Translator')` with `patch('main.GoogleTranslator')` in `test_safe_translate_success` and `test_safe_translate_failure`.
- Since `.translate()` now returns a plain string (not an object with `.text`), update the mock:
  ```python
  mock_translator_class.return_value.translate.return_value = "Hola Mundo"
  ```
- Update the call assertion to match the new signature:
  ```python
  mock_translator_class.assert_called_once_with(source="auto", target="es")
  mock_translator_class.return_value.translate.assert_called_once_with("Hello World")
  ```
- Add a new test asserting `"zh-cn"` gets normalized to `"zh-CN"` before being passed as `target=` (regression test for §6).
- `tests/test_main.py` needs no changes — it doesn't reference `Translator` directly — but the full suite should be re-run after the change (some tests instantiate `TranslatedFileWatcher()` without mocking the translator, so they currently make real network calls during `__init__`/`_safe_translate`; that behavior is unchanged by this migration).

## 12. Manual Verification / Test Plan

1. `pip install -r requirements.txt` in the existing Python 3.11 venv after editing it.
2. Smoke test: `python -c "from deep_translator import GoogleTranslator; print(GoogleTranslator(source='auto', target='es').translate('Hello'))"`.
3. Launch the app and check:
   - Startup welcome message is translated.
   - Manual translate box translates and copies to clipboard.
   - A live `chat.log` line gets translated in the Chat tab.
   - Switch the chat target language to **Chinese (Simplified)** specifically, to confirm the §6 fix — this is the one case guaranteed to break without it.
   - App Log tab shows no `[Translation error: ...]` entries during normal use.
4. Run `pytest` — full suite should pass, including the updated/new tests from §11.

## 13. Rollback Plan

The change is isolated to translation call sites, one dependency line, and docs/tests — a straightforward single-commit revert if `deep-translator` turns out to have its own issues.

## 14. Open Questions

1. **`src/sc_translator/main.py`** is a stale duplicate of the root `main.py` (`APP_VERSION = "1.1.3"`, otherwise diverged, ~200 lines shorter). It is not wired into the packaging entry point — `pyproject.toml`'s `[project.scripts] sc-chat-translator = "main:main"` points at the root `main.py`, which itself has no `main()` function defined (pre-existing, unrelated issue). Should this duplicate be updated in lockstep with this migration, deleted, or left alone? Not addressed by this design.
2. Keep the current broad `except Exception` pattern at all three call sites (minimal diff, consistent with today's behavior), or adopt `deep_translator`'s typed exceptions for more specific logging/user-facing messages? This design assumes the former to keep the change minimal; worth a follow-up if desired.
3. Confirm the `deep-translator` version pin (`>=1.11.4,<2.0.0`) is acceptable, or if an exact pin (`==1.11.4`) is preferred for reproducibility.

## 15. Implementation Log (2026-09-26)

This design has been implemented in this sandbox instance. Status: **done**, with two findings logged below for anyone replicating this on another instance.

**Applied exactly as designed:**
- `main.py` — imports, `_normalize_lang_code()` helper added, `run_async_translation()` and `import asyncio` removed, dead `self.translator` removed, all three call sites (`_safe_translate`, `_manual_translate`, `_watch_latest_chat`) converted to synchronous `GoogleTranslator(...).translate(...)`, `APP_VERSION` → `1.3.0`.
- `requirements.txt`, `pyproject.toml` (dependency + mypy override + version) updated.
- `tests/test_translator.py` updated (`main.Translator` → `main.GoogleTranslator` mocks, string-return instead of `.text`, new regression test for the `zh-cn`→`zh-CN` fix).
- `README.md`, `CHANGELOG.md`, `docs/installation.md`, `docs/troubleshooting.md`, `docs/development.md`, `docs/user-guide.md` all updated — repo-wide grep for `googletrans` outside `venv/` now only matches historical CHANGELOG entries (correctly left alone, they document past releases), this design doc itself (intentionally documents the old library), and `src/sc_translator/main.py` (the stale duplicate — untouched per §14 open question #1, not part of this change).
- `venv`: `deep-translator` installed (pulled in `requests`, `beautifulsoup4`, `soupsieve`, `charset_normalizer`, `urllib3` — no conflicts), `googletrans` uninstalled. Its now-orphaned transitive deps (`httpx`, `httpcore`, `h11`, `chardet`, `rfc3986`, etc.) were **not** removed — pip doesn't track "why" a package was installed, so pruning them safely would require manually diffing against every other dependency's requirements; left in place as harmless clutter rather than risking removal of something still in use.

**Findings / deviations:**

1. **Pre-existing test-suite issue, unrelated to this migration.** Running the full `pytest` suite in one process fails most tests that instantiate `TranslatedFileWatcher()` with a real (unmocked) `customtkinter` GUI, with `_tkinter.TclError: image "pyimageN" doesn't exist`. Root cause: the suite has no teardown (no `conftest.py`, no `app.destroy()` anywhere) — each such test creates a brand-new real Tk root/window without disposing of the previous one, and `PhotoImage` objects from an earlier window get garbage-collected out from under a later one. Confirmed this is **not** caused by the googletrans→deep-translator swap: the exact same tests fail with no translation code on the call stack at all (e.g. `test_language_mappings`, `test_chat_category_detection` in `test_main.py`, which never touch the translator), and the translation-specific tests (`test_safe_translate_success`, `test_safe_translate_failure`, `test_safe_translate_normalizes_chinese_code`, etc.) **pass individually** when run in isolation — proving the migration's own logic is correct. Not fixed here (would require adding test fixtures/teardown, out of scope for a dependency swap) — flagged for a separate follow-up if the team wants a green full-suite run.
2. **Live smoke test hit Google's real rate limit — and this reproduced for the user too, not just the sandbox.** `GoogleTranslator(source="auto", target="es").translate("Hello, world!")` raised `deep_translator.exceptions.TooManyRequests` from this sandbox's egress IP, and the user separately hit the identical `[Translation error: Server Error: You made too many requests...]` while running the actual app on their own machine, translating a single live chat line. This ruled out "sandbox-only throttled IP" as the sole explanation — the underlying issue is that **no call site throttles or retries**, and this app's own usage pattern is bursty enough to trip Google's ~5 requests/second cap on its own: a single startup welcome message can fire the welcome text, each "what's new" line, the download label, and the notes label as separate back-to-back `_safe_translate()` calls, on top of the manual-entry placeholder hint translated moments earlier — easily 5+ requests within well under a second, before any live chat translation even begins.

   **Follow-up fix applied (same session, 2026-09-26):** added `_translate_text(text, target_lang)` (`main.py`, near `_normalize_lang_code`) — a shared helper that wraps the single `GoogleTranslator(...).translate(...)` call site with a bounded retry: on `deep_translator.exceptions.TooManyRequests` it sleeps (`1.5s`, then `3.0s`) and retries, up to 2 retries, before giving up and letting the existing try/except-and-fall-back-to-original-text behavior take over unchanged. All three call sites (`_safe_translate`, `_manual_translate`, the `_watch_latest_chat` loop) now go through this one helper instead of constructing `GoogleTranslator` directly — also incidentally deduplicating three near-identical inline blocks. Verified via mocks: (a) `TooManyRequests` then success on retry returns the translated text after exactly one `time.sleep` call, (b) exhausting both retries still falls back to the original text exactly as before. Two new tests added to `tests/test_translator.py`: `test_safe_translate_retries_on_rate_limit_then_succeeds`, `test_safe_translate_falls_back_after_exhausting_retries` — both pass in isolation. `CHANGELOG.md`'s `1.3.0` entry updated with this fix.

   **This first fix was wrong and made things worse (corrected same session, 2026-09-26).** The retry-only approach added blocking `time.sleep()` calls *inside* `_safe_translate()`, which runs synchronously on the main thread during `__init__`, before the window is shown. Since startup alone fires ~9 such calls, a rate-limited launch could now block for up to ~40s (9 calls × up to 2 retries × up to 4.5s backoff) before the window appeared — this is the direct cause of the reported "app runs a few times slower." Worse, the user's log showed `Application started` firing **11 times within 13 seconds**, then repeatedly every 30-90s after — almost certainly the user (reasonably) re-launching the app because it appeared frozen, each relaunch firing its own ~9-call burst with retries on top. That's 100+ requests inside ~15 seconds from one IP, which doesn't just trip Google's per-second cap, it looks like sustained abuse — plausibly explaining the ~20 minutes of continuous `TooManyRequests` failures that followed in the log, independent of anything the code does.

   The retry-only fix treated the symptom (an occasional 429) without fixing the cause (nothing paces requests, so a burst can form at all — at startup, or from a fast-scrolling chat log). **Corrected fix:** added `_throttle_translate_call()` — a thread-safe, module-level minimum-interval gate (`_MIN_SECONDS_BETWEEN_TRANSLATE_CALLS = 0.3`, protected by a `threading.Lock`, using `time.monotonic()`) called at the top of `_translate_text()` before every request, regardless of call site or thread (covers the main-thread startup sequence and the background chat-watch loop with one mechanism). This caps effective throughput at ~3.3 req/s app-wide, safely under Google's ~5/s limit, so a burst is prevented rather than retried after the fact. The retry was dialed back accordingly — from 2 attempts/up to 4.5s backoff down to **1 attempt/1.0s backoff** — now a thin safety net rather than the primary mitigation, since the throttle should prevent almost all rate-limit hits under normal use. Net effect on startup latency: ~9 calls × 0.3s spacing ≈ 2.7s added in the worst case (vs. up to 40s with the broken first attempt, and no worse than the pre-migration baseline, which always made ~9 sequential network round-trips at startup regardless of library).

   Tests updated: `test_safe_translate_retries_on_rate_limit_then_succeeds` and `test_safe_translate_falls_back_after_exhausting_retries` now mock `main._throttle_translate_call` out (otherwise the throttle's own `time.sleep` calls made the retry-backoff call-count assertions flaky across a shared module-level timestamp). Added `test_translate_calls_are_throttled` to directly cover the new spacing behavior. All pass individually.

   **Not implemented** (would be scope creep beyond fixing the reported symptom): batching multiple pending welcome-message translations into one `translate_batch()` call (would reduce the ~9 startup calls to 1, cutting both latency and request count further, but changes the welcome-message code path more invasively than a rate-limit fix warrants), or moving welcome-message translation off the main thread entirely so the window appears instantly and text fills in afterward (bigger UX/threading change, not requested). Worth considering if startup latency or rate-limit pressure remains a problem after this fix.

   **Caveat for the user:** if Google's free endpoint has flagged the reporter's IP for the burst that already happened, some residual `TooManyRequests` errors may continue for a while after this fix is deployed, independent of the code — that block is server-side and outside the app's control, and should clear on its own (typically minutes, not hours, for this class of free-tier throttling). The throttle prevents the app from re-triggering or extending it going forward.
