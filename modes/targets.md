# Mode: /targets

**Purpose:** Build a personalised `config/targets.yml` — the list of companies to scan for new roles. Runs during onboarding or standalone to update the list as your search evolves.
**Input:** `/targets` — requires `profile/user_profile.json` to exist. If it doesn't, route to `/onboard` first.
**Output:** Writes `config/targets.yml` (gitignored — never committed).

---

## Pre-flight

1. Load `profile/user_profile.json` — if missing, stop and route to `/onboard`
2. Extract:
   - `role_archetypes` → company sectors and target titles
   - `search_parameters.primary_locations` + `secondary_locations` → location filter
   - `dealbreakers` → candidate title exclusions

---

## Step 1 — Derive config blocks

### exclude_title_keywords

Build from:
- `profile.dealbreakers` — any that are role-type exclusions (e.g. "Operations roles" → "Operations")
- Standard filters always included: `Staff`, `Principal`, `Lead`, `Director`, `Head of`, `VP`, `Senior Manager`, `Group Product Manager`, `Intern`, `PhD`, `Recruiter`

Do not duplicate. Present the list for user confirmation before writing.

### role_keywords

Extract `target_titles` from each archetype in `profile.role_archetypes`. Deduplicate. Convert to lowercase keyword form (e.g. "Data Scientist" → "data scientist"). Also extract any strong keywords from archetype names.

### locations

Load from `profile.search_parameters`:
- `primary_locations`
- `secondary_locations` (extract city names only, strip any parenthetical notes)
- Always include `Remote` if `open_to_remote` is true

---

## Step 2 — Company research

For each archetype in `profile.role_archetypes`, use `target_companies` as the seed list.

For each company:
1. Determine ATS type — use WebSearch: `"{company name}" site:greenhouse.io OR lever.co OR ashby.com jobs`
   - Greenhouse: `boards.greenhouse.io/{slug}` or `boards-api.greenhouse.io/v1/boards/{slug}/jobs`
   - Lever: `jobs.lever.co/{slug}`
   - Ashby: `jobs.ashby.com/{slug}`
   - If none found: mark as `manual`
2. Set `priority`:
   - `tier1` — matches a Tier 1 archetype or has a note flagging strong fit
   - `tier2` — matches a Tier 2 archetype
   - `tier3` — speculative addition, user added manually
3. Add a `note` for any context worth preserving: previous employer, scraper blocks, strong fit signal, specific team to target

Group companies by sector in the YAML (e.g. `# ── AI Labs`, `# ── Fintech / Crypto`). Sector headings are for human readability only — they do not affect scanning.

---

## Step 3 — Present and confirm

Present a summary:

```
TARGETS DRAFT
─────────────────────────────────────────
Role keywords:   [list]
Locations:       [list]
Companies:       [N] proposed

BY ARCHETYPE:
  [Archetype 1]: [company names]
  [Archetype 2]: [company names]
  [Archetype 3]: [company names]

Any companies to add or remove before I write the file?
```

Wait for user confirmation. Accept additions — for each new company ask:
- "Do you want me to look up the ATS type, or mark it as manual?"

Accept removals without comment.

---

## Step 4 — Write config/targets.yml

After confirmation, write the full YAML file following this structure exactly:

```yaml
# job-hunter target companies
# Scanned for new roles matching your archetypes
# ATS types: greenhouse | lever | ashby | manual
#   manual = private board or unsupported ATS — check career_url directly

exclude_title_keywords:
  - [keyword]

role_keywords:
  - [keyword]

locations:
  - [location]

companies:

  # ── [Sector] ──────────────────────────────────────────────────────────────

  - name: [Company]
    ats: [greenhouse|lever|ashby|manual]
    api_url: [greenhouse or lever API URL, if applicable]   # omit if manual
    lever_slug: [slug]                                       # lever only
    career_url: [careers page URL]
    priority: [tier1|tier2|tier3]
    note: [optional — scraper notes, fit signal, previous employer flag]
```

Rules:
- `api_url` only for Greenhouse and Lever — omit the field entirely for Ashby and manual
- `lever_slug` only for Lever
- `note` only when there is genuinely useful context — do not add a note for every company
- Preserve sector grouping comments for readability

Confirm: "targets.yml written with [N] companies across [N] archetypes. Run `/scan` to start discovering roles."

---

## Updating targets

Run `/targets` again at any time to:
- Add new companies discovered during `/scan` or research
- Remove companies that turned out to be irrelevant
- Change a priority level
- Update an ATS type that changed

The existing `config/targets.yml` is read first, then the user is asked what to change rather than rebuilding from scratch.

---

## ATS type quick reference

| ATS | API pattern | Notes |
|---|---|---|
| Greenhouse | `boards-api.greenhouse.io/v1/boards/{slug}/jobs` | Most common. Slug is usually company name lowercase. |
| Lever | `jobs.lever.co/{slug}` | No official API — scan the public job board page. |
| Ashby | `jobs.ashby.com/{slug}` | Growing adoption in startups. |
| Manual | — | Company uses a proprietary ATS, LinkedIn only, or blocks scrapers. Check `career_url` directly. |
