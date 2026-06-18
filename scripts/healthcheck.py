"""
job-hunter: healthcheck.py
Health-check script for new users. Verifies the environment is correctly set up
before running any job-hunter commands.

Usage:
  uv run scripts/healthcheck.py
"""

import sys
import os
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent

PASS  = "✅"
FAIL  = "❌"
WARN  = "⚠️ "
INFO  = "ℹ️ "

results = []


def check(label, passed, fix=None, warning=False):
    symbol = WARN if warning else (PASS if passed else FAIL)
    results.append((symbol, label, fix, passed or warning))
    print(f"  {symbol}  {label}")
    if not passed and fix:
        print(f"       {fix}")


def section(title):
    print(f"\n── {title} {'─' * max(0, 50 - len(title))}")


# ── Python version ────────────────────────────────────────────────────────────

section("Python")

major, minor = sys.version_info[:2]
version_str = f"Python {major}.{minor}.{sys.version_info[2]}"
check(
    f"{version_str} detected",
    major == 3 and minor >= 10,
    fix="job-hunter requires Python 3.10 or later. Install it via https://python.org or use uv: uv python install 3.11"
)

# ── Dependencies ──────────────────────────────────────────────────────────────

section("Dependencies")

packages = {
    "dotenv":                 "python-dotenv",
    "yaml":                   "pyyaml",
    "requests":               "requests",
    "google.oauth2":          "google-auth",
    "googleapiclient":        "google-api-python-client",
    "google_auth_httplib2":   "google-auth-httplib2",
}

missing_packages = []
for module, pip_name in packages.items():
    try:
        __import__(module)
        check(f"{pip_name}", passed=True)
    except ImportError:
        missing_packages.append(pip_name)
        check(
            f"{pip_name}",
            passed=False,
            fix=f"Run: uv pip install {pip_name}"
        )

if missing_packages:
    all_missing = " ".join(missing_packages)
    print(f"\n  {INFO}  Install all at once: uv pip install {all_missing}")
    print(f"  {INFO}  Or install everything from requirements.txt: uv pip install -r requirements.txt")

# ── Environment file ──────────────────────────────────────────────────────────

section("Environment (.env)")

env_path = ROOT / ".env"
check(
    ".env file exists",
    env_path.exists(),
    fix="Create a .env file in the project root. Copy .env.example if one exists, or create it manually."
)

if env_path.exists():
    from dotenv import dotenv_values
    env = dotenv_values(env_path)

    sheet_id = env.get("GOOGLE_SHEET_ID", "").strip()
    check(
        "GOOGLE_SHEET_ID is set",
        bool(sheet_id),
        fix="Add GOOGLE_SHEET_ID=your_spreadsheet_id to .env. The ID is the long string in your Google Sheet URL."
    )
    if sheet_id:
        check(
            "GOOGLE_SHEET_ID looks valid (not a placeholder)",
            sheet_id not in ("your_spreadsheet_id", "YOUR_SHEET_ID", ""),
            fix="Replace the placeholder in GOOGLE_SHEET_ID with your actual spreadsheet ID."
        )

# ── Google credentials ────────────────────────────────────────────────────────

section("Google Sheets credentials")

creds_path = ROOT / "config" / "google_creds.json"
check(
    "config/google_creds.json exists",
    creds_path.exists(),
    fix=(
        "Download your Google service account key:\n"
        "       1. Go to console.cloud.google.com → your project → APIs & Services → Credentials\n"
        "       2. Click your service account → Keys → Add Key → JSON\n"
        "       3. Save the downloaded file as config/google_creds.json\n"
        "       4. Share your Google Sheet with the service account email (Editor access)"
    )
)

if creds_path.exists():
    try:
        with open(creds_path) as f:
            creds_data = json.load(f)
        has_email = "client_email" in creds_data
        check(
            f"Credentials file is valid (service account: {creds_data.get('client_email', 'unknown')})",
            has_email,
            fix="The credentials file appears malformed. Re-download it from Google Cloud Console."
        )
    except json.JSONDecodeError:
        check(
            "Credentials file is valid JSON",
            passed=False,
            fix="config/google_creds.json is not valid JSON. Re-download it from Google Cloud Console."
        )

# ── CV ────────────────────────────────────────────────────────────────────────

section("CV")

cv_path = ROOT / "cv.md"
check(
    "cv.md exists",
    cv_path.exists(),
    fix="Add your CV as cv.md in the project root, or run /onboard to build your profile and paste your CV there."
)

