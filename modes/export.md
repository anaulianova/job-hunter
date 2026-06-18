# CV Export Mode

Handles CV tailoring and PDF export. Run after completing a 5-point evaluation.

---

## Export Command

```bash
uv run scripts/cv_export.py --company elliptic-da --date jun18
# Looks for: submitted/cv_elliptic-da_jun18.md → falls back to cv.md
# Outputs:   submitted/elliptic-da_jun18.pdf

uv run scripts/cv_export.py --input path/to/file.md --company stripe --date jun17
# Explicit source file
```

Date defaults to today if omitted. The script warns `⚠️ PDF is N pages` if content overflows — the CV must always be 1 page.

---

## Tailoring Workflow

1. Run `/evaluate` on a JD — this produces a report in `pipeline/reports/`
2. Ask Claude to tailor the CV: *"Tailor my CV for [role]"*
3. Claude applies Point 3 amendments + Point 4 (Airwallex) + Point 5 (About Me)
4. Claude writes the tailored version to `submitted/cv_{company}_{date}.md`
5. You review and approve
6. Run the export command above
7. PDF lands in `submitted/{company}_{date}.pdf`

---

## File Structure

```
tailored/
  cv_{company}_{date}.md   ← tailored CV source (not committed to git)

submitted/
  {company}_{date}.pdf     ← submission copy and permanent record
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

## Airwallex Inclusion Rules

Controlled per role at Point 4 of the evaluation. When **INCLUDE**:

```markdown
### Airwallex / t0
**Manager, Strategy & Operations** | Mar 2026 – May 2026 | San Francisco
- Assessed integration opportunities for AI-powered workflows across daily operations of an AI-native accounting platform
- Contributed to GTM positioning and compliance framework evaluation (SOC II)
```

When **EXCLUDE**: remove the entire Airwallex section.

Include when: AI workflow framing is relevant, B2B SaaS context adds value, cross-functional ops experience is valued.
Exclude when: pure DS/ML role, London institutional role, short tenure creates noise.
