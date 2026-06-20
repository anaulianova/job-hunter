# CV Export Mode

Handles CV tailoring and PDF export. Run after completing a 5-point evaluation.

---

## Export Commands

**CV:**
```bash
uv run scripts/cv_export.py --company elliptic-da --date jun18
# Looks for: app/cv/record/cv_elliptic-da_jun18.md → falls back to cv.md
# Outputs:   app/cv/pdf/elliptic-da_jun18.pdf

uv run scripts/cv_export.py --input path/to/file.md --company stripe --date jun17
# Explicit source file
```

**Cover letter:**
```bash
uv run scripts/coverletter_export.py --company gsr --date jun20
# Reads:   app/coverletter/record/cover_gsr_jun20.md (body only)
# Injects: contact block from profile/user_profile.json
# Outputs: app/coverletter/pdf/cover_gsr_jun20.pdf
```

Date defaults to today if omitted. The script warns `⚠️ PDF is N pages` if content overflows — the CV must always be 1 page.

---

## CV Tailoring Workflow

1. Run `/evaluate` on a JD — this produces a report in `pipeline/reports/`
2. Ask Claude to tailor the CV: *"Tailor my CV for [role]"*
3. Claude applies Point 3 amendments + Point 4 (sensitive role decisions) + Point 5 (About Me) + subtitle keyword selection
4. Claude writes the tailored version to `app/cv/record/cv_{company}_{date}.md`
5. You review and approve
6. Run the export command above
7. PDF lands in `app/cv/pdf/{company}_{date}.pdf`

---

## File Structure

```
app/cv/record/
  cv_{company}_{date}.md          ← tailored CV source (not committed to git)

app/cv/pdf/
  {company}_{date}.pdf            ← CV submission copy and permanent record

app/coverletter/record/
  cover_{company}_{date}.md       ← cover letter body only (not committed to git)

app/coverletter/pdf/
  cover_{company}_{date}.pdf      ← cover letter with injected contact block
```

The markdown file is the source of truth. Re-export any time to regenerate the PDF.

---

## PDF Design Spec

Implemented in `scripts/cv_export.py` → `CV_CSS`. Designed for A4, 1 page.

| Element | Size | Style |
|---|---|---|
| Page margins | 1.4cm top, 1.3cm sides | A4 |
| Body | 9pt Helvetica | line-height 1.35 |
| Name (h1) | 20pt bold | |
| Subtitle | 9pt bold | #555 |
| Contact line | 8.5pt | #444, links underlined |
| Section headers (h2) | 10pt bold uppercase | letter-spacing 1pt, ruled underline |
| Company name (h3) | 9.5pt bold | |
| Role/date line | 8.5pt | #555 |
| Bullets | 9pt | line-height 1.32 |

**1-page rule is non-negotiable.** If the export warns of overflow, shorten the content before submitting — do not adjust CSS to squeeze more in.

---

## Markdown CV Format

`cv.md` must follow this exact structure for the PDF renderer to apply styles correctly:

```markdown
# Full Name
**Tagline • Tagline • Tagline**

Phone | email | [LinkedIn](url) | [GitHub](url) | [Medium](url)

---

## About Me

One paragraph, max 3 sentences.

---

## Experience

### Company Name
**Job Title** | Start – End | Location
- Bullet (max 2 lines)
- Bullet (max 2 lines)

### Company Name (second role, same company)
**First Title** | Dates | Location
- Bullet

**Second Title** | Dates
- Bullet

---

## Education

**Institution** | Qualification | Dates

---

## Skills

**Category:** items, items, items
```

**Critical formatting rules:**
- Blank line required between role/date line and first bullet (the renderer needs it to parse bullets as a list)
- Each bullet max 2 lines in the rendered PDF
- Pipe `|` separators on role lines trigger the grey italic styling
- Links in the contact line are underlined in the PDF

---

## Sensitive Role Rules

Sensitive roles are defined in `profile/user_profile.json` → `sensitive_roles`. The include/exclude decision is made at Point 4 of the evaluation and recorded in the evaluation report.

When **INCLUDE**: insert the role using only the `approved_framing` from the profile — never improvise alternative framing.

When **EXCLUDE**: omit the role section entirely. If removing it creates a visible timeline gap, note it so the user can decide whether to address it.

**Format for any included sensitive role:**
```markdown
### [Company]
**[Title]** | [Dates] | [Location]
- [approved_framing line 1]
- [approved_framing line 2, if defined]
```
