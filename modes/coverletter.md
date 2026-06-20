# Mode: /cover

**Purpose:** Write a tailored cover letter for a Tier 1 application.
**Input:** Auto-triggered by `/apply` on Tier 1 roles. Can also be run standalone: `/cover [company]`.
**Tier restriction:** Tier 1 only. If Tier 2 or 3, ask for explicit confirmation before proceeding.

---

## Pre-flight

1. Load `profile/user_profile.json`
2. Load `pipeline/pipeline.json` — find the role by company name
3. Load the evaluation report from `pipeline/reports/`
4. Confirm: "Writing cover letter for [Job Title] at [Company] — Tier [X]."

If the role has no evaluation report: stop and prompt: "Run `/evaluate` first — I need the JD analysis to write from."

---

## Step 1 — Choose the angle

Before writing anything, present two options:

> **Standard cover letter** — 3–4 paragraphs making a specific, honest case for the candidacy. Best for most roles.
>
> **Wild card (Claude URL)** — A short letter that links to a Claude-generated case for the candidacy instead of prose. Signals tech-savviness and AI fluency. Works well for AI-native companies, developer-tools firms, and forward-thinking startups. **Not suitable for traditional finance, large banks, or any company with restricted external web access.**

Then ask:

> "What angle do you want to lead with for [Company]?
>
> For example:
> - A specific product or feature you find genuinely interesting
> - A recent company decision or moment that resonated with you
> - The exact problem this role is hired to solve and why you're the right person for it
> - A specific piece of your background that maps directly to their situation
>
> The opening paragraph lives or dies on this. Give me something concrete — a vague answer produces a generic letter."

Wait for the user's answer before writing.

---

## Step 2 — Draft the cover letter

### Standard format

Four paragraphs. No more. Structure:

**Paragraph 1 — The hook (2–3 sentences)**
Lead with the angle the user gave. Reference something specific about the company — a product decision, a recent move, the exact problem. Never open with "I am writing to apply for..." or any variant. Never open with flattery ("I have long admired..."). Starting with "I'm applying for the [Role] role because..." is acceptable when followed immediately by a specific, concrete reason.

**Paragraph 2 — The evidence (3–4 sentences)**
Connect the most relevant experience directly to the role's core problem. This is not a CV summary — pick one or two specific things that map tightly. Use the evaluation report (Point 2 red flags, Point 3 amendments) to know what gaps to pre-empt and what strengths to lead with. If there is a known gap (e.g. DeFi for a DeFi role), address it directly and honestly — do not paper over it.

**Paragraph 3 — The fit (2–3 sentences)**
Say explicitly why this role at this company, not just any role. Reference the company's trajectory, mission, or a specific team dynamic. Grounded in the angle from Step 1.

**Paragraph 4 — The close (1–2 sentences)**
Confident and direct. Include any relevant logistics if needed (location, right to work, relocation). No throat-clearing.

### Wild card format

```
Dear Hiring Team,

I'm applying for the [Role] role at [Company].

In an effort to save you the time of reading yet another generic cover letter, I've had Claude put together an honest and truthful assessment of my qualifications for this role. You can review it here:

[CLAUDE_SHARE_URL — user must provide this]

Should the case for my candidacy prove compelling, I'd welcome the opportunity to discuss further.

Thank you for your time and consideration.

Sincerely,

Anastasia
```

**Note to user when wild card is chosen:** "You'll need to create and paste a Claude share URL here — open a Claude conversation, ask it to assess your fit for this role, and use the share button to get a public link. The URL goes in place of [CLAUDE_SHARE_URL]."

---

## Rules (never violate)

