"""Command-line entry point.

Usage:
    python -m briefing fetch [--force]     fetch today's listings into data/<date>/papers.json
    python -m briefing pending             list days and finished weeks that still need a briefing
    python -m briefing digest DATE         print a compact text view of a day's papers
    python -m briefing validate DATE|WEEK  check data/<date>/briefing.json or data/weekly/<week>.json
    python -m briefing build               validate everything and regenerate the site
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from .config import load_config
from .pipeline import digest, fetch_day, pending_days, pending_weeks
from .site import BriefingError, build_site, read_json
from .validate import validate_briefing, validate_weekly
from .weekly import week_dates


def cmd_validate(root: Path, key: str) -> list[str]:
    if "-W" in key:
        weekly = read_json(root / "data" / "weekly" / f"{key}.json")
        snapshots = [
            read_json(p)
            for d in week_dates(key)
            if (p := root / "data" / d / "papers.json").exists()
        ]
        return validate_weekly(weekly, key, snapshots)
    day = root / "data" / key
    return validate_briefing(read_json(day / "briefing.json"), read_json(day / "papers.json"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m briefing")
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    parser.add_argument("--config", default=None, help="config file (default: <root>/config.toml)")
    sub = parser.add_subparsers(dest="command", required=True)
    fetch = sub.add_parser("fetch")
    fetch.add_argument("--force", action="store_true")
    sub.add_parser("pending")
    dig = sub.add_parser("digest")
    dig.add_argument("date")
    val = sub.add_parser("validate")
    val.add_argument("key")
    sub.add_parser("build")
    args = parser.parse_args(argv)

    root = Path(args.root)
    config = load_config(args.config or root / "config.toml")

    if args.command == "fetch":
        status, day = fetch_day(root, config, force=args.force)
        snapshot = read_json(root / "data" / day / "papers.json")
        print(json.dumps({"status": status, "date": day, "total": snapshot["total"], "selected": snapshot["selected"]}))
    elif args.command == "pending":
        print(json.dumps({"days": pending_days(root), "weeks": pending_weeks(root, date.today().isoformat())}))
    elif args.command == "digest":
        sys.stdout.write(digest(read_json(root / "data" / args.date / "papers.json"), config))
    elif args.command == "validate":
        errors = cmd_validate(root, args.key)
        print("\n".join(errors) if errors else "OK")
        return 1 if errors else 0
    elif args.command == "build":
        try:
            written = build_site(root, config)
        except BriefingError as exc:
            print(exc, file=sys.stderr)
            return 1
        print(f"wrote {len(written)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
