# GitHub synchronisation plan

Status: **local setup done, nothing pushed** (2026-10-13)

## Decisions

- Primary repository: **https://github.com/jacek-mar/star-conflict-chat-translator**
- `https://github.com/Boruta-project/star-conflict-chat-translator` stays as the original
  project and is kept in sync from the `jacek-mar` account (collaborator access).
- Local working folder (synchronised with GitHub):
  `C:\Users\Jacek\python_projects\star-conflict-chat-translator`
- Archives (read-only, not synchronised):
  - `C:\Users\Jacek\python_projects\star-conflict-chat-translator-main_1.2.0` (v1.3.0 + venv + built exe)
  - `C:\Users\Jacek\python_projects\sc_chat_translator_1.2.0` (v1.1.3 / 1.2.0 / 1.3.0 copies and planning notes)

## Done

1. Cloned the fork into the new folder (history up to v1.1.3, 59 commits).
2. Added remotes: `origin` = jacek-mar fork, `upstream` = Boruta-project.
3. Copied the v1.3.0 code from the archive folder, excluding `venv/`, `dist/`,
   `build_pyinstaller/`, `htmlcov/`, `.pytest_cache/`, `__pycache__/`.
4. v1.4.0 changes are made in this folder (see `v1.4.0-plan.md`).

## Before pushing (manual checks)

1. **Sign in as jacek-mar.** Git Credential Manager may have cached the Boruta-project
   login: Windows Credential Manager → Windows Credentials → remove `git:https://github.com`.
   The next push asks you to sign in.
2. **Commit identity.** GitHub links commits to an account by email. Make sure the
   address used for commits is added and verified on the jacek-mar account, or set it
   for this repository only:
   `git config user.name "jacek-mar"` / `git config user.email "<address on the account>"`
   (or the private `…@users.noreply.github.com` address from GitHub settings).
3. Review `git status` — only source, docs, tests and assets should be included.

## Suggested commits

1. `Import v1.2.0–v1.3.0 work` (the copied baseline: MyMemory backend, UI presets, …)
2. `v1.4.0: new game log location, translation error handling, quota pause, email setting, cache`
3. `Docs: move links to GitHub, make jacek-mar the primary repository`

Tag: `v1.4.0`

## Pushing

```bash
git push origin main --tags     # jacek-mar fork (primary)
git push upstream main --tags   # Boruta-project (as collaborator)
```

Alternative for upstream: push only to the fork, then open a pull request
jacek-mar → Boruta-project and merge it. Slower, but leaves a reviewable record.

## After pushing

- Create the GitHub Release `v1.4.0` on jacek-mar and attach the Windows exe
  (build with `docs/building-executables.md`).
- In the Boruta-project README, add a note pointing to the jacek-mar repository as the
  primary home of the project.
- Optional: on jacek-mar, enable Issues (forks have them disabled by default) and
  consider GitHub Pages for the user guide.
- The app (≥ 1.4.0) reads `remote/welcome.json` and `game_dictionary.json` from `main`,
  so these only work once pushed. Push before announcing the release.
- Last jsonsilo update, for users on ≤ 1.3.0: set `version` to `1.4.0` and
  `download_url` to `https://github.com/jacek-mar/star-conflict-chat-translator/releases`
  in the jsonsilo welcome entry — after the GitHub Release exists.
