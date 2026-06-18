"""
job-hunter: linkedin_import.py
Imports LinkedIn Saved Jobs from a CSV export into the pipeline.

How to get your LinkedIn export:
1. LinkedIn → Settings → Data Privacy → Get a copy of your data
2. Select "Job applications" and/or "Saved jobs"
3. Download and unzip
4. Run: python scripts/linkedin_import.py ~/Downloads/SavedJobs.csv

LinkedIn CSV columns vary by export type. This script handles both:
- Standard saved jobs: Job Title, Company Name, Location, Saved Date, Job URL
- Application history: Job Title, Company, Applied Date, Job URL
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
PIPELINE_FILE = ROOT / "pipeline" / "pipeline.json"


def load_pipeline():
    if PIPELINE_FILE.exists():
        with open(PIPELINE_FILE) as f:
            return json.load(f)
    return []


def save_pipeline(pipeline):
    PIPELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PIPELINE_FILE, "w") as f:
        json.dump(pipeline, f, indent=2)


def normalise_row(row):
    """Handle LinkedIn's inconsistent CSV column names."""
    keys = {k.strip().lower(): v.strip() for k, v in row.items()}

    title = (
        keys.get("job title") or
        keys.get("title") or
        keys.get("position") or ""
    )
    company = (
        keys.get("company name") or
        keys.get("company") or ""
    )
    location = (
        keys.get("location") or
        keys.get("job location") or ""
    )
    url = (
        keys.get("job url") or
        keys.get("url") or
        keys.get("link") or ""
    )
    saved_date = (
        keys.get("saved date") or
        keys.get("applied date") or
        keys.get("date") or ""
    )

    return {
        "title": title,
        "company": company,
        "location": location,
        "url": url,
        "saved_date": saved_date
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/linkedin_import.py <path_to_csv>")
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"❌ File not found: {csv_path}")
        sys.exit(1)

    pipeline = load_pipeline()
    existing_urls = {entry.get("url", "") for entry in pipeline}

    imported = 0
    skipped = 0
    errors = 0

    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"\n📥 LinkedIn Import — {csv_path.name}")
    print(f"   Rows in file: {len(rows)}\n")

    new_entries = []
    for row in rows:
        try:
            normalised = normalise_row(row)

            if not normalised["title"] and not normalised["company"]:
                errors += 1
                continue

            if normalised["url"] and normalised["url"] in existing_urls:
                skipped += 1
                continue

            entry = {
                "company": normalised["company"],
                "job_title": normalised["title"],
                "tier": None,
                "match_score": None,
                "status": "discovered",
                "url": normalised["url"],
                "location": normalised["location"],
                "evaluated_date": None,
                "application_date": None,
                "cv_version": None,
                "notes": f"Imported from LinkedIn CSV on {date.today()}. Originally saved: {normalised['saved_date']}"
            }
            new_entries.append(entry)
            existing_urls.add(normalised["url"])
            imported += 1

        except Exception as e:
            print(f"  ⚠ Error on row: {row} → {e}")
            errors += 1

    if new_entries:
        pipeline.extend(new_entries)
        save_pipeline(pipeline)

    print(f"✅ Import complete:")
    print(f"   {imported} new roles added to pipeline")
    print(f"   {skipped} already in pipeline (skipped)")
    print(f"   {errors} rows with errors or missing data")

    if new_entries:
        print(f"\nNew roles:")
        for i, e in enumerate(new_entries, 1):
            print(f"  [{i}] {e['company']} — {e['job_title']} — {e['location']}")

    print(f"\nNext step: run /evaluate to assess these roles, or open Claude Code and paste a job URL.")


if __name__ == "__main__":
    main()
