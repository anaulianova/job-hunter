# Mode: /apply

**Purpose:** Prepare and submit an application. Generates application Q&A answers, confirms CV, updates pipeline, syncs Google Sheets.
**Input:** `/apply [company]` — company slug matches a role in `pipeline/pipeline.json` with status `evaluated` or `cv_tailored`.
**Run only when user decides to actually apply.** Do not run during evaluation — this is the execution step, not the research step.

---

## Pre-flight

1. Load `pipeline/pipeline.json` — find the matching role by company name (case-insensitive)
2. If multiple roles for the same company, list them and ask user to confirm which one
3. Load the evaluation report from `pipeline/reports/`
4. Load `config/question_bank.json` — the standard question list
5. Confirm: "Applying to [Job Title] at [Company] — Tier [X]. Generating application package..."

---

## Step 1 — Confirm CV

Check that the tailored CV exists:
- Look for `tailored/cv_{company-slug}_{date}.md` and `submitted/{company-slug}_{date}.pdf`
- If found: "CV ready: `submitted/{company-slug}_{date}.pdf` → rename to `CV_{FirstName}_{LastName}.pdf` before uploading."
- If not found: "No tailored CV found for this role. Run the CV export first: `uv run scripts/cv_export.py --company {company-slug} --date {date}`"

---

## Step 2 — Generate Application Q&A

Load `config/question_bank.json`. For each question, apply the tier rule:

### Tier handling per question

**`boilerplate`** — pull the pre-written text directly, substituting geography/role where noted. No generation.

**`standard`** — light generation: take the boilerplate and insert the company name, role title, and one specific detail from the JD. ~1 sentence of personalisation.

**`personalise`** — full generation from the JD and evaluation report. Substantive, role-specific answer. Reference something concrete from the JD.

**`ask_user`** — before generating, ask: "What angle do you want to take for [question] at [company]? (e.g. a specific product, mission aspect, or experience to lead with)" — then generate from their answer.

### Tier rules summary

| Question | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|
| Salary (narrative) | personalise | standard | boilerplate |
| Salary (number) | personalise | standard | boilerplate |
| Why this company | ask_user | personalise | standard |
| Note to hiring manager | ask_user | personalise | standard |
| Additional info | personalise | standard | boilerplate (blank) |

### Output format

```
══════════════════════════════════════
APPLICATION Q&A — [Company] | [Job Title] | Tier [X]
══════════════════════════════════════

SALARY EXPECTATION (free text):
[answer]

SALARY EXPECTATION (number):
[number]

WHY DO YOU WANT TO WORK HERE:
[answer]

NOTE TO HIRING MANAGER:
[answer]

ANYTHING ADDITIONAL:
[answer or "Leave blank."]

══════════════════════════════════════
```

---

## Step 3 — Sync to Google Sheets

After user confirms the answers are good:

1. Call `uv run scripts/sheets.py --sync-qa "[company]" "[job_title]"` to push answers to Sheet 4
2. Update `pipeline.json` status → `applied`, set `application_date` to today
3. Call `uv run scripts/sheets.py --sync-tracker` to push to Sheet 1

Confirm: "✅ Applied. Pipeline and tracker updated."

---

## Adding New Questions

When the user encounters a question not in `config/question_bank.json`:
1. Generate a one-time answer for the current application
2. Ask: "Add this to the question bank for future applications?" — if yes, add it with appropriate `tier_handling` settings
3. Never skip a question the user flags as important

---

## Cost note

This command is intentionally decoupled from `/evaluate`. Answers are only generated when you decide to apply — not for every evaluated role. For Tier 3 roles, all answers use boilerplate (zero generation cost).
