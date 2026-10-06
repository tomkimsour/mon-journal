from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from .arxiv import fetch_listing_html, parse_listing_date, parse_papers
from .classify import build_snapshot
from .config import Config
from .weekly import iso_week_id, week_dates


def fetch_day(
    root: str | Path,
    config: Config,
    fetcher: Callable[[str], str] = fetch_listing_html,
    force: bool = False,
) -> tuple[str, str]:
    """Fetch today's listings and write data/<date>/papers.json; return ("new" | "exists", date)."""
    listings = []
    for category in config.categories:
        page = fetcher(category)
        listings.append({"category": category, "date": parse_listing_date(page), "papers": parse_papers(page)})

    snapshot = build_snapshot(listings, config)
    out = Path(root) / "data" / snapshot["date"] / "papers.json"
    if out.exists() and not force:
        return "exists", snapshot["date"]

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=1), encoding="utf-8")
    return "new", snapshot["date"]


def pending_days(root: str | Path) -> list[str]:
    """List dates that have a papers.json snapshot but no briefing.json yet."""
    return [
        d.name
        for d in sorted((Path(root) / "data").glob("????-??-??"))
        if (d / "papers.json").exists() and not (d / "briefing.json").exists()
    ]


def pending_weeks(root: str | Path, today: str) -> list[str]:
    """List ISO weeks whose Friday is before today, with daily briefings but no weekly recap."""
    data = Path(root) / "data"
    weeks = sorted({iso_week_id(d.parent.name) for d in data.glob("????-??-??/briefing.json")})
    return [
        w for w in weeks
        if week_dates(w)[4] < today and not (data / "weekly" / f"{w}.json").exists()
    ]


def digest(snapshot: dict, config: Config) -> str:
    """Render a snapshot as compact plain text grouped by bucket, for an agent to read."""
    lines = [
        f"# {snapshot['date']} — {snapshot['selected']} of {snapshot['total']} new papers matched a bucket",
    ]
    for bucket in config.buckets:
        papers = [p for p in snapshot["papers"] if p["bucket"] == bucket.name]
        if not papers:
            continue
        lines.append(f"\n## {bucket.name} ({len(papers)})")
        for p in papers:
            authors = ", ".join(p.get("authors", [])[:3]) + (" et al." if len(p.get("authors", [])) > 3 else "")
            lines.append(f"\n[{p['arxiv_id']}] {p['title']} ({p.get('badge', '')}) — {authors}")
            lines.append(p.get("abstract", ""))
    return "\n".join(lines) + "\n"
