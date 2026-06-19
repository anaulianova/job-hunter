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
- Look for `cv/record/cv_{company-slug}_{date}.md` and `cv/pdf/{company-slug}_{date}.pdf`
- If found: "CV ready: `cv/pdf/{company-slug}_{date}.pdf` → rename to `CV_{FirstName}_{LastName}.pdf` before uploading."
- If not found: "No tailored CV found for this role. Run the CV export first: `uv run scripts/cv_export.py --company {company-slug} --date {date}`"

**Title consistency check.** Before confirming the CV, scan `pipeline/pipeline.json` for other non-skipped/non-withdrawn entries at the same company.
- If any exist: identify the entry with the highest match score and check which title variant was used in its CV amendments (from the evaluation report).
- Verify the current CV uses the **same title variant** for any role with `permitted_title_variants`.
- If a mismatch is found: flag it before the user proceeds — `⚠ TITLE MISMATCH — [Company]: This CV uses "[current variant]" but the [Job Title] application ([Score]/100) uses "[locked variant]". Amend this CV to match before submitting.`
- Do not proceed to Q&A generation until the user has confirmed the CV title is consistent.

---

## Step 2 — Generate Application Q&A

Load `config/question_bank.json`. For each question, apply the tier rule:

### Tier handling per question

**`boilerplate`** — pull the pre-written text directly, substituting geography/role where noted. No generation.

**`standard`** — light generation: take the boilerplate and insert the company name, role title, and one specific detail from the JD. ~1 sentence of personalisation.

**`personalise`** — full generation from the JD and evaluation report. Substantive, role-specific answer. Reference something concrete from the JD.

**`ask_user`** — before generating, ask: "What angle do you want to take for [question] at [company]? (e.g. a specific product, mission aspect, or experience to lead with)" — then generate from their answer. If no response, generate a best-effort answer and flag it for review.

### Voice and tone rules (apply to all generated answers)

- **No em dashes.** Never use `--` in written copy. Restructure the sentence instead. It is a dead giveaway of AI-generated text.
- **Why this company** answers are about professional narrative fit, not flattery. Answer the implicit question: how does this role fit into my story, what can I bring, and what do I want to grow into? Showing ambition alongside honesty ("this is a deliberate stretch") is good. Corporate flattery ("X company sits at the intersection of Y and Z") is not.
- **Note to hiring manager** is not a summary of the CV or the Why answer. It is one piece of context that makes the person stand out in under 10 seconds from a storytelling angle — something NOT evident from the resume or the Why answer. Pull from `profile.career_narrative` and `profile.proudest_achievement`. Keep it short. Do not exaggerate the background.
- **Every substantive answer must imply why this person would be a great candidate.** Not explicitly ("I would be a great fit because...") but through framing, story, and closing line. A reader who finishes any answer should come away with a sense of what this person would bring — not just that they want the job. The why-great-candidate signal can be subtle but it must be present.
- All claims must be factually accurate and defensible. If unsure whether a specific claim is correct, omit it rather than approximating.

### Tier rules summary

| Question | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|
| Salary (narrative) | personalise | standard | boilerplate |
| Salary (number) | personalise | standard | boilerplate |
| Why this company | ask_user | personalise | standard |
| Note to hiring manager | ask_user | personalise | standard |
| Additional info | personalise | standard | boilerplate (blank) |

---

## Step 2b — Isolated reviewer pass

After drafting all answers, spawn an isolated reviewer agent before presenting anything. This is not an in-context persona switch — it is a separate agent spawned via the Agent tool with explicit context injection.

### How to invoke

Spawn the reviewer using the Agent tool with the following injected context:

```
Agent(
  prompt = [contents of modes/reviewer.md]
           + "\n\nJOB DESCRIPTION:\n" + [full JD text]
           + "\n\nAPPLICATION ANSWERS:\n" + [answers as JSON]
)
```

Pass **only** the JD text and the generated answers. Do not pass the profile, career narrative, CV text, evaluation report, or any other context. The reviewer sees only what a real hiring team member would see — nothing more.

### Why a separate agent, not a persona switch

An in-context reviewer has the applicant's profile and background in its context window whether instructed to ignore it or not. A spawned subagent with explicit context injection is isolated by construction — it cannot access what wasn't passed to it. This is the mechanism that makes the reviewer reliable.

