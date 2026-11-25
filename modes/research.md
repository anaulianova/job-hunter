# Mode: /research

**Purpose:** Produce a structured company brief before an application or interview. Gives you the context to write a sharper cover letter, answer "why this company?" with specificity, and walk into an interview knowing the terrain.
**Input:** `/research [company]` — company name as it appears in your pipeline, or any company name.
**Output:** Structured brief saved to `pipeline/reports/research_{company-slug}_{date}.md`.

---

## Pre-flight

1. Load `profile/user_profile.json`
2. Check `pipeline/pipeline.json` for any existing evaluation of this company — load role context if found
3. Confirm: "Researching [Company]. This will take a moment..."

---

## Research areas

Run WebSearch across all sections. Cite sources inline. Flag anything that contradicts other sources or seems outdated.

---

### 1. Company snapshot

- What does the company actually do — in one plain sentence (not their marketing copy)
- Business model: how do they make money
- Stage: public / private / pre-IPO — and approximate valuation or last funding round
- Headcount (approximate) and growth trajectory
- Key investors or acquirers if relevant

---

### 2. Recent developments (last 6–12 months)

- Funding rounds, acquisitions, or major product launches
- Leadership changes (new CEO, CTO, relevant team leads)
- Layoffs, restructures, or hiring freezes — flag clearly if found
- Press coverage: what is the company known for right now, good or bad
- Regulatory or legal exposure relevant to the role

---

### 3. Product and technology

- Core product(s) — what problem do they solve, for whom
- Technical differentiation: what do they claim makes them different
- Any public engineering or research output (blog posts, papers, open source)
- Known tech stack if relevant to the role

---

### 4. The role in context

If an evaluation report exists for this company:
- Restate the role's core problem (from Point 1)
- Which team is this role likely on — infer from JD if not stated
- What does success look like in this role in year 1

If no evaluation report: skip this section and note it.

---

### 5. Competitive landscape

- Top 2–3 competitors and how the company is positioned against them
- Market tailwinds or headwinds
- Who is winning and why — honest assessment

---

### 6. Culture and working style

- Remote / hybrid / in-office policy
- Glassdoor or Blind signal (with date — these decay fast)
- Known interview process: rounds, formats, known technical components
- Any red flags in public reviews worth noting

---

### 7. Conversation hooks

3–5 specific, concrete things you could reference in a cover letter or interview that signal you've done real research — not generic facts everyone knows:

- A specific product decision that is interesting or bold
- A recent piece of engineering or research worth mentioning
- A market bet the company is making that you have a view on
- A tension or challenge in their space that the role likely touches

These should be specific enough that mentioning them in an interview would land as genuine knowledge, not surface-level research.

---

## Output format

```
══════════════════════════════════════
COMPANY BRIEF — [Company]
Generated: [date]
══════════════════════════════════════

SNAPSHOT
[content]

RECENT DEVELOPMENTS
[content]

PRODUCT & TECHNOLOGY
[content]

THE ROLE IN CONTEXT
[content or "No evaluation report found — run /evaluate first."]

COMPETITIVE LANDSCAPE
[content]

CULTURE & WORKING STYLE
[content]

CONVERSATION HOOKS
1. [specific hook]
2. [specific hook]
3. [specific hook]
...

══════════════════════════════════════
Sources: [inline citations from search]
```

Save to `pipeline/reports/research_{company-slug}_{date}.md` after output.

After saving: "Brief saved. Use the conversation hooks in your cover letter or to answer 'why this company?' — run `/cover [company]` when you're ready to write."
