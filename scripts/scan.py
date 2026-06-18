"""
job-hunter: scan.py
Scrapes company career portals using ATS APIs (Greenhouse, Ashby, Lever)
and returns new roles matching the user's profile keywords and locations.

Usage:
    python scripts/scan.py                    # scan all targets
    python scripts/scan.py --company stripe   # scan one company
    python scripts/scan.py --dry-run          # show matches without saving
"""

import json
import yaml
import requests
import argparse
from datetime import datetime, date
from pathlib import Path
from urllib.parse import urlparse

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
TARGETS_FILE = ROOT / "config" / "targets.yml"
PIPELINE_FILE = ROOT / "pipeline" / "pipeline.json"
SCAN_LOG_FILE = ROOT / "pipeline" / "scan_log.json"

# ── Helpers ─────────────────────────────────────────────────────────────────

def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)

def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return []

def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def existing_urls(pipeline):
    return {entry.get("url", "") for entry in pipeline}

def keyword_match(text, keywords):
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)

def location_match(text, locations):
    text_lower = text.lower()
    return any(loc.lower() in text_lower for loc in locations) or "remote" in text_lower

def seniority_ok(title, exclude_keywords):
    title_lower = title.lower()
    return not any(kw.lower() in title_lower for kw in exclude_keywords)

# ── ATS Scrapers ────────────────────────────────────────────────────────────

