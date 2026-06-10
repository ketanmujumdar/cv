# Resume Builder + Application Tracker

Two systems live here:

1. **Resume builder** — generate tailored HTML/PDF resumes per company from YAML configs.
2. **Application tracker** — sync those configs into a Google Sheet, then manage application status (LinkedIn link, recruiter email, contact channel, notes, etc.) from the terminal.

---

## 1. Resume builder

### Setup (one-time)

```bash
pip3 install --break-system-packages --user pyyaml jinja2

# Optional: PDF export
pip3 install --break-system-packages --user playwright
playwright install chromium
```

### Build

```bash
python3 resumes/build.py flo_energy            # one company → HTML
python3 resumes/build.py flo_energy --pdf      # + PDF
python3 resumes/build.py --all                 # all configs
python3 resumes/build.py --list                # show available configs
```

Output: `resumes/output/<company>.html` and `.pdf`.

### Dev server (live reload)

```bash
python3 resumes/serve.py flo_energy            # build + serve + watch
python3 resumes/serve.py flo_energy --pdf      # also re-export PDF on change
python3 resumes/serve.py --all --port 9000
```

Serves at `http://localhost:8080`. Watches `resumes/data/` and `resumes/templates/`.

### How it works

- `resumes/data/base.yml` — shared profile (contact, experience, skills, education).
- `resumes/data/<company>.yml` — overrides (headline, summary, skill emphasis, theme colors, cover letter).
- `resumes/templates/modern.html` — Jinja2 template.
- `build.py` merges base + company override and renders.

### Add a new company

```bash
cp resumes/data/sonar.yml resumes/data/newcompany.yml
$EDITOR resumes/data/newcompany.yml
python3 resumes/serve.py newcompany
```

---

## 2. Application tracker (Google Sheets)

The sheet is your database. Two scripts handle structure + sync, one CLI handles day-to-day updates.

### Files

| File | Purpose |
|---|---|
| `sheet_common.py` | Shared env loader, auth, column definitions |
| `setup_sheet.py` | One-time: format Applications tab + create Dashboard tab |
| `sync_tracker.py` | Sync `data/*.yml` → sheet rows (idempotent) |
| `track.py` | CLI to read/update rows from the terminal |
| `.env` | Sheet ID + creds path (**gitignored**) |
| `.env.example` | Template for `.env` |

### One-time setup

1. **Google Cloud Console**
   - Create project → enable **Google Sheets API** and **Google Drive API**.
   - Create a **service account**, download its JSON key.
   - Drop the JSON in `_creeds/` (gitignored).

2. **Google Sheet**
   - Create blank sheet.
   - Share it with the service account email (Editor).
   - Copy the sheet ID from the URL: `docs.google.com/spreadsheets/d/<ID>/edit`.

3. **Local config**
   ```bash
   cp resumes/.env.example resumes/.env
   $EDITOR resumes/.env
   # fill in:
   #   GOOGLE_SHEET_ID=...
   #   GOOGLE_CREDS_PATH=_creeds/<your>.json
   #   GOOGLE_SHEET_TAB=Applications
   ```

4. **Install Python deps**
   ```bash
   pip3 install --break-system-packages --user gspread google-auth
   ```

5. **Run setup + first sync**
   ```bash
   python3 resumes/setup_sheet.py     # formats sheet, creates Dashboard
   python3 resumes/sync_tracker.py    # populates rows from data/*.yml
   ```

### Sheet structure

**Applications tab** — one row per company config.

| Column | Type | Managed by |
|---|---|---|
| Company | text | auto (`sync_tracker.py`) |
| Role | text | auto |
| Headline | text | auto |
| Theme | hex color | auto |
| HTML | path | auto |
| PDF | path | auto |
| Updated | date | auto |
| **Status** | dropdown | manual |
| **Date Applied** | date | manual |
| **Source** | text (where you found the role) | manual |
| **Contact** | text (recruiter name) | manual |
| **Next Action** | text | manual |
| **Notes** | text (multi-line) | manual |
| **Link** | URL (job posting) | manual |
| **Email** | text | manual |
| **Reached Via** | dropdown | manual |

**Status values**: `Drafted`, `Submitted`, `Screening`, `Interview`, `Offer`, `Rejected`, `Withdrawn` — each gets its own background color.

**Reached Via values**: `LinkedIn`, `Email`, `Referral`, `Portal`, `Recruiter`, `Cold outreach`, `Other`.

**Dashboard tab** — live status counts via `COUNTIF`.

### CLI — `track.py`

Use this instead of opening the sheet for quick updates.

```bash
# Read
python3 resumes/track.py list                                       # table view of all
python3 resumes/track.py show visa                                  # full row

# Status / dates
python3 resumes/track.py status visa Interview
python3 resumes/track.py applied bakuun                             # marks Submitted + today
python3 resumes/track.py applied bakuun 2026-06-01                  # specific date

# Job details
python3 resumes/track.py link visa "https://linkedin.com/jobs/view/..."
python3 resumes/track.py email visa "jane@visa.com"
python3 resumes/track.py via visa LinkedIn

# Notes (timestamped, appends)
python3 resumes/track.py note flo_energy "Recruiter call Thu 3pm"

# Generic field setter
python3 resumes/track.py set sonar Contact "Jane Doe"
python3 resumes/track.py set sonar Source "AngelList"
python3 resumes/track.py set sonar 'Next Action' "Follow up Monday"
```

Company names match by prefix if unique (`vi` matches `visa` if it's the only match).

### Add a new company end-to-end

```bash
cp resumes/data/sonar.yml resumes/data/acme.yml
$EDITOR resumes/data/acme.yml
python3 resumes/build.py acme --pdf
python3 resumes/sync_tracker.py
python3 resumes/track.py link acme "https://acme.com/jobs/123"
python3 resumes/track.py via acme Referral
python3 resumes/track.py applied acme
```

### What sync does (and does not)

- `sync_tracker.py` only touches **auto columns** (left side). Your status, notes, link, email — all safe.
- Re-running sync on existing companies refreshes Role/Headline/HTML/PDF paths from the yml.
- New companies appear with `Status=Drafted`.

### API quota

Setup ~3 calls. Sync = 1 read + 1-2 writes. Each `track.py` command = 1 read + 1-2 writes. Google's quota is 60/min — we use well under 5% per command.

### Security

`resumes/.env`, `_creeds/`, and any `*-service-account*.json` / `*-credentials*.json` are gitignored. Never commit them — this repo is public.

To rotate credentials: delete the old JSON, generate a new key in Cloud Console, drop it in `_creeds/`, update `GOOGLE_CREDS_PATH` in `.env`.
