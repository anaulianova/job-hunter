# Mode: /evaluate

**Purpose:** Run the full 5-point evaluation on a job description. Accepts a URL, a file path, or pasted JD text.
**Input:** `/evaluate {url}` or `/evaluate {path}` or `/evaluate` then paste JD text, or auto-routed when user pastes a URL/JD directly.
**Output:** Structured evaluation report saved to `pipeline/reports/{company}_{date}.md` and entry added to `pipeline/pipeline.json`.

---

## JD Input Methods

Three ways to provide a job description, in order of preference:

1. **URL** — `/evaluate https://...` — system fetches and extracts the JD text
2. **File** — `/evaluate jds/polymarket.txt` — system reads from the `jds/` folder
3. **Paste** — paste raw JD text directly into chat (auto-routed, no command needed)

**If a URL fails to load** (JS-rendered page, login wall, LinkedIn, etc.):
> "Couldn't load this page — copy the job description text and paste it here, or save it to `jds/{company}.txt` and run `/evaluate jds/{company}.txt`."
Never silently skip or log "unable to fetch" without telling the user.

**`jds/` folder:** Save JD text files here for roles where the URL can't be scraped (LinkedIn, OpenAI, SWIFT, etc.). Filename convention: `{company}.txt` or `{company}_{role-slug}.txt`.

---

## Pre-flight

1. Load `profile/user_profile.json` — if missing, stop and route to `/onboard`
2. Load `cv.md` — if missing, stop and ask user to add their CV
3. Resolve JD input:
   - URL → fetch page, extract text; if fetch fails, prompt user per above
   - File path → read from `jds/` folder
   - Pasted text → use as-is

Confirm before starting: "Evaluating: [Job Title] at [Company]. Running 5-point analysis..."

---

## Point 1 — Role Suitability Check

Act as a senior hiring manager. Read the JD and answer:
- What is the core function of this role? (DS, analyst, ops, engineering, PM, research, etc.)
- What level is it? (IC3/junior, IC4/mid, IC5/senior, staff, manager)
- Is the location compatible with the user's search parameters?
- Does the salary range (if listed) meet the user's floor?

**Output:**
```
SUITABILITY: [SUITABLE / STRETCH / UNSUITABLE]
ROLE TYPE: [core function]
LEVEL: [level assessment]
RATIONALE: [one sentence]
```

If UNSUITABLE: stop here. Do not run Points 2–5. Log to pipeline with status `skipped`.
If STRETCH: flag clearly, but continue evaluation at the user's discretion.

---

## Point 2 — Fitness Analysis

Act as a senior recruiter who specialises in hiring for this type of role. Read the full JD against the user's CV and profile.

**Output:**
```
MATCH SCORE: [X/100]

TOP 5 MISSING KEYWORDS:
1. [exact term from JD]
2. [exact term from JD]
3. [exact term from JD]
4. [exact term from JD]
5. [exact term from JD]

3 RED FLAGS (visible in under 10 seconds):
1. [red flag — be specific and honest]
2. [red flag]
3. [red flag]

TIER: [1 / 2 / 3 / SKIP]
```

---

## Point 3 — ATS & Hiring Manager Audit

Act as both an ATS filter AND a hiring manager reading 200 CVs in one sitting.

First: identify which sections of the current CV would be skipped or downweighted for this role.

Then: provide exact rewrite amendments. Format each as:

```
─────────────────────────────────────
SECTION: [Role or Section Name]
ORIGINAL: [copy the existing bullet exactly as written]
REWRITE: [exact new copy — 2 lines max, paste-ready]
KEYWORD INSERTED: [which missing keyword from Point 2 this addresses]
─────────────────────────────────────
```

If a new bullet should be added (not a rewrite):
```
─────────────────────────────────────
SECTION: [Role or Section Name]
NEW BULLET: [exact copy — 2 lines max, paste-ready]
KEYWORD INSERTED: [keyword]
─────────────────────────────────────
```

After amendments: "These edits address [X] of the 5 missing keywords. Keywords not yet addressed: [list any remaining]."

---

## Point 4 — Airwallex Decision

Load the Airwallex rule from `profile/user_profile.json` → `sensitive_roles`.

Evaluate against this JD:
- Is AI workflow framing relevant? [yes/no]
- Does B2B SaaS context help? [yes/no]
- Is cross-functional ops experience valued? [yes/no]
- Is this a pure DS/ML role? [yes/no]
- Is this London-based institutional? [yes/no]

**Output:**
```
AIRWALLEX: [INCLUDE / EXCLUDE]
RATIONALE: [one sentence]
```

If INCLUDE, provide the approved framing to use:
```
APPROVED FRAMING:
• Assessed integration opportunities for AI-powered workflows across daily operations of an AI-native accounting platform.
• [second bullet if relevant, drawn from approved_framing in profile]
```

---

## Point 5 — About Me Rewrite

Write a new About Me paragraph for this specific role.

Rules:
- Maximum 3 sentences
- Lead with the framing most relevant to this JD
- Never use "political scientist"
- Honest and defensible

**Output:**
```
ABOUT ME (tailored):
[Sentence 1]
[Sentence 2]
[Sentence 3]
```

---

## Summary Output

After all 5 points, output a summary block:

```
══════════════════════════════════════
JOB-HUNTER EVALUATION SUMMARY
══════════════════════════════════════
Company:        [company]
Role:           [job title]
Location:       [location]
Tier:           [1 / 2 / 3]
Match Score:    [X/100]
Suitability:    [SUITABLE / STRETCH / UNSUITABLE]
Airwallex:      [INCLUDE / EXCLUDE]
══════════════════════════════════════
Next step: Review CV amendments above, update your CV, then run /track to log this role.
```

---

## Post-Evaluation Actions

1. Save full report to `pipeline/reports/{company_slug}_{YYYY-MM-DD}.md`
2. Add/update entry in `pipeline/pipeline.json`:
```json
{
  "company": "",
  "job_title": "",
  "tier": "",
  "match_score": 0,
  "status": "evaluated",
  "url": "",
  "location": "",
  "evaluated_date": "YYYY-MM-DD",
  "application_date": null,
  "cv_version": null,
  "notes": ""
}
```
3. Ask: "Would you like me to draft a cover letter for this role?" (Tier 1 only)