- Never open with "I am writing to apply for..."
- Never use generic praise ("exciting opportunity", "fast-growing company", "innovative team")
- Never repeat the CV — a cover letter that summarises the CV wastes the reader's time
- Never use terms listed in `profile.forbidden_descriptions`
- Tone must match the company: a market maker cover letter reads differently from an AI lab cover letter — calibrate to the sector and culture
- All claims must be honest and defensible in an interview
- Maximum 4 paragraphs for standard format
- **No em dashes.** Never use `—` or `--`. Restructure the sentence instead. This applies everywhere, including mid-sentence.
- **Never openly acknowledge a gap or weakness.** Phrases like "the DeFi gap is genuine", "I'll be honest about what I don't have", or "this is a stretch" hand the reader an argument to pass. If a gap exists, address it by reframing positively (what you bring that transfers) or leave it implicit. Never name it as a gap.
- **Para 1 must connect your specific experience to this specific role.** A good opener names what you did and draws a direct line to what this company is doing. Vague openers that just say you want the on-chain version of your past job are not enough.
- **Keep the evidence paragraph tight.** Do not explain how your previous employer's internal systems worked. The reader doesn't need to understand your company's plumbing — they need to understand what you can do. Cut any sentence that explains mechanics rather than demonstrating skill or result.
- **Never use pedantic parallels** ("X is structurally identical to Y — A replaces B, and C replaces D"). These read as overworked and lose the reader. If the connection is real, state it simply.
- **Never mention location or willingness to relocate in the cover letter.** This is handled in the Q&A section. It wastes space and can introduce unnecessary friction before the reader is sold.
- **Always close with a thank you** for the reader's time, followed by an invitation to discuss how your qualifications fit the role. This is the only closing formula.
- **Do not include personal details (address, phone) in the markdown file.** These are injected at PDF export time from `profile/user_profile.json`.

---

## Step 3 — Reviewer pass

After drafting, spawn an isolated reviewer agent before showing the letter to the user. This is not an in-context persona switch — it is a separate agent spawned via the Agent tool.

Spawn with:

```
Agent(
  prompt = "You are a hiring manager at [Company] who has read this job description carefully.
  You are reviewing a cover letter cold — the only context you have is what's written below.

  Read the cover letter and give feedback on 5 points:
  1. First sentence: does it immediately tell you what this is about and why this person?
  2. Evidence: does paragraph 2 make a specific, compelling case, or is it vague?
  3. Gap handling: if there is a known gap, is it handled directly and honestly, or avoided?
  4. Tone: does it sound like a person wrote it? Flag any em dashes, hedged phrases, superlatives, or AI-sounding copy.
  5. Closing: does the reader finish with a clear sense of what this person brings?

  Be direct. Do not soften your assessment. Return 3–5 specific bullet points.

  JOB DESCRIPTION:
  [full JD text]

  COVER LETTER BODY:
  [draft letter text]"
)
```

Pass **only** the JD text and the draft letter. Do not pass the profile, CV, evaluation report, or any other context.

Read the reviewer's feedback, apply the most important improvements, then show the revised letter to the user.

**Show the reviewer's feedback to the user** before the revised letter — this keeps the loop transparent. Format:

```
── Reviewer feedback ──────────────────────────
[feedback bullets]
───────────────────────────────────────────────

── Revised letter ─────────────────────────────
[revised letter body]
───────────────────────────────────────────────
```

---

## Step 4 — User approval and save

After the user approves, save the letter body to:
`app/coverletter/record/cover_{company-slug}_{date}.md`

The file contains only the letter body — no name, address, phone, or email. Those are injected at export time.

Then export to PDF:
```
uv run scripts/coverletter_export.py --company {company-slug} --date {date}
```

Output PDF: `app/coverletter/pdf/cover_{company-slug}_{date}.pdf`

Confirm: "Cover letter saved and exported. Rename to `Cover_Letter_Anastasia_Ulianova.pdf` before uploading."

---

## Output format (for display in chat)

```
── Reviewer feedback ──────────────────────────
[feedback bullets from reviewer]
───────────────────────────────────────────────

COVER LETTER — [Company] | [Job Title]
══════════════════════════════════════

[Paragraph 1]

[Paragraph 2]

[Paragraph 3]

[Paragraph 4]

Sincerely,

Anastasia

══════════════════════════════════════
Word count: ~[N]
```

After outputting: "Does this angle land? I can sharpen the opening or reframe paragraph 2."
