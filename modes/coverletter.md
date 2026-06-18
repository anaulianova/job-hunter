# Mode: /cover

**Purpose:** Write a tailored cover letter for a Tier 1 application.
**Input:** `/cover [company]` — run after `/apply`, not after `/evaluate`.
**Tier restriction:** Tier 1 only. If the role is Tier 2 or 3, ask the user to confirm before proceeding — cover letters are a significant time investment and rarely move the needle outside Tier 1.

---

## Pre-flight

1. Load `profile/user_profile.json`
2. Load `pipeline/pipeline.json` — find the role by company name
3. Load the evaluation report from `pipeline/reports/`
4. Confirm: "Writing cover letter for [Job Title] at [Company] — Tier [X]."

If the role is not in the pipeline or has no evaluation report: "I don't have an evaluation report for this role. Run `/evaluate` first so I have the JD analysis to work from."

---

## Step 1 — Ask for the angle

Before writing a single word, ask:

> "What angle do you want to lead with for [Company]?
>
> For example:
> - A specific product or feature you find genuinely interesting
> - A recent company decision or moment that resonated with you
> - The exact problem this role is hired to solve and why you're the right person for it
> - A specific piece of your background that maps directly to their situation
>
> The opening paragraph lives or dies on this. A vague answer produces a generic letter — give me something concrete."

Wait for the user's answer before writing anything.

---

## Step 2 — Draft the cover letter

Four paragraphs. No more. Structure:

**Paragraph 1 — The hook (3–4 sentences)**
Lead with the angle the user gave. Reference something specific about the company — a product decision, a public statement, a recent move, a specific team. Never open with "I am writing to apply for..." or any variant. Never open with a compliment ("I have long admired...").

**Paragraph 2 — The evidence (3–4 sentences)**
Connect the user's most relevant experience directly to the role's core problem. This is not a CV summary — pick one or two specific things that map tightly. Use the evaluation report (Point 2 red flags, Point 3 amendments) to know what gaps to pre-empt or what strengths to lead with.

**Paragraph 3 — The fit (2–3 sentences)**
Say explicitly why this role at this company, not just any role. Reference the company's trajectory, mission, or a specific team dynamic that is relevant. Grounded in the angle from Step 1.

**Paragraph 4 — The close (1–2 sentences)**
Confident, direct. No throat-clearing. No "I look forward to discussing." A clean close that matches the tone of the letter.

---

## Rules (never violate)

- Never open with "I am writing to apply for..."
- Never use generic praise ("exciting opportunity", "fast-growing company", "innovative team")
- Never repeat the CV — a cover letter that summarises the CV wastes the reader's time
- Never use terms listed in `profile.forbidden_descriptions`
- Tone must match the company: a market maker cover letter reads differently from a policy org cover letter — calibrate to the sector and culture
- All claims must be honest and defensible in an interview
- Maximum 4 paragraphs, no exceptions

---

## Output format

```
══════════════════════════════════════
COVER LETTER — [Company] | [Job Title]
══════════════════════════════════════

[Paragraph 1]

[Paragraph 2]

[Paragraph 3]

[Paragraph 4]

══════════════════════════════════════
Word count: ~[N]
```

After outputting: "Does this angle land? Happy to sharpen the opening or reframe paragraph 2 if the evidence isn't landing right."

---

## Saving the cover letter

After the user approves: save to `submitted/cover_{company-slug}_{date}.md`.
