# job-hunter

![Built with Claude Code](https://img.shields.io/badge/built%20with-Claude%20Code-blueviolet) ![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![License: MIT](https://img.shields.io/badge/license-MIT-green) ![Human in the loop](https://img.shields.io/badge/human--in--the--loop-always-orange)

Job searching sucks. 

It's slow, imprecise, and demoralising. But it doesn't have to be anymore. job-hunter is an agentic system built on Claude Code that handles the analysis, tailoring, and tracking — so you spend your time on the applications that actually fit. It evaluates every role like a senior recruiter would, rewrites your CV with exact copy, and generates application answers that sound like you.

I battle-tested this system while applying to hundreds of jobs myself. The job market is broken. Doesn't mean we have to break with it.  

> Engineers always get the best tools. This one is for everyone.

*This project was inspired by [career-ops](https://github.com/santifer/career-ops) by Santiago Ferreira. Thanks! Without seeing what you built, I wouldn't have thought to formalise my process to share with the world. I hope this can be useful to someone out there as much as it has for me.*

---

## What job-hunter does

You start by having a conversation. job-hunter learns who you are — not just the CV, but the context behind it: the roles you want to frame carefully, the titles that don't capture what you actually did, the words you never want used to describe you, the salary you won't go below. That profile is saved and used in every evaluation from that point forward.

From there, the workflow runs like this: you feed it a job description (URL, pasted text, or a saved file), and it runs a **five-point evaluation** — suitability check, fitness score out of 100, missing keywords, ATS audit with line-by-line CV rewrites, sensitive role decisions, and a tailored About Me. The CV amendments are exact copy, not suggestions. You can either paste them directly or use the generated PDF from my CV template. 

But applying is not just tailoring your CV — it's answering all those "Why do you want to work at this company?" questions. When you decide to apply, job-hunter generates answers to every standard application question in the background, runs an internal reviewer pass that simulates a hiring manager skimming them, and syncs everything directly to your Google Sheets tracker. The answers land in Sheet 4 without interrupting your flow. Pull up any answer in conversation to refine it, and each improvement feeds back into how future answers are generated.

The more you use it, the better it knows you. Framing decisions you make early, sensitive roles you decide to include or exclude, application answers that worked — all of it accumulates in your profile and improves every subsequent evaluation.

---

## How it works

```
/onboard
  └── Conversational setup: CV ingestion, background context, role archetypes,
      salary floor, sensitive role framing. Saved to profile/user_profile.json.
        │
        ▼
/scan  or  paste a URL  or  save to jds/company.txt
  └── Job discovery via company portals, URL input, or Sheet 3 batch queue.
        │
        ▼
/evaluate
  └── 5-point analysis: suitability, fitness score, missing keywords,
      CV amendments (exact copy), sensitive role decision, About Me rewrite.
        │
        ▼
Tailor your CV
  └── Apply amendments from the evaluation report. Export to PDF runs
      automatically during /apply — one page, always.
        │
        ▼
/apply
  └── Q&A generation (salary, why this company, note to HM),
      internal reviewer pass, silent sync to Google Sheets Sheet 4.
      Ask to review any answer in conversation to refine it.
        │
        ▼
/track  /research  /interview
  └── Status updates, company research briefs, interview prep by stage.
```

---

## Getting started

**You will need four things before running anything:**

- **[Claude Code](https://docs.claude.ai/en/docs/claude-code/getting-started)** — the AI assistant this system runs on. Free tier available. This is what powers the analysis, writing, and evaluation.
- **[Python 3.10+](https://www.python.org/downloads/)** — the programming language the supporting scripts run on. You do not need to write any code.
- **A Google account** — for the Sheets tracker that logs your pipeline, applications, and Q&A answers.
- **[Git](https://git-scm.com/downloads)** — for downloading the project to your computer. If you have never used it, the install is one click.

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/anaulianova/job-hunter.git
cd job-hunter
```

**2. Install dependencies**
```bash
uv pip install -r requirements.txt
```

**3. Run the health check**
```bash
uv run scripts/healthcheck.py
```
This checks your Python version, all dependencies, your `.env` file, Google credentials, CV, profile, and output directories. It tells you exactly what is missing and how to fix it — run it again after fixing anything until everything passes.

**4. Set up Google Sheets**

<details>
<summary>Click to expand — 5-step Google Sheets setup</summary>

1. Go to [console.cloud.google.com](https://console.cloud.google.com), create a new project, and enable the **Google Sheets API**.
2. Navigate to **APIs & Services → Credentials → Create Credentials → Service Account**. Give it a name and click through.
3. Open the service account, go to **Keys → Add Key → JSON**. Download the file and save it as `config/google_creds.json` in this project.
4. Create a new Google Sheet. Share it with the service account email address (found in the JSON file under `client_email`) — give it **Editor** access.
5. Copy the spreadsheet ID from the URL (`docs.google.com/spreadsheets/d/**{THIS PART}**/edit`) and add it to a `.env` file in the project root:
   ```
   GOOGLE_SHEET_ID=your_spreadsheet_id_here
   ```

Then run:
```bash
uv run scripts/sheets.py --setup
```
This creates all four tabs (Tracker, Pipeline, Job Postings, App Q&A) with headers, dropdowns, and colour coding.

</details>

**5. Open Claude Code in the project directory**
```bash
claude
```

**6. Run `/onboard` to start**

Type `/onboard` in Claude Code. It will walk you through everything — CV ingestion, background questions, role archetypes, salary floor, and any roles you want to frame carefully. Takes about 10 minutes. You only do it once.

---

## Feeding it job descriptions

Not every job description is accessible via URL. LinkedIn blocks scraping, some ATS systems require login, and some company career pages render nothing useful. job-hunter supports three input methods:

**1. URL — paste directly**
Works for most public job boards: Greenhouse, Lever, Ashby, and most company career pages. Paste the URL directly into Claude Code or use `/scan`.
```
/evaluate https://boards.greenhouse.io/company/jobs/12345
```

**2. jds/ folder — for blocked pages**
For LinkedIn, OpenAI, and any role where the URL does not load: open the job posting, select all the text, copy it, and save it as a `.txt` file in the `jds/` folder.
```
jds/openai_researcher.txt
```
Then run:
```
/evaluate jds/openai_researcher.txt
```
To get the text from a LinkedIn posting: open the job, use Ctrl+A / Cmd+A to select all, paste into any text editor, and save.

**3. Google Sheets (Sheet 3) — batch queue**
Paste job URLs into the "Job Postings" tab of your tracker, then process them in a batch:
```
/scan --from-sheet
```
Good for clearing a backlog of saved roles.

**LinkedIn CSV import**

LinkedIn lets you export your saved jobs: go to **Settings → Data Privacy → Get a copy of your data**, select Saved Jobs, and download. Then:
```bash
uv run scripts/linkedin_import.py ~/Downloads/SavedJobs.csv
```
This imports your entire backlog into the pipeline at once, ready to evaluate.

---

## Commands

| Command | What it does |
|---|---|
| `/onboard` | First-time setup: build your profile, define target roles, set salary floor |
| `/targets` | Build your company target list — generates `config/targets.yml` |
| `/scan` | Search target company portals for new roles matching your archetypes |
| `/evaluate` | Run a 5-point recruiter-grade evaluation on any job description |
| `/apply` | Generate application Q&A answers, validate, and sync to Google Sheets |
| `/cover` | Write a cover letter for Tier 1 roles — run after `/apply` |
| `/research` | Company brief: recent news, product, culture, and conversation hooks |
| `/interview` | Interview prep by stage: questions, STAR stories, mock Q&A |
| `/pipeline` | View your current job pipeline and statuses |
| `/track` | Sync pipeline data to Google Sheets and update application statuses |

---

## Honesty guardrails

job-hunter is designed to never suggest skills or experience you do not have. Every CV amendment must be honest and defensible in an interview — the rule is: if you would hesitate when asked about it, it does not go in. When a keyword from a job description cannot be honestly inserted into your CV, the system flags the gap explicitly rather than forcing a fit. This is not a limitation. It is the point. A CV that gets you an interview you cannot survive is worse than no interview at all.

---

## A system that learns

job-hunter improves with use. The profile built during onboarding is a living document — sensitive role framing, tier definitions, permitted title variants, target companies, and application Q&A answers all accumulate as you work through your pipeline. The more applications you run through it, the more precisely it knows how to position you for the next one. By the tenth application, the context it holds is something no off-the-shelf tool can replicate.

---

## Project structure

```
job-hunter/
├── CLAUDE.md              # System instructions loaded by Claude Code
├── AGENTS.md              # Full agent behaviour rules and constraints
├── cv.md                  # Your CV in Markdown (gitignored)
├── config/
│   ├── question_bank.json # Standard application questions + tier rules
│   └── targets.yml        # Your company target list (gitignored)
├── modes/                 # One file per command — the agent's instructions
│   ├── onboard.md
│   ├── evaluate.md
│   ├── apply.md
│   ├── scan.md
│   ├── track.md
│   ├── export.md
│   ├── targets.md
│   ├── coverletter.md
│   ├── research.md
│   └── interview.md
├── scripts/
│   ├── healthcheck.py     # Environment health check — run before anything else
│   ├── sheets.py          # Google Sheets sync
│   ├── cv_export.py       # CV to PDF export
│   └── linkedin_import.py # LinkedIn saved jobs CSV import
├── pipeline/              # Your evaluated roles and reports (gitignored)
├── profile/               # Your user profile JSON (gitignored)
├── submitted/             # Submitted CV versions (gitignored)
├── tailored/              # Tailored CV drafts (gitignored)
└── jds/                   # Job description text files (gitignored)
```

---

## Disclaimer

job-hunter is a local, open-source tool. Your CV and personal data never leave your machine — they are sent directly to Anthropic's API when you run Claude Code, and governed by [Anthropic's privacy policy](https://www.anthropic.com/privacy). The system is designed to never auto-submit applications — you always review and confirm before anything is sent. AI-generated content should always be reviewed for accuracy before submitting to an employer.

---

## About

I built this during an active job search because I was frustrated with how manual and imprecise the process was — every application felt like starting from scratch. I am a data scientist with a background in fintech, crypto markets, and AI systems, and I built this the same way I approach any problem: by making it a system. The full case study on how I built it, what worked, and what I would do differently is on [Medium](https://anastasiaulianova.medium.com/).

If you use job-hunter and it helps you land something — I want to hear about it. Open an issue, tag me, or just send a note. That kind of feedback is what keeps a project like this worth maintaining.

**Good luck.**

---

*Got hired using job-hunter? [Share your story](https://github.com/anaulianova/job-hunter/issues/new?title=Got+hired!&labels=success-story) — it helps others find the project and helps me know what's working.*
