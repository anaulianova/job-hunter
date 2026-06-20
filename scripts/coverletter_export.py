"""
coverletter_export.py
Assembles a cover letter from a markdown body file and exports it to PDF.

The markdown file contains only the letter body — no personal details.
Personal details (name, address, phone, email) are injected at export time
from profile/user_profile.json so they are never committed to git.

Usage:
    uv run scripts/coverletter_export.py --company gsr --date jun20
        → reads app/coverletter/record/cover_gsr_jun20.md
        → injects contact block from profile/user_profile.json
        → writes app/coverletter/pdf/cover_gsr_jun20.pdf

    uv run scripts/coverletter_export.py --company gsr
        → date defaults to today
"""

import argparse
import io
import json
import sys
from datetime import date
from pathlib import Path

try:
    import markdown
    from xhtml2pdf import pisa
except ImportError:
    print("❌ Missing dependencies. Run:")
    print("   uv pip install markdown xhtml2pdf")
    sys.exit(1)

ROOT           = Path(__file__).parent.parent
RECORD_DIR     = ROOT / "app" / "coverletter" / "record"
PDF_DIR        = ROOT / "app" / "coverletter" / "pdf"
PROFILE_PATH   = ROOT / "profile" / "user_profile.json"

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

COVER_CSS = """
@page {
    size: A4;
    margin: 2.4cm 2.5cm 2cm 2.5cm;
}

body {
    font-family: Helvetica, Arial, sans-serif;
    font-size: 10.5pt;
    color: #111111;
    line-height: 1.55;
}

.contact-block {
    font-size: 10.5pt;
    margin-bottom: 0;
    line-height: 1.55;
}

.date-line {
    text-align: right;
    font-size: 10.5pt;
    margin: 18pt 0 16pt 0;
}

p {
    margin: 0 0 11pt 0;
}

.closing {
    margin-top: 18pt;
}
"""


def _format_date(date_str: str) -> str:
    """Convert 'jun20' → 'Saturday 20 June, 2026'."""
    month_abbr = date_str[:3].lower()
    day = int(date_str[3:])
    month_num = MONTH_MAP.get(month_abbr)
    if not month_num:
        raise ValueError(f"Unrecognised month abbreviation: {month_abbr!r}")
    year = date.today().year
    d = date(year, month_num, day)
    return d.strftime("%A %-d %B, %Y")


def _load_profile() -> dict:
    if not PROFILE_PATH.exists():
        print(f"❌ Profile not found: {PROFILE_PATH}")
        sys.exit(1)
    with open(PROFILE_PATH) as f:
        return json.load(f)


def _build_contact_html(profile: dict) -> str:
    name    = profile.get("name", "")
    address = profile.get("address", [])
    phone   = profile.get("phone", "")
    email   = profile.get("email", "")
    lines   = [name] + address + [phone, email]
    return "<br>".join(line for line in lines if line)


def _build_html(contact_html: str, date_str: str, body_md: str) -> str:
    md   = markdown.Markdown()
    body = md.convert(body_md)
    formatted_date = _format_date(date_str)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>{COVER_CSS}</style>
</head>
<body>
<div class="contact-block">{contact_html}</div>
<div class="date-line">{formatted_date}</div>
{body}
</body>
</html>"""


def export_pdf(md_path: Path, output_path: Path, date_str: str) -> None:
    profile      = _load_profile()
    contact_html = _build_contact_html(profile)
    body_md      = md_path.read_text(encoding="utf-8")
    html         = _build_html(contact_html, date_str, body_md)

    buf = io.BytesIO()
    result = pisa.CreatePDF(html, dest=buf, encoding="utf-8")
    if result.err:
        raise RuntimeError(f"PDF generation error: {result.err}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(buf.getvalue())


def main():
    parser = argparse.ArgumentParser(description="Export cover letter markdown to PDF")
    parser.add_argument("--company", required=True,
                        help="Company slug, e.g. 'gsr'")
    parser.add_argument("--date",
                        help="Date string, e.g. 'jun20' (defaults to today)")
    parser.add_argument("--input",
                        help="Explicit markdown source")
    args = parser.parse_args()

    date_str = args.date or date.today().strftime("%b%-d").lower()
    company  = args.company.lower().replace(" ", "-")
    stem     = f"cover_{company}_{date_str}"

    if args.input:
        md_path = Path(args.input).resolve()
    else:
        md_path = RECORD_DIR / f"{stem}.md"

    if not md_path.exists():
        print(f"❌ Source not found: {md_path}")
        sys.exit(1)

    output_path = PDF_DIR / f"{stem}.pdf"
    export_pdf(md_path, output_path, date_str)

    print(f"✅  {output_path.name}")
    print(f"   Source : {md_path.relative_to(ROOT)}")
    print(f"   Size   : {output_path.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
