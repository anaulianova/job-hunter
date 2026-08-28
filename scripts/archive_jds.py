#!/usr/bin/env python3
"""Archive processed JD files from jds/ into jds/evaluated/.

A JD file is "processed" once its role exists in pipeline/pipeline.json with any
status other than `discovered` — i.e. it has actually been evaluated, skipped,
withdrawn or applied to.

Run this after an evaluation batch. It sweeps everything in one pass, so a file
missed during an individual evaluation is picked up on the next run rather than
accumulating. That is the point: a per-file "remember to move it" rule fails
silently and at scale, a sweep does not.

    uv run scripts/archive_jds.py            # move everything matched
    uv run scripts/archive_jds.py --dry-run  # show what would move
    uv run scripts/archive_jds.py --file X   # move one named file
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JDS = ROOT / "jds"
ARCHIVE = JDS / "evaluated"
PIPELINE = ROOT / "pipeline" / "pipeline.json"
KEEP = {"README.txt", ".gitkeep", ".DS_Store"}

# Filename company tokens that do not match the pipeline company string directly.
ALIASES = {
    "jpm": "jpmorgan chase", "jpmorgan": "jpmorgan chase",
    "bofa": "bank of america", "federal": "federal reserve bank of new york",
    "millenium": "millenium", "millennium": "millenium",
    "ms": "morgan stanley", "rbc": "rbc", "bcgx": "bcg x",
    "oxford": "oxford knight", "oliver": "oliver bernard",
    "dow": "dow jones", "state": "state street",
}


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def processed_companies() -> set[str]:
    """Company names that have at least one non-`discovered` pipeline entry."""
    if not PIPELINE.exists():
        sys.exit(f"❌ {PIPELINE} not found")
    entries = json.load(open(PIPELINE))
    return {norm(e["company"]) for e in entries
            if e.get("status") and e["status"] != "discovered"}


def file_tokens(name: str) -> list[str]:
    """Leading tokens of a filename, date suffix and extension stripped."""
    stem = Path(name).stem
    stem = re.sub(r"_(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\d{1,2}$", "", stem, flags=re.I)
    return [t for t in re.split(r"[^a-z0-9]+", stem.lower()) if t]


def match(name: str, companies: set[str]) -> str | None:
    toks = file_tokens(name)
    if not toks:
        return None
    # try progressively shorter leading token runs: "morgan stanley b e" -> "morgan stanley" -> "morgan"
    for n in range(min(3, len(toks)), 0, -1):
        cand = " ".join(toks[:n])
        cand = ALIASES.get(cand, cand)
        if cand in companies:
            return cand
        for c in companies:
            if c.startswith(cand) and len(cand) >= 4:
                return c
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="show what would move, change nothing")
    ap.add_argument("--file", help="archive one named file regardless of pipeline state")
    args = ap.parse_args()

    ARCHIVE.mkdir(parents=True, exist_ok=True)
    companies = processed_companies()

    if args.file:
        src = JDS / args.file
        if not src.exists():
            sys.exit(f"❌ {src} not found")
        if not args.dry_run:
            shutil.move(str(src), str(ARCHIVE / src.name))
        print(f"{'would move' if args.dry_run else '✅ moved'}: {src.name}")
        return

    files = [p for p in JDS.iterdir()
             if p.is_file() and p.name not in KEEP and not p.name.startswith(".")]
    moved, skipped = [], []
    for p in sorted(files):
        hit = match(p.name, companies)
        if hit:
            moved.append((p, hit))
            if not args.dry_run:
                shutil.move(str(p), str(ARCHIVE / p.name))
        else:
            skipped.append(p)

    verb = "would archive" if args.dry_run else "archived"
    print(f"✅ {verb} {len(moved)} JD file(s) → jds/evaluated/")
    for p, hit in moved:
        print(f"   {p.name}  →  matched pipeline entry: {hit}")
    if skipped:
        print(f"\n⚠  {len(skipped)} file(s) left in jds/ — no evaluated pipeline entry found:")
        for p in skipped:
            print(f"   {p.name}")
        print("   Either the role has not been evaluated yet, or the filename does not")
        print("   match its company. Evaluate it, or move it by hand with --file.")


if __name__ == "__main__":
    main()