def fetch_greenhouse(company):
    """Fetch jobs from Greenhouse public API."""
    api_url = company.get("api_url")
    if not api_url:
        board_token = company["career_url"].rstrip("/").split("/")[-1]
        api_url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"

    try:
        resp = requests.get(api_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        jobs = data.get("jobs", [])
        return [
            {
                "title": j.get("title", ""),
                "location": j.get("location", {}).get("name", ""),
                "url": j.get("absolute_url", ""),
                "company": company["name"],
                "ats": "greenhouse",
                "posted_at": j.get("updated_at", "")[:10] if j.get("updated_at") else ""
            }
            for j in jobs
        ]
    except Exception as e:
        print(f"  ⚠ Greenhouse fetch failed for {company['name']}: {e}")
        return []

def fetch_lever(company):
    """Fetch jobs from Lever public API."""
    # Use explicit lever_slug if provided; never infer from company career URL
    slug = company.get("lever_slug")
    if not slug:
        print(f"  ⚠ No lever_slug set for {company['name']} — add lever_slug to targets.yml")
        return []

    api_url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
    try:
        resp = requests.get(api_url, timeout=10)
        resp.raise_for_status()
        jobs = resp.json()
        return [
            {
                "title": j.get("text", ""),
                "location": j.get("categories", {}).get("location", ""),
                "url": j.get("hostedUrl", ""),
                "company": company["name"],
                "ats": "lever",
                "posted_at": datetime.fromtimestamp(j["createdAt"] / 1000).strftime("%Y-%m-%d") if j.get("createdAt") else ""
            }
            for j in jobs
        ]
    except Exception as e:
        print(f"  ⚠ Lever fetch failed for {company['name']}: {e}")
        return []

def fetch_ashby(company):
    """Fetch jobs from Ashby public API."""
    # Use explicit ashby_slug if provided; never infer from company career URL
    slug = company.get("ashby_slug")
    if not slug:
        print(f"  ⚠ No ashby_slug set for {company['name']} — add ashby_slug to targets.yml")
        return []

    api_url = f"https://jobs.ashbyhq.com/api/non-user-facing/job-board/jobs?organizationHostedJobsPageName={slug}"
    try:
        resp = requests.get(api_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        jobs = data.get("jobs", [])
        return [
            {
                "title": j.get("title", ""),
                "location": j.get("locationName", ""),
                "url": f"https://jobs.ashbyhq.com/{slug}/{j.get('id', '')}",
                "company": company["name"],
                "ats": "ashby",
                "posted_at": j.get("publishedDate", "")[:10] if j.get("publishedDate") else ""
            }
            for j in jobs
        ]
    except Exception as e:
        print(f"  ⚠ Ashby fetch failed for {company['name']}: {e}")
        return []

# ── Main Scan ───────────────────────────────────────────────────────────────

def scan_company(company, keywords, locations, exclude_titles=None):
    ats = company.get("ats", "")
    print(f"  Scanning {company['name']} ({ats})...")

    if ats == "greenhouse":
        jobs = fetch_greenhouse(company)
    elif ats == "lever":
        jobs = fetch_lever(company)
    elif ats == "ashby":
        jobs = fetch_ashby(company)
    elif ats == "manual":
        print(f"  ℹ {company['name']}: manual check required → {company.get('career_url', 'no URL')}")
        return []
    else:
        print(f"  ⚠ No scraper for ATS type '{ats}' — skipping {company['name']}")
        return []

    # Filter by keywords, location, and seniority
    matched = [
        j for j in jobs
        if keyword_match(j["title"], keywords)
        and location_match(j["location"], locations)
        and seniority_ok(j["title"], exclude_titles or [])
    ]

    print(f"  → {len(matched)} matching roles (from {len(jobs)} total listings)")
    return matched

def main():
    parser = argparse.ArgumentParser(description="job-hunter portal scanner")
    parser.add_argument("--company", help="Scan a single company by name")
    parser.add_argument("--dry-run", action="store_true", help="Show results without saving")
    args = parser.parse_args()

    config = load_yaml(TARGETS_FILE)
    pipeline = load_json(PIPELINE_FILE)
    seen_urls = existing_urls(pipeline)

    keywords = config.get("role_keywords", [])
    locations = config.get("locations", [])
    exclude_titles = config.get("exclude_title_keywords", [])
    companies = config.get("companies", [])

    if args.company:
        companies = [c for c in companies if c["name"].lower() == args.company.lower()]
        if not companies:
            print(f"❌ Company '{args.company}' not found in targets.yml")
            return

    print(f"\n🔍 job-hunter scan — {date.today()}")
    print(f"Targets: {len(companies)} companies | Keywords: {len(keywords)} | Locations: {locations}\n")

    all_matches = []
    errors = []

    for company in companies:
        # Skip duplicate companies (targets.yml has some duplicates currently)
        try:
            matches = scan_company(company, keywords, locations, exclude_titles)
            new = [m for m in matches if m["url"] not in seen_urls]
            all_matches.extend(new)
            seen_urls.update(m["url"] for m in new)
        except Exception as e:
            errors.append({"company": company["name"], "error": str(e)})

    print(f"\n✅ Scan complete. {len(all_matches)} new roles found.\n")

    if all_matches:
        for i, job in enumerate(all_matches, 1):
            print(f"  [{i}] {job['company']} — {job['title']} — {job['location']}")
            print(f"       {job['url']}\n")

    if not args.dry_run and all_matches:
        # Add to pipeline
        new_entries = [
            {
                "company": j["company"],
                "job_title": j["title"],
                "tier": None,
                "match_score": None,
                "status": "discovered",
                "url": j["url"],
                "location": j["location"],
                "evaluated_date": None,
                "application_date": None,
                "cv_version": None,
                "notes": f"Found via scan on {date.today()}"
            }
            for j in all_matches
        ]
        pipeline.extend(new_entries)
        save_json(PIPELINE_FILE, pipeline)
        print(f"💾 Saved {len(new_entries)} new entries to pipeline.json")

    # Update scan log
    if not args.dry_run:
        scan_log = {
            "last_scan": datetime.now().isoformat(),
            "companies_checked": [c["name"] for c in companies],
            "new_roles_found": len(all_matches),
            "errors": errors
        }
        save_json(SCAN_LOG_FILE, scan_log)

if __name__ == "__main__":
    main()
