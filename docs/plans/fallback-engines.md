# Plan: Additional Translation Engines (to do)

Status: **postponed** (2026-10-13). MyMemory stays the only engine for now.

## Goal

Let a player add their own key for a second engine, used when MyMemory's daily limit
is reached (or chosen instead of MyMemory). Opt-in only; the app must keep working with
no key and no account.

## Candidates (researched 2026-10-13)

All four are supported by the `translate` package the app already uses
(`Translator(provider=..., secret_access_key=...)`), so the code change is small; the
blocker is that none could be tested without a key.

| Engine | Free allowance | Key / account | Verdict |
|---|---|---|---|
| **DeepL API** | "Developer" plan: 1,000,000 characters **in total**, does not reset. The old "API Free" plan (500,000/month) can no longer be purchased. | DeepL account; whether new users can still get the Developer plan, and whether a card is required, is unclear. | Best quality; first choice once a key is available for testing. |
| **Microsoft Translator (Azure F0)** | 2,000,000 characters / month | Azure account; reportedly needs a credit card | Generous, but the card requirement is a barrier for players. |
| **LibreTranslate** | Self-hosted: unlimited | Public server now requires a paid key; self-hosting needs Docker and language models (hundreds of MB) | Too heavy for players; possible for advanced users with their own server. |
| **Google Cloud Translation** | 500,000 characters / month | Google Cloud account with billing (card) | Not supported by `translate`; would need its own client. |

Sources: DeepL API plans (support.deepl.com), Azure Translator pricing, LibreTranslate
project pages; see the 2026-10-13 session notes.

## When this is picked up

1. Get a test key (DeepL Developer first).
2. Settings → Translation Service: engine choice + key field (stored only in
   `settings.json`, never logged, same rules as the email).
3. `TranslationService`: on MyMemory's quota error, use the second engine if a key is set.
4. Tests with a mocked provider; one manual live test with the real key.
5. Document in `docs/translation-service.md` (section "Other translation engines").