### What the reviewer returns

The reviewer returns the complete revised Q&A as a JSON object. Apply those revisions silently. Do not surface the reviewer's changes or notes to the user at any point — only the final revised answers enter the sync step.

---

## Step 3 — Sync directly to Google Sheets

Do not show the answers to the user before syncing. Run silently:

1. Call `uv run scripts/sheets.py --sync-qa "[company]" "[job_title]" "[answers_json]"` to push answers to Sheet 4
2. Update `pipeline.json` status → `applied`, set `application_date` to today
3. Call `uv run scripts/sheets.py --sync-tracker` to push to Sheet 1 with status `Queued`

The Tracker row lands as **Queued** (turquoise). The user fills out and submits the application manually, then updates the status to **Sent** — either by editing the dropdown in the sheet directly, or by asking: "mark [company] as sent".

Then confirm with a single line:

```
[Job Title] at [Company] queued. Q&A in Sheet 4, application ready in Sheet 1. Ask me to pull up any answer to review, or say "mark [company] as sent" once you've submitted.
```

The user can then ask to see and refine individual answers in conversation. This keeps the context loop open — improvements feed back into how future answers are generated — without front-loading a wall of text for every application.

---

## Batch mode: `/apply --batch`

Use when preparing multiple applications at once. Evaluations remain sequential — batch mode handles the application prep phase only. No user input is required between roles; the user returns to a summary table.

### When to use

Run after a session of `/evaluate` where multiple roles were tiered and confirmed. Batch mode processes all roles that are ready to apply but haven't been applied to yet.

### Flow

**Step 1 — Load the queue.**
Read `pipeline/pipeline.json`. Collect all entries where:
- `status` is `evaluated` or `cv_tailored`
- `tier` is `tier1` or `tier2` (Tier 3 uses boilerplate — apply individually via `/apply [company]` if needed)
- `application_date` is null

Display as a numbered list:
```
Roles ready to apply (N total):
[1] Anthropic — Data Scientist, Safeguards — Tier 1
[2] Stripe — Product Manager, Capital — Tier 2
[3] Coinbase — Payments Risk Analyst II — Tier 2

Enter numbers to include (e.g. 1,3) or 'all':
```

**Step 2 — Process each role in sequence.**
For each selected role, run silently:

1. Generate Q&A answers (Step 2 rules — tier handling, voice and tone rules all apply per role)
2. Spawn isolated reviewer (Step 2b) — pass only JD + answers, no profile
3. Apply reviewer revisions
4. Sync answers to Sheet 4: `uv run scripts/sheets.py --sync-qa ...`
5. Update `pipeline.json` status → `applied`, set `application_date` to today
6. Sync to Sheet 1: `uv run scripts/sheets.py --sync-tracker` — row lands as `Queued`

Do not pause for confirmation between roles. If a tailored CV is missing for a role, note it in the summary but continue processing.

**Step 3 — Summary table.**
After all roles are processed, output a single summary:

```
Batch complete — N applications prepared and synced to Sheets.

Company        Title                        Tier  Q&A  CV
────────────────────────────────────────────────────────────────
Anthropic      Data Scientist, Safeguards    1     ✓    Tailored CV found
Stripe         Product Manager, Capital      2     ✓    No tailored CV — export first
Coinbase       Payments Risk Analyst II      2     ✓    Tailored CV found

Ask me to pull up any answer if you want to review or improve it.
```

### Cost note

Tier 1 and Tier 2 roles generate answers via LLM. Each role in the batch costs one generation pass plus one reviewer subagent call. Tier 3 uses boilerplate (zero generation cost) and should be run individually to avoid batching overhead for trivial applications.

---

## Adding New Questions

When the user encounters a question not in `config/question_bank.json`:
1. Generate a one-time answer for the current application
2. Ask: "Add this to the question bank for future applications?" — if yes, add it with appropriate `tier_handling` settings
3. Never skip a question the user flags as important

---

## Cost note

This command is intentionally decoupled from `/evaluate`. Answers are only generated when you decide to apply — not for every evaluated role. For Tier 3 roles, all answers use boilerplate (zero generation cost).
