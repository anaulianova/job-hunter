# Mode: /onboard

**Purpose:** Build a complete user profile through structured conversation. Run once on setup, or re-run to update. Saves to `profile/user_profile.json`.

---

## Pre-check

Before starting, check if `profile/user_profile.json` already exists.
- If yes: "I found an existing profile for [name]. Do you want to (1) update it or (2) start fresh?"
- If no: proceed with full onboarding below.

---

## Onboarding Flow

Run the conversation in exactly this sequence. Do not ask all questions at once — have a natural back-and-forth. Wait for the user's answer before moving to the next block.

---

### Block 1 — CV Ingestion

Say: "Let's start. Please paste your CV text, or share the file path if it's already in the project as cv.md."

- If pasted: extract all experience, education, skills, and save to `cv.md`
- If `cv.md` already exists: "I can see your CV is already loaded. I'll use that as the base."

Confirm: "Got it. I've read your CV. Let me ask you a few questions to build your full profile — things that don't appear on a CV but matter enormously to a recruiter."

---

### Block 2 — Career Context (5–6 questions max)

Ask these in a natural conversational way, not as a numbered list:

1. "What kind of work do you actually want to be doing day-to-day? Not the job title — the actual work."
2. "What industries or domains do you have real expertise in — the ones where you could hold your own in a room of specialists?"
3. "What's the one thing from your background you're most proud of that you feel doesn't come across clearly on your CV?"
4. "Is there anything in your history you'd consider sensitive or complicated — a short tenure, a pivot, a gap — that we should think carefully about how to frame? For any such role, what's the honest reason, and how would you want it presented?"
5. "Is there a word or description people sometimes use for your background that you feel is inaccurate or that you'd prefer we never use?"
6. "What would make you say no to an offer, even a well-paid one?"

After the user answers, synthesise: "Here's what I'm hearing: [2–3 sentence summary]. Does that feel right?"

---

### Block 3 — Search Parameters

Ask as a single block (these are factual, not reflective):

"Now the practical parameters. I just need your answers to these:
- What locations are you targeting? (and do you need visa sponsorship for any of them?)
- What's your salary floor — the number below which you wouldn't take a role?
- Are you open to remote roles?
- Any company types or industries you want to avoid?"

---

### Block 4 — Profile Synthesis (Agent-Driven)

After collecting all information, the agent produces:

**A. Complete profile narrative** (3–4 sentences summarising who the user is as a candidate)

**B. Domain expertise list** — the 3–6 domains the user has genuine expertise in, to calibrate the agent's evaluation lens.

**C. Three role archetypes** based on background fit. For each:
- Archetype name (e.g. "Senior Data Scientist — Fintech/Crypto")
- Why the user is a strong fit
- Typical companies and titles to target
- One honest gap to be aware of

**D. Tier definitions** for this user's search:
- Tier 1: [specific criteria based on their archetypes]
- Tier 2: [criteria]
- Tier 3: [criteria]

Present this and say: "This is how I see your profile and the roles worth pursuing. Do these feel right? Is there a category of role you're interested in that I haven't included?"

---

### Block 5 — Validation and Save

After the user confirms or refines:

1. Save to `profile/user_profile.json` (see schema below)
2. Confirm: "Profile saved. You're ready to search. Run `/scan` to discover new roles, or paste a job URL to evaluate one now."

---

## Output Schema: `profile/user_profile.json`

```json
{
  "name": "",
  "email": "",
  "phone": "",
  "location_current": "",
  "visa_status": {
    "US": "no_sponsorship_required",
    "UK": "no_sponsorship_required"
  },
  "languages": [],
  "career_narrative": "",
  "what_i_want_to_do": "",
  "proudest_achievement": "",
  "domain_expertise": [],
  "forbidden_descriptions": [],
  "sensitive_items": [],
  "dealbreakers": [],
  "search_parameters": {
    "primary_locations": [],
    "secondary_locations": [],
    "open_to_remote": true,
    "salary_floor_usd": 0,
    "salary_floor_gbp": 0,
    "avoid_industries": [],
    "avoid_role_types": []
  },
  "role_archetypes": [
    {
      "name": "",
      "fit_rationale": "",
      "target_companies": [],
      "target_titles": [],
      "honest_gap": "",
      "notes": ""
    }
  ],
  "tier_definitions": {
    "tier_1": "",
    "tier_2": "",
    "tier_3": ""
  },
  "cv_path": "cv.md",
  "permitted_title_variants": [
    {
      "company": "",
      "variants": [],
      "notes": ""
    }
  ],
  "sensitive_roles": [
    {
      "company": "",
      "title": "",
      "dates": "",
      "duration": "",
      "include_rule": "",
      "approved_framing": "",
      "do_not_frame_as": ""
    }
  ],
  "onboarded_at": "",
  "last_updated": ""
}
```

**Note on `permitted_title_variants`:** Only add entries here for roles where the user has explicitly confirmed that a title switch is accurate and defensible — e.g. a role that genuinely spanned two functions. Never assume variants without asking.

**Note on `sensitive_roles`:** For any short tenure or difficult-to-explain role, capture the honest context and an approved framing the user is comfortable defending. The agent will only use `approved_framing` — never improvise.
