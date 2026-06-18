# job-hunter

An intelligent, agentic job search system built on Claude Code.
Conversational onboarding → job discovery → recruiter-grade evaluation → CV tailoring → application tracking.

> Built by Anastasia Ulianova. Open source. [Case study →](https://anastasiaulianova.medium.com/)

---

## Quick Start

```
/onboard       → First time setup: build your profile and define target roles
/targets       → Build your company target list (writes config/targets.yml)
/scan          → Search for new jobs (company portals + URL batch input)
/evaluate      → Run 5-point evaluation on a JD (paste text or URL or jds/file.txt)
/apply         → Generate application Q&A answers + confirm CV + update tracker
/cover         → Write a cover letter (Tier 1 only — run after /apply)
/research      → Company brief: news, product, culture, conversation hooks
/interview     → Interview prep: questions, STAR stories, mock Q&A
/pipeline      → View current job pipeline and statuses
/track         → Update Google Sheets tracker
```

Or just paste a job URL or JD directly — job-hunter auto-detects and routes it.

---

## How It Works

```
User onboards (CV + conversation)
         │
         ▼
  Profile + role archetypes saved
         │
    ┌────┴─────┐
    ▼          ▼
  /scan     /evaluate (URL, paste, or jds/file.txt)
    │          │
    └────┬─────┘
         ▼
   5-Point Evaluation
   (fit score, ATS audit, CV amendments, red flags, About Me)
         │
         ▼
   User validates CV edits
         │
         ▼
   /apply → Q&A answers generated + CV confirmed
   (salary, why this company, note to HM, etc.)
         │
         ▼
   Google Sheets tracker + Q&A sheet updated
```

---

## Agent Instructions

See [AGENTS.md](./AGENTS.md) for full agent behaviour, rules, and constraints.

## Your Profile

Stored in [profile/user_profile.json](./profile/user_profile.json) after onboarding.
Edit directly or re-run `/onboard` to update.

## Imports from AGENTS.md

@AGENTS.md
