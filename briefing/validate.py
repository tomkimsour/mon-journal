from __future__ import annotations

CONFIDENCE_LEVELS = {"high", "medium", "low"}
SUMMARY_FIELDS = ("problem", "method", "why")
MUST_READ_FIELDS = ("id", "why", "key_idea", "evidence", "caveat")
CLUSTER_FIELDS = ("title", "why", "paper_ids", "confidence")


def missing_fields(obj: dict, fields, where: str) -> list[str]:
    return [f"{where}: missing '{f}'" for f in fields if f not in obj]


def unknown_ids(ids, known: set[str], where: str) -> list[str]:
    return [f"{where}: unknown paper id {pid}" for pid in ids if pid not in known]


def validate_briefing(briefing: dict, snapshot: dict) -> list[str]:
    """Check an agent-written daily briefing against the day's snapshot; return error messages."""
    errors = missing_fields(briefing, ("date", "headline", "thesis", "clusters", "must_read", "summaries"), "briefing")
    if errors:
        return errors

    known = {p["arxiv_id"] for p in snapshot["papers"]}
    if briefing["date"] != snapshot["date"]:
        errors.append(f"briefing: date {briefing['date']} does not match snapshot date {snapshot['date']}")

    for i, cluster in enumerate(briefing["clusters"]):
        where = f"clusters[{i}]"
        errors += missing_fields(cluster, CLUSTER_FIELDS, where)
        errors += unknown_ids(cluster.get("paper_ids", []), known, where)
        level = str(cluster.get("confidence", "")).lower()
        if "confidence" in cluster and level not in CONFIDENCE_LEVELS:
            errors.append(f"{where}: confidence must be one of {sorted(CONFIDENCE_LEVELS)}")

    for i, item in enumerate(briefing["must_read"]):
        where = f"must_read[{i}]"
        errors += missing_fields(item, MUST_READ_FIELDS, where)
        errors += unknown_ids([item["id"]] if "id" in item else [], known, where)

    for pid, summary in briefing["summaries"].items():
        where = f"summaries[{pid}]"
        errors += unknown_ids([pid], known, where)
        errors += missing_fields(summary, SUMMARY_FIELDS, where)

    return errors


def validate_weekly(weekly: dict, week_id: str, snapshots: list[dict]) -> list[str]:
    """Check an agent-written weekly briefing against the snapshots of that week; return error messages."""
    errors = missing_fields(weekly, ("week", "headline", "summary", "trends", "top_papers"), "weekly")
    if errors:
        return errors

    known = {p["arxiv_id"] for s in snapshots for p in s["papers"]}
    if weekly["week"] != week_id:
        errors.append(f"weekly: week {weekly['week']} does not match file week {week_id}")

    for i, trend in enumerate(weekly["trends"]):
        where = f"trends[{i}]"
        errors += missing_fields(trend, ("title", "body"), where)
        errors += unknown_ids(trend.get("paper_ids", []), known, where)

    for i, item in enumerate(weekly["top_papers"]):
        where = f"top_papers[{i}]"
        errors += missing_fields(item, ("id", "why"), where)
        errors += unknown_ids([item["id"]] if "id" in item else [], known, where)

    return errors
