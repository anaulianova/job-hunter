# Mode: /track

**Purpose:** Sync pipeline and application data to the 'Job Hunter' Google Spreadsheet.

## Spreadsheet structure

| Sheet | Purpose | Written by |
|---|---|---|
| Sheet 1 — Tracker | Applied roles with status tracking | `--sync-tracker` |
| Sheet 2 — Pipeline | Full record of all evaluated roles | `--sync-pipeline` |
| Sheet 3 — Job Postings | User-pasted URLs for batch evaluation | User (manual input) |

## Setup (one-time)

```bash
uv run scripts/sheets.py --setup
```

Creates all 3 sheets and applies full formatting:
- Deletes the blank default "Sheet1" Google creates automatically
- Header row: **bold** and frozen. All data rows: plain (not bold).
- Dropdown validation with colour-coded cells:
  - Tracker Status: `Sent` (pink) · `First Screening` (yellow) · `Interview` (blue) · `Case Study` (orange) · `Rejected` (red, row greyed) · `Silent Rejection` (dark grey, row light-greyed) · `Offer` (green)
  - Job Postings Status: `Pending` (yellow) · `Evaluating` (orange) · `Skipped` (red) · `Evaluated` (green)

**Run once only.** Re-running stacks conditional formatting rules. To reset, delete the 3 tabs manually and re-run.

### Sheet columns

**Tracker** (7 cols): Company · Job Title · Status · Application Date · Medium · URL · Location

**Pipeline** (8 cols): Company · Job Title · Tier · Match Score · Evaluated Date · Location · URL · Notes

**Job Postings** (5 cols): URL · Company · Job Title · Date Added · Status

Requires:
- `config/google_creds.json` — Google service account credentials
- `GOOGLE_SHEET_ID` in `.env` — spreadsheet ID from the URL

## Syncing evaluated roles → Sheet 2 (Pipeline)

Run after every evaluation session:

```bash
uv run scripts/sheets.py --sync-pipeline
```

Appends all roles with any status except `discovered`. Deduplicates by URL.

## Syncing applications → Sheet 1 (Tracker)

Run after submitting an application:

```bash
uv run scripts/sheets.py --sync-tracker
```

Appends roles with statuses: `applied, screening, interview, offer, rejected, withdrawn, cv_tailored`.

## Updating a status in the Tracker

```bash
uv run scripts/sheets.py --update-status <url> "first screening"
```

Valid statuses: `Sent, First Screening, Interview, Case Study, Rejected, Silent Rejection, Offer`

## Processing your Sheet 3 queue

When you've pasted URLs into Sheet 3:

```bash
uv run scripts/sheets.py --get-pending-urls   # see what's queued
/scan --from-sheet                             # batch evaluate them
```

After evaluation, mark each URL done:

```bash
uv run scripts/sheets.py --mark-evaluated <url>
```
