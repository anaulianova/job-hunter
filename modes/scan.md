# Mode: /scan

**Purpose:** Discover new job listings via two routes: (A) automated company portal scanning, (B) user-provided URLs or LinkedIn CSV import.
**Output:** New entries added to `pipeline/pipeline.json` with status `discovered`. Deduplication against existing entries.

---

## Route Detection

When `/scan` is called:
1. If user provides a URL or list of URLs → Route B (manual input)
2. If user provides a file path ending in `.csv` → Route C (LinkedIn import)
3. If no argument → Route A (automated portal scan), then also run Route D
4. `/scan --from-sheet` → Route D only (Google Sheets queue)

---

## Route A — Automated Portal Scan

Run `scripts/scan.py` which:
1. Reads `config/targets.yml` for the list of target companies and their career page / ATS type
2. For each company, queries their ATS API (Greenhouse, Ashby, Lever) or scrapes their careers page
3. Filters results by: role keywords matching user archetypes, location matching search parameters
4. Deduplicates against `pipeline/pipeline.json`
5. Returns new listings only

After scan completes:
- Display new listings as a numbered list: `[N]. [Company] — [Title] — [Location] — [URL]`
- Ask: "Found [N] new roles. Which would you like to evaluate? (enter numbers, or 'all' to queue them all)"
- Queue selected roles for `/evaluate`

If no new roles found: "No new roles matching your profile found today. Targets checked: [list]. Next scheduled scan: tomorrow."

**Minimum scan frequency:** Once per day (when the system is running). Log last scan time in `pipeline/scan_log.json`.

---

## Route B — Manual URL Input

User provides one or more URLs:
```
/scan https://boards.greenhouse.io/stripe/jobs/12345
/scan url1, url2, url3
```

For each URL:
1. Fetch the page and extract job title, company, location, and full JD text
2. Add to `pipeline/pipeline.json` with status `discovered`
3. Immediately offer to evaluate: "Added [Title] at [Company]. Run evaluation now? (y/n)"

---

## Route C — LinkedIn CSV Import

User provides path to LinkedIn saved jobs export:
```
/scan ~/Downloads/SavedJobs.csv
```

Run `scripts/linkedin_import.py` which:
1. Reads the CSV (LinkedIn export format: `Job Title`, `Company Name`, `Location`, `Saved Date`, `Job URL`)
2. Deduplicates against existing pipeline entries
3. Adds new entries with status `discovered`
4. Reports: "Imported [N] new roles from LinkedIn export. [M] already in pipeline, skipped."

Display imported roles as numbered list. Ask which to evaluate.

---

## Route D — Google Sheets Job Postings Queue

Run when the user has pasted URLs into Sheet 3 ("Job Postings") of the Google Sheets tracker:

```bash
uv run scripts/sheets.py --get-pending-urls
```

This returns all URLs in Sheet 3 with status `pending` or blank.

For each URL:
1. Fetch the page and extract job title, company, location, and full JD text
2. Add to `pipeline/pipeline.json` with status `discovered`
3. Mark the URL as `evaluating` in Sheet 3: `uv run scripts/sheets.py --mark-evaluated <url>`
4. Queue for `/evaluate`

After evaluation, mark as `evaluated` in Sheet 3.

Display as numbered list. Ask: "Found [N] jobs from your Sheet 3 queue. Evaluate all now? (y/n)"

---

## Scan Log Entry (`pipeline/scan_log.json`)

```json
{
  "last_scan": "YYYY-MM-DDTHH:MM:SS",
  "companies_checked": [],
  "new_roles_found": 0,
  "errors": []
}
```
