# Remote content

The app downloads two files from this repository's `main` branch (via
`raw.githubusercontent.com`) at most once per hour:

| File | Used for |
|---|---|
| [`remote/welcome.json`](welcome.json) | Welcome message, "what's new" list and new-version notice |
| [`../game_dictionary.json`](../game_dictionary.json) | Community game dictionary (only when the user enables *Remote dictionary sync* in Settings) |

Changes reach users after they are **pushed to `main`**: within the app's fetch interval
(1 hour) plus GitHub's raw-file cache (about 5 minutes). Both files must stay valid JSON —
check with `python -m json.tool remote/welcome.json` before pushing. A broken file is
ignored by the app (it logs a warning and keeps the last good content).

## `welcome.json` fields

| Field | Meaning |
|---|---|
| `id` | Increase it (e.g. `"004"` → `"005"`) to show the welcome message again to everyone (shown on the next 10 starts). |
| `version` | Latest released app version. Users with an older version see the extended message with `whats_new`, `download_url` and `notes`. Set it **after** the release exists on GitHub. |
| `color` | Tk colour name for the welcome text, e.g. `DodgerBlue`. |
| `welcome_message` | Main text, `\n` for new lines. |
| `whats_new.changes` | List of changes shown in the version notice. |
| `download_url` | Where to get the new version (the Releases page). |
| `notes` | Extra line shown under the version notice. |

## Older app versions

Versions up to 1.3.0 still read the former jsonsilo.com endpoints. To reach those users,
update the jsonsilo welcome entry once more (set `version` to the new release and
`download_url` to this repository's Releases page).