if cv_path.exists():
    size = cv_path.stat().st_size
    check(
        f"cv.md has content ({size:,} bytes)",
        size > 200,
        fix="cv.md appears empty or too short. Paste your full CV text into it."
    )

# ── User profile ──────────────────────────────────────────────────────────────

section("User profile")

profile_path = ROOT / "profile" / "user_profile.json"
check(
    "profile/user_profile.json exists",
    profile_path.exists(),
    fix="Run /onboard to create your profile. This is required before evaluating or applying to any role."
)

if profile_path.exists():
    try:
        with open(profile_path) as f:
            profile = json.load(f)

        required_fields = ["name", "search_parameters", "role_archetypes", "sensitive_roles"]
        missing_fields = [f for f in required_fields if f not in profile]

        check(
            "Profile has required fields",
            not missing_fields,
            fix=f"Profile is missing: {', '.join(missing_fields)}. Re-run /onboard to fill these in."
        )

        name = profile.get("name", "").strip()
        check(
            f"Profile name is set ({name or 'missing'})",
            bool(name),
            fix="Add your name to profile/user_profile.json under the 'name' field, or re-run /onboard."
        )

    except json.JSONDecodeError:
        check(
            "Profile is valid JSON",
            passed=False,
            fix="profile/user_profile.json is not valid JSON. Open it in a text editor and check for syntax errors, or re-run /onboard."
        )

# ── Pipeline directory ────────────────────────────────────────────────────────

section("Pipeline")

pipeline_dir = ROOT / "pipeline"
check(
    "pipeline/ directory exists",
    pipeline_dir.is_dir(),
    fix="Create the pipeline directory: mkdir pipeline"
)

pipeline_file = pipeline_dir / "pipeline.json"
if pipeline_file.exists():
    try:
        with open(pipeline_file) as f:
            pipeline = json.load(f)
        check(
            f"pipeline/pipeline.json is valid ({len(pipeline)} role(s) tracked)",
            isinstance(pipeline, list),
            fix="pipeline/pipeline.json should contain a JSON array. If corrupted, you can reset it to: []"
        )
    except json.JSONDecodeError:
        check(
            "pipeline/pipeline.json is valid JSON",
            passed=False,
            fix="pipeline/pipeline.json is not valid JSON. Reset it to an empty array: []"
        )
else:
    check(
        "pipeline/pipeline.json exists",
        passed=False,
        warning=True,
        fix="No pipeline file yet — this is normal if you haven't evaluated any roles. It will be created automatically on first /evaluate."
    )

reports_dir = pipeline_dir / "reports"
if not reports_dir.exists():
    check(
        "pipeline/reports/ directory exists",
        passed=False,
        warning=True,
        fix="Will be created automatically on first /evaluate."
    )

# ── Output directories ────────────────────────────────────────────────────────

section("Output directories")

for dirname in ["submitted", "tailored", "jds"]:
    dirpath = ROOT / dirname
    check(
        f"{dirname}/ directory exists",
        dirpath.is_dir(),
        fix=f"Create it: mkdir {dirname}"
    )

# ── Summary ───────────────────────────────────────────────────────────────────

print("\n" + "═" * 55)
print("  DOCTOR SUMMARY")
print("═" * 55)

failures = [(label, fix) for (sym, label, fix, ok) in results if not ok and sym == FAIL]
warnings = [(label, fix) for (sym, label, fix, ok) in results if sym == WARN]
passed   = sum(1 for (sym, label, fix, ok) in results if sym == PASS)
total    = len(results)

print(f"\n  {PASS}  {passed} checks passed")

if warnings:
    print(f"  {WARN}  {len(warnings)} warning(s) — non-blocking, will resolve as you use the system")

if failures:
    print(f"  {FAIL}  {len(failures)} issue(s) need fixing before you can use job-hunter:\n")
    for i, (label, fix) in enumerate(failures, 1):
        print(f"  {i}. {label}")
        if fix:
            print(f"     → {fix}\n")
    print("\n  Fix the issues above, then re-run: uv run scripts/doctor.py")
else:
    print(f"\n  You're all set. Start with:")
    print(f"    /onboard   — build your profile (first time)")
    print(f"    /evaluate  — paste a job URL or JD to evaluate a role")
    print(f"    /scan      — search for new roles")

print()
