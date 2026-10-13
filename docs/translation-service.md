# Translation Service: MyMemory, Daily Limits and the Email Setting

This page explains, in plain terms:

- [Why the app no longer uses Google Translate](#why-the-app-no-longer-uses-google-translate)
- [How the free daily limit works](#how-the-free-daily-limit-works)
- [Why entering your email raises the limit](#why-entering-your-email-raises-the-limit)
- [Translate only the channels you need](#translate-only-the-channels-you-need)
- [What happens to your email address](#what-happens-to-your-email-address)
- [What happens when the limit is reached](#what-happens-when-the-limit-is-reached)
- [Questions and answers](#questions-and-answers)

---

## Why the app no longer uses Google Translate

Up to version 1.2.0 the app translated chat through **Google Translate's free web endpoints**. These are not an official, supported service. They are the same addresses the Google Translate website uses, which free tools have long borrowed without an API key.

In **September 2026 Google started blocking this kind of access across the board**. Requests were answered with *"too many requests / automated queries"* errors, even when the app sent only one message every few seconds. This was not caused by this app or by any particular player: every tool that used the free Google endpoints was affected. The libraries the app had used (`googletrans`, and later `deep-translator`) could not get around the block, and neither is being fixed by its authors.

There were two ways forward:

| Option | What it would mean for players |
|---|---|
| Google's **official** Cloud Translation API (or Azure, DeepL) | Every player creates a developer account, usually adds a payment card, and pastes an API key into the app. |
| **MyMemory**, a free translation service run by Translated | Works straight away with no account and no key. It has a daily limit, which you can raise for free by entering an email address. |

Version 1.3.0 switched to **MyMemory** so that the app keeps working with nothing to set up. MyMemory detects the language of each chat line by itself, so messages in English, Russian, Polish, Chinese and other languages in the same channel are still handled automatically.

**Trade-offs to be aware of:**

- MyMemory combines a large translation memory with machine translation. For some language pairs the results are not as good as Google's or DeepL's.
- A single request is limited to about 500 characters. Chat lines are much shorter than that, so you will not notice it in normal play.
- There is a daily limit (see below).

If MyMemory turns out not to be good enough in real use, the next step would be support for an official API with your own key, not a return to the blocked free Google endpoints.

---

## How the free daily limit works

MyMemory counts the **characters** it translates for you each day:

| How you use MyMemory | Free limit per day |
|---|---|
| Anonymous (no email set; the default) | **5,000 characters** |
| With your email address set | **50,000 characters** |

Some points to keep in mind:

- **The anonymous limit is counted per internet connection (IP address).** Everyone behind the same router, or anyone else using MyMemory from your address, shares those 5,000 characters.
- 5,000 characters is roughly **100–150 typical chat lines**. On a busy evening in a crowded channel you can use that up quickly.
- The app already avoids wasting your limit:
  - It reuses earlier translations of repeated messages instead of asking again.
  - It never sends messages with no letters at all (such as "200", "!!!" or emoji) for translation.

---

## Why entering your email raises the limit

**MyMemory sets this rule itself; the app just follows it.** MyMemory gives a ten times larger free allowance to anyone who sends a valid email address along with their requests. No account, password, registration or payment is needed.

MyMemory doesn't explain its reasons in detail, but the effect is easy to see. Without an email, all MyMemory can see is your internet address, which many people may share. With an email, it can recognise you as one person and give you your own allowance. It can also reach you if there is ever a problem with your usage. In return for that, it is willing to translate more for you.

In practice:

- You get **your own 50,000-character daily allowance**. It is tied to your address, not to your internet connection.
- You do **not** receive a confirmation email, newsletter or login.
- You can remove it at any time (**Settings → Translation Service → Clear**). The app then goes back to the anonymous 5,000-character limit.

**Use your own address.** Don't share one address among several players. The allowance belongs to the address, so everyone using it would share one 50,000-character pool and use it up together.

---

## Translate only the channels you need

Every translated message uses part of the daily limit, roughly as many characters as the message is long. Busy channels such as **Trading** or a crowded general chat can use most of it before your squad or private messages come in.

In **Settings → Translated Channels** you can untick the channels you don't need translated:

- **All channels are ticked by default.** Nothing changes unless you untick something.
- An unticked channel is **still shown** in the chat and saved in History, just without the translation line (and without using any of your limit).
- **Translate all** and **Translate none** switch every channel at once. *Translate none* is useful if you only want the manual translation tool.
- The setting is saved immediately and kept between sessions.

A practical setup when you keep hitting the limit:

1. First add your email (see above): ten times more translation, no other change.
2. If that's still not enough, untick the channels you read least, typically **Trading** and general chats in languages you already understand.

---

## What happens to your email address

- It is saved **only on your computer**, in the app's `settings.json` file.
- It is sent **only to MyMemory**, together with each translation request, over an encrypted (HTTPS) connection.
- It is **never** written to the app's log files and is never sent to the app's authors or anyone else.
- It is **optional**. The app works without it; you just get the smaller anonymous limit.

For how MyMemory handles the data it receives, see MyMemory's own website: <https://mymemory.translated.net/>.

---

## What happens when the limit is reached

When MyMemory reports that the daily limit has been used up:

1. **Chat keeps working.** Every message is still shown, with the short note `[not translated – daily limit reached]`.
2. The app **stops sending translation requests** until the limit resets, instead of failing on every new line.
3. One notice appears in the chat, and the status bar shows roughly when translation will resume.
4. Translation **resumes automatically**; you don't need to restart the app.

To avoid hitting the limit, add your email in **Settings → Translation Service (MyMemory)**, and/or translate fewer channels (**Settings → Translated Channels**).

---

## Questions and answers

**Do I have to enter an email?**
No. It is entirely optional. Without it the app works the same, just with the smaller daily limit.

**Can I use a secondary or "gaming" email address?**
Yes. Any valid address that you control works.

**Why are some messages shown without a translation?**
Either their channel is unticked in **Settings → Translated Channels**, the message has no letters to translate, or MyMemory recognised it as already being in your language.

**Does the email make translations better?**
No. Translation quality is the same; only the daily allowance changes.

**Can I go back to Google Translate?**
Not at the moment. Google blocks the free access the app used to rely on, and the official Google API needs a developer account with billing. See [the section above](#why-the-app-no-longer-uses-google-translate).

**Where can I report a problem?**
Use the project's issue tracker: <https://github.com/jacek-mar/star-conflict-chat-translator/issues>.

---

*Technical background for developers: [design-translate-library-migration.md](design-translate-library-migration.md) and [design-deep-translator-migration.md](design-deep-translator-migration.md).*
