# Design: Switch to the `translate` Library (MyMemory backend) — EXPERIMENTAL

| | |
|---|---|
| **Status** | **Experimental / trial run** — see §6 |
| **Target release** | 1.3.0 (same in-progress release as the deep-translator migration; not yet shipped) |
| **Supersedes** | [design-deep-translator-migration.md](design-deep-translator-migration.md) — that migration's own §15 implementation log documents how this replacement became necessary. Read that file first for the `googletrans` → `deep-translator` history; this file picks up from there. |
| **Date** | 2026-09-26 |

## 1. Why deep-translator's `GoogleTranslator` had to be abandoned (not just patched)

After migrating from `googletrans` to `deep-translator` and fixing an unrelated request-pacing bug (see the other design doc's §15), translation kept failing with `TooManyRequests` even for single, isolated, well-spaced manual translate clicks — a pattern pacing fixes cannot explain. Research (not guesswork) confirmed the real cause:

- **Since approximately September 14, 2026, Google has been blocking the `client=gtx` identifier** used by its free/unofficial translate endpoints, returning HTTP 429 with an "automated queries" page — a platform-wide crackdown on scraping-based access, not something tied to this app's usage history or IP.
- `deep-translator`'s `GoogleTranslator` scrapes a different but related endpoint (`translate.google.com/m`, the mobile page) with **zero custom headers** (no browser-like User-Agent), sent via a hardcoded `requests.get(url, params=...)` with no way to override headers or the `client` parameter from our side.
- `deep-translator` itself is dormant (last released June 2023) — no maintainer fix exists or is likely.
- A community-known workaround exists for `client=gtx`-based tools specifically (switch to `client=at`), but doesn't apply to `deep-translator`'s different endpoint, and there's no supported way to apply it without monkey-patching the library's internals — rejected as too fragile for what should be a stable dependency.

**Conclusion:** this wasn't a bug in our integration to fix — the free Google-scraping approach itself (the same fundamental approach `googletrans` used, that this whole effort was originally trying to escape) is currently broken at the source, platform-wide. Continuing to build on it would just repeat the same failure mode with a different library.

## 2. Why `deep-translator`'s other backend (`MyMemoryTranslator`) was also rejected

Before looking elsewhere, `deep-translator`'s built-in `MyMemoryTranslator` (a different, Google-independent free service) was evaluated as a same-dependency swap. Live-tested directly rather than assumed:

```
MyMemoryTranslator(source='auto', target='es').translate(...)
→ LanguageNotSupportedException: 'es' --> No support for the provided language...
```

Root cause, confirmed by testing MyMemory's raw REST API directly (bypassing both libraries):

- MyMemory's server **does** support genuine server-side auto-detection — but only via the literal string `"autodetect"`, not `"auto"`.
- `deep-translator`'s base class treats the literal string `"auto"` as a universal wildcard that bypasses its own client-side validation — but then forwards `"auto"` straight to MyMemory, which doesn't recognize that spelling. The server doesn't even error cleanly: `langpair=auto|es` returns **HTTP 200** with the translated-text field containing `"'AUTO' IS AN INVALID SOURCE LANGUAGE..."` — a silent failure dressed up as a successful translation.
- This is a `deep-translator`-specific integration gap (it doesn't know MyMemory's specific "autodetect" convention), not a MyMemory limitation.

Since this app's core feature — translating chat lines whose source language is unknown and varies line-to-line (English, Russian, Polish, Chinese, etc. in the same channel) — has no viable path without real auto-detection, and `deep-translator` cannot deliver that for MyMemory, `deep-translator` was dropped entirely rather than patched around.

## 3. Alternatives researched (current, verified — not from training-data memory)

### 3a. Official APIs (Google Cloud / Azure / DeepL)

| API | Free tier (verified 2026) | Card required? | Auto-detect |
|---|---|---|---|
| Google Cloud Translation | 500k chars/mo (recurring $10 credit, never expires) + $300 new-signup credit (90 days) | **Yes** | Native |
| Azure Translator (F0) | 2M chars/mo, same features as paid | **Yes** (typically) | Native |
| DeepL API | **One-time** 1M characters (Developer tier — the old recurring "API Free" plan was retired July 2026) | **No** | Native (`source_lang` optional) |

All three require the end user to create an account and manage their own API key — a real UX change from this app's current zero-config design. DeepL is the only one avoiding a card requirement, at the cost of a non-renewing allowance. **Not pursued for this trial** — kept as the fallback direction if the MyMemory-via-`translate` trial (below) proves insufficient; see §6.

### 3b. Other libraries considered

- **`translators` (PyPI, v6.0.4, released Jan 2026)** — actively maintained, 39 engines, built-in `from_language="auto"` default. Credible second option, but its last release predates the September 2026 Google crackdown, so its Google engine is plausibly affected by the same block; not verified further since 3c resolved the immediate need.
- **Local language-detection + MyMemory (e.g. `lingua-py`, rated best-in-class for short/slang text, paired with `deep-translator`'s `MyMemoryTranslator` using explicit codes)** — technically workable, but unnecessary once MyMemory's own real auto-detect (`"autodetect"`) was confirmed working — would have added a whole new dependency and a probabilistic detection step to solve a problem that turned out to already be solved server-side.
- **`argos-translate`** — fully offline, genuinely zero rate limits, but requires each user to download per-language-pair model files (heavy for a lightweight game companion app), has no built-in auto-detect, and quality degrades for language pairs requiring a pivot through English. Not a good fit.

### 3c. `translate` (PyPI, terryyin/translate-python) — the option that actually resolved this

The user specifically asked this be checked. It did more than just "be more recently maintained" — it fixes the exact integration gap that disqualified `deep-translator`+MyMemory:

- Latest release: **3.8.1, July 2026** (vs. `deep-translator`'s dormant June 2023).
- Default provider: **MyMemory**, no API key.
- Its `from_lang` default (`TRANSLATION_FROM_DEFAULT` constant) is the literal string **`"autodetect"`** — exactly the value MyMemory's server actually wants. Confirmed by reading its `MyMemoryProvider` source: it does zero client-side language-code validation and passes `from_lang`/`to_lang` straight through, so it correctly relies on the server rather than an incomplete local mapping table.
- Confirmed live, end-to-end, through the actual `translate.Translator` class (not just the raw API):
  ```
  Translator(to_lang='es').translate('Hello, how are you today?')
  → 'Hola, ¿cómo estás hoy?'
  Translator(to_lang='pl').translate('Привет, как дела?')   # Russian source, undeclared
  → 'Cześć, jak się masz?'
  ```
  Real auto-detection, working, through the library we're about to depend on — not just the raw API in isolation.
- Bare 2-letter codes (`"es"`, `"pl"`, `"zh-cn"`) all work fine server-side — **no code-remapping table needed** (unlike the `zh-cn`→`zh-CN` fix that `GoogleTranslator` required; verified `zh-cn` and `zh-CN` return identical results from MyMemory directly).

**One real, confirmed limitation to carry forward:** MyMemory hard-caps queries at **500 characters per request** (server message: `"QUERY LENGTH LIMIT EXCEEDED. MAX ALLOWED QUERY: 500 CHARS"`). `translate`'s own client-side chunking (`TRANSLATION_API_MAX_LENGTH = 1000` in `translate.py`) is miscalibrated for the MyMemory provider specifically — it won't split a 753-character string (like this app's extended welcome message, `msg_len=753` was observed in a real log) before sending it, so that call raises `translate.exceptions.TranslationError` for anything between 501–1000 chars. This is not fatal — it raises a normal catchable exception, which this app's existing per-call-site `except Exception → fall back to original text` pattern already handles gracefully (the welcome message just displays untranslated in that case, with a warning logged) — but it's a real, known gap, not silently patched over. No chunking logic is being added in this pass; live chat lines are never anywhere near 500 characters, so this only affects the occasional long extended-welcome-message content.

Also confirmed: MyMemory's daily quota is enforced via the same `responseStatus`-in-JSON mechanism (HTTP 200, but `responseStatus: 403` with a descriptive message) — `translate`'s `MyMemoryProvider.get_translation()` correctly checks this field and raises `TranslationError`, so quota exhaustion won't silently display a garbage "translation" either.

## 4. Quota mechanics (for anyone tuning `mymemory_email` later)

- Anonymous: **5,000 characters/day**, shared per source IP.
- With a registered email (free, no account/card — just a string passed as the `de` request parameter): **50,000 characters/day**, tied to that specific email.
- Important: if the *same* email were hard-coded into the app and shipped to every user, all installs would share one 50k/day pool app-wide — the wrong shape for a multi-user distributed app. The email must be a **per-user, optional** setting, never a baked-in default.

## 5. What was implemented

- `main.py`: replaced `from deep_translator import GoogleTranslator` (+ `TooManyRequests` retry logic) with `from translate import Translator` (+ `from translate.exceptions import TranslationError`). The `_translate_text()` helper now constructs `Translator(to_lang=target, from_lang="autodetect")` and calls `.translate(text)`. The `GoogleTranslator`-era retry-with-backoff (built around `TooManyRequests`, a daily-quota-shaped failure that a few seconds of retrying can't fix anyway) was removed; the existing app-wide request-spacing throttle (`_throttle_translate_call`, unrelated to any specific backend) was kept as reasonable etiquette. The `zh-cn`→`zh-CN` normalization fixup was removed — confirmed unnecessary for MyMemory (§3c).
- Added an optional `mymemory_email` setting (empty string by default, anonymous quota) — a `settings.json` key only, no new Settings-tab UI field, consistent with how this app already treats other advanced/optional settings (e.g. `remote_dictionary_url`). Documented so a user can opt in manually.
- `requirements.txt` / `pyproject.toml`: `deep-translator` → `translate>=3.8.1,<4.0.0`. `deep-translator` uninstalled from the venv; `translate` installed (pulls in `lxml`, `libretranslatepy`, reuses the already-installed `requests`).
- `tests/test_translator.py`: mocks updated from `main.GoogleTranslator` to `main.Translator`; the `zh-cn` normalization test removed (no longer applicable) and replaced with a test confirming codes pass through unchanged; retry-specific tests removed along with the retry logic they covered.
- Docs (`README.md`, `CHANGELOG.md`, `docs/installation.md`, `docs/troubleshooting.md`, `docs/development.md`, `docs/user-guide.md`) updated to reflect `translate`/MyMemory instead of `googletrans`/`deep-translator`.

## 6. Why this is marked experimental, and the rollback path

Per explicit direction: treat this as a **trial run**, not a settled architecture. If it doesn't hold up in real use, the intended fallback is switching to an official API with a user-supplied key (§3a — DeepL first, given no card requirement), not back to `deep-translator` or `googletrans` (both already ruled out for the same underlying reason: dependence on Google's now-hostile-to-scraping free endpoint).

Things that would indicate the trial has failed and a switch is warranted:
- Hitting the 5,000-char/day anonymous cap during ordinary (not test/burst) use — the first lever is asking the user to set `mymemory_email` for the 10x quota before concluding the approach itself has failed.
- MyMemory translation quality proving noticeably worse than Google's for this app's language pairs (it's a translation-memory/crowdsourced service, not a dedicated NMT model — quality varies by language pair and is generally behind Google/DeepL).
- MyMemory itself becoming unreliable or rate-limiting more aggressively than documented.

Because the code changes are isolated to `_translate_text()` and its two constants/imports (same shape of change as the previous migration), reverting or swapping to a different backend again remains a small, contained diff — not a rearchitecture.

## 7. Post-implementation finding: MyMemory rejects "same-language" translation entirely, not just for English

Found from a real chat line shortly after deployment:

```
[Priv_to] [Kvasiir]: 'ping 200 xd'
→ [Translation error: PLEASE SELECT TWO DISTINCT LANGUAGES]
```

§5's fix only handled this for `_safe_translate`'s known-English hardcoded/welcome strings (skip outright when `dest == "en"`). This case is different and broader: **any** live chat message — from any call site, to any target language — that MyMemory's auto-detector classifies as already being in the target language triggers the same hard rejection, not a graceful no-op. `"ping 200 xd"` is short, slang-heavy game chat with no strong language signal; MyMemory detected it as English, and the user's target language was also English.

This isn't an edge case specific to one language pair — it's a structural property of MyMemory's API (confirmed by reproducing it directly against the raw endpoint: `langpair=autodetect|en` for `"ping 200 xd"` returns `responseStatus: 403`, `"PLEASE SELECT TWO DISTINCT LANGUAGES"`, while the same text against `pl` or `es` targets succeeds and correctly returns the text unchanged). Short, ambiguous, or slang-heavy messages — extremely common in game chat ("gg", "lol", numbers, abbreviations) — are exactly the kind of text most likely to be detected as matching whatever the target language already is.

**Fix:** moved the handling into `_translate_text()` itself (the shared helper all three call sites go through), rather than special-casing individual callers again. It catches `TranslationError`, checks for this exact MyMemory message, and returns the original text — since that IS the correct output when source and target are already the same — while re-raising any other `TranslationError` (quota exceeded, query-too-long, etc.) unchanged so existing fallback/logging behavior still applies to genuine failures. Verified against the live API with the exact reported message, and covered by two new tests (`test_translate_text_returns_original_when_already_target_language`, `test_translate_text_reraises_other_translation_errors`).

The narrower `_safe_translate` dest=="en" skip from §5 is kept alongside this — it's a proactive optimization (skips the network round-trip entirely for strings whose source is always known to be English), while this fix is the general reactive safety net for every call site where source language is genuinely unknown in advance.
