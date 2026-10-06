from __future__ import annotations

import re
from functools import lru_cache

from .config import Bucket, Config

TITLE_WEIGHT = 2


@lru_cache(maxsize=None)
def keyword_pattern(keyword: str) -> re.Pattern:
    return re.compile(r"(?<![a-z0-9])" + re.escape(keyword) + r"(?:s|es)?(?![a-z0-9])")


def count_hits(text: str, keywords: list[str]) -> int:
    return sum(1 for kw in keywords if keyword_pattern(kw).search(text))


def assign_bucket(paper: dict, buckets: list[Bucket]) -> str:
    """Return the name of the best-matching bucket for a paper, or "" if none match."""
    title = paper.get("title", "").lower()
    body = (paper.get("abstract", "") + " " + paper.get("subjects", "")).lower()
    best, best_score = "", 0
    for bucket in buckets:
        score = TITLE_WEIGHT * count_hits(title, bucket.keywords) + count_hits(body, bucket.keywords)
        if score > best_score:
            best, best_score = bucket.name, score
    return best


def short_label(category: str) -> str:
    return category.split(".", 1)[-1]


def badge(paper: dict, categories: list[str]) -> str:
    """Label a paper with the configured categories it belongs to, primary first, e.g. "RO/AI"."""
    subjects = paper.get("subjects", "")
    present = [c for c in categories if f"({c})" in subjects]
    primary = paper.get("primary_cat", "")
    if primary in present:
        present.remove(primary)
        present.insert(0, primary)
    return "/".join(short_label(c) for c in present)


def build_snapshot(listings: list[dict], config: Config) -> dict:
    """Merge per-category listings into one day's deduplicated, bucketed snapshot."""
    dates = {listing["date"] for listing in listings}
    if len(dates) != 1:
        raise ValueError(f"listings disagree on announcement date: {sorted(dates)}")
    date = dates.pop()

    unique: dict[str, dict] = {}
    for listing in listings:
        for paper in listing["papers"]:
            if paper["section"] == "replace":
                continue
            unique.setdefault(paper["arxiv_id"], paper)

    counts = {b.name: 0 for b in config.buckets}
    selected = []
    for paper in unique.values():
        bucket = assign_bucket(paper, config.buckets)
        if not bucket:
            continue
        counts[bucket] += 1
        selected.append(dict(paper, bucket=bucket, badge=badge(paper, config.categories)))

    return {
        "date": date,
        "categories": list(config.categories),
        "total": len(unique),
        "selected": len(selected),
        "bucket_counts": counts,
        "papers": selected,
    }
