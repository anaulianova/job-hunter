# Mode: /interview

**Purpose:** Prepare for an interview at a specific company. Generates expected questions, suggested answers grounded in your actual experience, and STAR stories mapped to the role.
**Input:** `/interview [company]` — company name as it appears in your pipeline.

---

## Pre-flight

1. Load `profile/user_profile.json`
2. Load `pipeline/pipeline.json` — find the role by company name
3. Load the evaluation report from `pipeline/reports/` if it exists
4. Check for a research brief at `pipeline/reports/research_{company-slug}_*.md` if it exists
5. Confirm: "Preparing interview pack for [Job Title] at [Company]. What stage is this? (e.g. first call, technical, final panel)"

Wait for the user's answer — the prep looks very different for a recruiter screen vs. a technical panel vs. a final round.

---

## Interview stages

### Recruiter / HR screen

Focus: background walkthrough, motivation, logistics.

Generate:
- **Walk me through your background** — 3-minute narrative arc tailored to this role, in the user's voice. Should move from past → present → why this role, using the framing most relevant to this JD. Never a CV recitation.
- **Why this company?** — Pull from research brief if it exists. 3–4 sentences, specific to what the company is doing right now.
- **Why are you looking?** — Honest, forward-looking, no negativity about previous employers.
- **Salary expectations** — Load from `profile.search_parameters` and AGENTS.md Salary Rules. Anchor at top of range for the geography.
- **Visa / right to work** — Load from `profile.visa_status` for the relevant geography.

---

### Hiring manager / team interview

Focus: fit, judgment, domain depth, how you work.

Generate:
- **5 behavioural questions** most likely for this role type and level, based on the JD
- For each: a suggested STAR answer (Situation, Task, Action, Result) drawn from the user's actual experience — never invented examples
- **3 domain questions** specific to the role's technical or subject-matter requirements
- **Questions to ask the interviewer** — 4–5 sharp questions that signal genuine curiosity and research. No generic questions ("what does success look like in this role" is overused — find something more specific).

---

### Technical / case interview

Focus: skills demonstration, problem-solving approach.

Generate:
- What technical components are likely based on the JD (e.g. SQL, Python, stats, product sense, case study)
- 3 practice questions at the appropriate level for the role
- For each: the approach the user should take, drawing on their relevant experience and tools
- One worked example if relevant

---

### Final round / panel

Focus: culture fit, leadership, big-picture thinking.

Generate:
- **Executive-level questions** likely at this stage (vision, trade-offs, leadership scenarios)
- For each: a suggested answer that demonstrates range and judgment
- **Negotiation prep** — if an offer is coming, load salary target from profile and prep the user on how to handle the conversation without anchoring low
- **Questions to close** — 2–3 questions that signal long-term seriousness about the role

---

## STAR story bank

Regardless of stage, generate 3–5 STAR stories from the user's experience that are versatile across common behavioural questions:

```
STORY: [Title — e.g. "Founding A.R.I.A. and closing VARA"]
BEST FOR: [list of question types this story answers]
SITUATION: [1–2 sentences]
TASK: [1 sentence]
ACTION: [2–3 sentences — the specific things the user did]
RESULT: [1–2 sentences — quantified where possible]
```

Rules for STAR stories:
- Draw only from the user's actual experience — never invent
- Results must be honest and defensible — no inflated numbers
- Keep each story under 2 minutes when spoken aloud
- Flag if a story relies on a sensitive role (load `profile.sensitive_roles`) — use approved framing only

---

## Sensitive role handling

If any interview question is likely to surface a sensitive role (e.g. "walk me through your recent experience"), load `profile.sensitive_roles` and apply the same include/exclude logic as Point 4 of `/evaluate`. Use only `approved_framing` — never improvise.

---

## Output format

```
══════════════════════════════════════
INTERVIEW PREP — [Company] | [Job Title] | [Stage]
══════════════════════════════════════

WALK ME THROUGH YOUR BACKGROUND
[narrative]

──────────────────────────────────────
WHY [COMPANY]
[answer]

──────────────────────────────────────
BEHAVIOURAL QUESTIONS
[question + STAR answer × 5]

──────────────────────────────────────
DOMAIN / TECHNICAL QUESTIONS
[question + approach × 3]

──────────────────────────────────────
STAR STORY BANK
[stories × 3–5]

──────────────────────────────────────
QUESTIONS TO ASK
[4–5 questions]

══════════════════════════════════════
```

After output: "Anything you want to drill on? I can generate more questions for a specific area, do a mock Q&A, or work through a technical practice problem."

---

## Mock Q&A

If the user wants to practise:
- Ask one question at a time
- Wait for the user's answer
- Give specific, honest feedback: what landed, what was vague, what to cut or sharpen
- Never just say "great answer" — that's useless
