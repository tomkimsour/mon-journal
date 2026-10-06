from __future__ import annotations

from datetime import date, timedelta


def iso_week_id(day: str) -> str:
    """Return the ISO week id for a date, e.g. "2026-10-06" -> "2026-W41"."""
    year, week, _ = date.fromisoformat(day).isocalendar()
    return f"{year}-W{week:02d}"


def week_dates(week_id: str) -> list[str]:
    """Return the seven ISO dates (Monday to Sunday) of an ISO week id."""
    year, week = week_id.split("-W")
    monday = date.fromisocalendar(int(year), int(week), 1)
    return [(monday + timedelta(days=i)).isoformat() for i in range(7)]


def aggregate_week(days: list[tuple[dict, dict]]) -> dict:
    """Combine (snapshot, briefing) pairs of one week into totals, bucket counts and a paper index."""
    days = sorted(days, key=lambda d: d[0]["date"])
    bucket_counts: dict[str, int] = {}
    papers: dict[str, dict] = {}
    for snapshot, _ in days:
        for name, n in snapshot["bucket_counts"].items():
            bucket_counts[name] = bucket_counts.get(name, 0) + n
        for paper in snapshot["papers"]:
            papers[paper["arxiv_id"]] = dict(paper, date=snapshot["date"])
    return {
        "total": sum(s["total"] for s, _ in days),
        "selected": sum(s["selected"] for s, _ in days),
        "bucket_counts": bucket_counts,
        "days": [
            {"date": s["date"], "headline": b["headline"], "selected": s["selected"], "total": s["total"]}
            for s, b in days
        ],
        "papers": papers,
    }
