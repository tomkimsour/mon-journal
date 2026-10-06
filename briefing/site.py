from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from .config import Config
from .feed import build_feed
from .render import render_daily, render_index, render_weekly
from .validate import validate_briefing, validate_weekly
from .weekly import week_dates

STYLE_SRC = Path(__file__).parent / "assets" / "style.css"


class BriefingError(ValueError):
    pass


@dataclass
class Entry:
    kind: str
    key: str
    date: str
    href: str
    headline: str
    summary: str
    selected: int
    total: int


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_days(root: Path) -> list[tuple[dict, dict]]:
    """Load every (snapshot, briefing) pair that has both files on disk."""
    days = []
    for day_dir in sorted((root / "data").glob("????-??-??")):
        papers, briefing = day_dir / "papers.json", day_dir / "briefing.json"
        if papers.exists() and briefing.exists():
            days.append((read_json(papers), read_json(briefing)))
    return days


def check(errors: list[str], source: str) -> None:
    if errors:
        raise BriefingError(f"{source}:\n  " + "\n  ".join(errors))


def build_site(root: str | Path, config: Config) -> list[Path]:
    """Validate all briefings and regenerate posts, index.html, feed.xml and assets."""
    root = Path(root)
    posts = root / "posts"
    posts.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    entries: list[Entry] = []

    days = load_days(root)
    for snapshot, briefing in days:
        check(validate_briefing(briefing, snapshot), f"data/{snapshot['date']}/briefing.json")

    for snapshot, briefing in days:
        day = snapshot["date"]
        out = posts / f"{day}.html"
        out.write_text(render_daily(snapshot, briefing, config), encoding="utf-8")
        written.append(out)
        entries.append(
            Entry("daily", day, day, f"posts/{day}.html", briefing["headline"], briefing["thesis"],
                  snapshot["selected"], snapshot["total"])
        )

    for weekly_path in sorted((root / "data" / "weekly").glob("????-W??.json")):
        week_id = weekly_path.stem
        dates = set(week_dates(week_id))
        week_days = [d for d in days if d[0]["date"] in dates]
        weekly = read_json(weekly_path)
        check(validate_weekly(weekly, week_id, [s for s, _ in week_days]), f"data/weekly/{weekly_path.name}")
        out = posts / f"{week_id}.html"
        out.write_text(render_weekly(week_id, week_days, weekly, config), encoding="utf-8")
        written.append(out)
        entries.append(
            Entry("weekly", week_id, max(dates), f"posts/{week_id}.html", weekly["headline"], weekly["summary"],
                  sum(s["selected"] for s, _ in week_days), sum(s["total"] for s, _ in week_days))
        )

    assets = root / "assets"
    assets.mkdir(exist_ok=True)
    shutil.copyfile(STYLE_SRC, assets / "style.css")
    (root / "index.html").write_text(render_index(entries, config), encoding="utf-8")
    (root / "feed.xml").write_text(build_feed(entries, config), encoding="utf-8")
    written += [assets / "style.css", root / "index.html", root / "feed.xml"]
    return written
