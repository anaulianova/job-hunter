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

## Step 2b — Reviewer pass (internal, before showing user)

After drafting all answers, run a reviewer pass before presenting anything. Do not show the user the draft answers or the reviewer notes — only show the final revised answers after the pass is complete.

### Reviewer persona

You are a talent acquisition specialist or hiring manager at [Company]. You are reviewing hundreds of applications for this specific role. You have read the JD carefully. You know nothing about the applicant beyond what is written in these answers. You will skim, not read — the first sentence of each answer determines whether you keep reading. You have no patience for irrelevance.

**Critical constraint:** The reviewer has NO access to the user's profile, career narrative, or background context. It can only see the JD and the written answers. If something in an answer requires outside context to make sense, the reviewer will not have that context and the answer will fail.

### What the reviewer checks per answer

1. **Relevance to role** — does the answer directly serve the job being applied for? Anything that reads as off-topic given only the JD will lose the reader.
2. **First-sentence test** — if a skimmer reads only the first sentence, do they immediately understand the point? If not, the answer needs reordering.
3. **Length** — is it appropriate for a text box on an application form? "Why this company" should be 3–5 sentences max. "Note to HM" should be 2–3 sentences max.
4. **Coherence without context** — does the answer make sense to someone who knows nothing about the applicant? If a story or claim requires context the reviewer doesn't have, it will confuse rather than impress.
5. **Tone** — does it sound human and direct, or does it read as a prepared statement? Skimmers notice the difference.

### Reviewer output (internal only — never shown to user)

For each answer that needs adjustment:
```
REVIEWER NOTE — [Question]:
Issue: [one sentence on what fails the skim test]
Fix: [specific instruction for the rewrite]
```

Then silently apply the fixes. Do not surface the reviewer notes or the draft answers to the user at any point.

---

## Step 3 — Sync directly to Google Sheets

Do not show the answers to the user before syncing. Run silently:

1. Call `uv run scripts/sheets.py --sync-qa "[company]" "[job_title]" "[answers_json]"` to push answers to Sheet 4
2. Update `pipeline.json` status → `applied`, set `application_date` to today
3. Call `uv run scripts/sheets.py --sync-tracker` to push to Sheet 1

Then confirm with a single line:

```
Applied to [Job Title] at [Company]. Q&A synced to Sheet 4. Ask me to pull up any answer if you want to review or improve it.
```

The user can then ask to see and refine individual answers in conversation. This keeps the context loop open — improvements feed back into how future answers are generated — without front-loading a wall of text for every application.

---

## Adding New Questions

When the user encounters a question not in `config/question_bank.json`:
1. Generate a one-time answer for the current application
2. Ask: "Add this to the question bank for future applications?" — if yes, add it with appropriate `tier_handling` settings
3. Never skip a question the user flags as important

---

## Cost note

This command is intentionally decoupled from `/evaluate`. Answers are only generated when you decide to apply — not for every evaluated role. For Tier 3 roles, all answers use boilerplate (zero generation cost).
