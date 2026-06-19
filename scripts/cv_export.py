"""
cv_export.py
Converts a tailored CV markdown file to a professionally formatted PDF.

Usage:
    uv run scripts/cv_export.py --company elliptic --date jun18
        → looks for cv/record/cv_elliptic_jun18.md, falls back to cv.md
        → writes cv/pdf/elliptic_jun18.pdf

    uv run scripts/cv_export.py --company elliptic
        → date defaults to today

    uv run scripts/cv_export.py --input cv.md --company test --date jun18
        → explicit source file

Tailoring workflow:
    1. Claude reads cv.md + pipeline/reports/{role}.md and applies amendments
    2. Claude writes tailored version to cv/record/cv_{company}_{date}.md
    3. User validates
    4. Run this script to export PDF
"""

import argparse
import io
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import markdown
    from xhtml2pdf import pisa
except ImportError:
    print("❌ Missing dependencies. Run:")
    print("   uv pip install markdown xhtml2pdf")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
SUBMITTED_DIR = ROOT / "cv" / "pdf"
TAILORED_DIR  = ROOT / "cv" / "record"

CV_CSS = """
@page {
    size: A4;
    margin: 1.4cm 1.3cm 1.3cm 1.3cm;
}

body {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 9pt;
    color: #111111;
    line-height: 1.35;
}

/* ── Name ── */
h1 {
    font-size: 20pt;
    font-weight: bold;
    margin: 0 0 2pt 0;
    letter-spacing: 0.2pt;
    color: #000;
}

/* ── Subtitle (Data Scientist • Product...) ── */
.subtitle {
    font-size: 9pt;
    color: #555555;
    margin: 0 0 2pt 0;
    font-weight: bold;
}

/* ── Contact line ── */
.contact {
    font-size: 8.5pt;
    color: #444444;
    margin: 0;
}

/* ── Divider ── */
hr {
    border: none;
    border-top: 0.4pt solid #bbbbbb;
    margin: 5pt 0 4pt 0;
}

/* ── Section headers (EXPERIENCE, EDUCATION...) ── */
h2 {
    font-size: 10pt;
    font-weight: bold;
    text-transform: uppercase;
    letter-spacing: 1pt;
    color: #222222;
    border-bottom: 0.4pt solid #999999;
    padding-bottom: 1.5pt;
    margin: 9pt 0 3pt 0;
}

/* ── Company / Institution name ── */
h3 {
    font-size: 9.5pt;
    font-weight: bold;
    margin: 6pt 0 0 0;
    color: #000;
}

/* ── Title | Date | Location line ── */
.role-line {
    font-size: 8.5pt;
    color: #555555;
    margin: 0 0 1pt 0;
}

/* ── Bullet points ── */
ul {
    margin: 0 0 2pt 0;
    padding-left: 12pt;
}

li {
    font-size: 9pt;
    margin-bottom: 0.8pt;
    line-height: 1.32;
}

/* ── Body paragraphs ── */
p {
    margin: 1.5pt 0;
    font-size: 9pt;
}

/* ── Links ── */
a {
    color: #111111;
    text-decoration: underline;
}

/* ── Prevent orphaned section headers ── */
h2, h3 {
    page-break-after: avoid;
}
"""


def _fix_list_spacing(md_content: str) -> str:
    """Insert blank line before list items that immediately follow a non-list line.

    The Python markdown library requires a blank line before a list when it
    appears after a paragraph. cv.md uses tight GFM-style formatting that
    GitHub renders fine but Python markdown doesn't.
    """
    lines = md_content.split("\n")
    out = []
    for i, line in enumerate(lines):
        if line.startswith("- ") and i > 0:
            prev = lines[i - 1].strip()
            if prev and not prev.startswith("- "):
                out.append("")
        out.append(line)
    return "\n".join(out)


def _preprocess_html(html: str) -> str:
    """Inject CSS classes into structural elements that markdown can't tag directly."""

    # Subtitle: first <p> after <h1> that contains only a <strong> block
    html = re.sub(
        r'(</h1>\s*\n?)(<p>)(<strong>[^<]+</strong>\s*</p>)',
        r'\1<p class="subtitle">\3',
        html,
    )
    # Contact line: paragraph containing an email address (robust against inline links)
    html = re.sub(
        r"<p>((?:(?!</p>|<p>).)*[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+(?:(?!</p>|<p>).)*)</p>",
        r'<p class="contact">\1</p>',
        html,
        flags=re.DOTALL,
    )
    # Role/date line: <p> immediately following </h3> that starts with <strong>
    html = re.sub(
        r'(</h3>\s*\n?)(<p>)(<strong>)',
        r'\1<p class="role-line">\3',
        html,
    )
    # Second (or later) role at same company: <p><strong> following </ul>
    html = re.sub(
        r'(</ul>\s*\n?)(<p>)(<strong>)',
        r'\1<p class="role-line">\3',
        html,
    )
    return html


def _md_to_html(md_content: str) -> str:
    md_content = _fix_list_spacing(md_content)
    md = markdown.Markdown(extensions=["sane_lists"])
    body = md.convert(md_content)
    body = _preprocess_html(body)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>{CV_CSS}</style>
</head>
<body>
{body}
</body>
</html>"""


def _page_count(pdf_bytes: bytes) -> int:
    """Count pages via raw PDF token — no extra dependencies needed."""
    import re as _re
    return len(_re.findall(b"/Type /Page[^s]", pdf_bytes))


def export_pdf(md_path: Path, output_path: Path) -> None:
    md_content = md_path.read_text(encoding="utf-8")
    html = _md_to_html(md_content)
    buf = io.BytesIO()
    result = pisa.CreatePDF(html, dest=buf, encoding="utf-8")
    if result.err:
        raise RuntimeError(f"PDF generation error: {result.err}")
    pdf_bytes = buf.getvalue()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(pdf_bytes)
    pages = _page_count(pdf_bytes)
    if pages > 1:
        print(f"⚠️  PDF is {pages} pages — CV must be 1 page. Shorten the content before submitting.")
    return pages


def main():
    parser = argparse.ArgumentParser(description="Export tailored CV markdown to PDF")
    parser.add_argument("--company", required=True,
                        help="Company slug, e.g. 'elliptic' — used for output filename")
    parser.add_argument("--date",
                        help="Date string, e.g. 'jun18' (defaults to today)")
    parser.add_argument("--input",
                        help="Explicit markdown source (default: cv/pdf/cv_{company}_{date}.md → cv.md)")
    args = parser.parse_args()

    date_str = args.date or datetime.today().strftime("%b%-d").lower()
    company  = args.company.lower().replace(" ", "-")
    stem     = f"{company}_{date_str}"

    # Resolve source markdown
    if args.input:
        md_path = Path(args.input).resolve()
    else:
        tailored = TAILORED_DIR / f"cv_{stem}.md"
        md_path  = tailored if tailored.exists() else ROOT / "cv.md"

    if not md_path.exists():
        print(f"❌ Source not found: {md_path}")
        sys.exit(1)

    output_path = SUBMITTED_DIR / f"{stem}.pdf"
    pages = export_pdf(md_path, output_path)

    page_str = f"{pages}p" if pages else "?"
    print(f"✅  {output_path.name}  [{page_str}]")
    print(f"   Source : {md_path.relative_to(ROOT)}")
    print(f"   Size   : {output_path.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
