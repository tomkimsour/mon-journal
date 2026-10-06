from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Site:
    title: str
    subtitle: str
    base_url: str
    language: str = "en"
    feed_max_items: int = 60


@dataclass
class Bucket:
    name: str
    emoji: str
    keywords: list[str] = field(default_factory=list)


@dataclass
class Config:
    site: Site
    categories: list[str]
    buckets: list[Bucket]


def load_config(path: str | Path) -> Config:
    """Load and validate the briefing configuration from a TOML file."""
    with open(path, "rb") as fh:
        raw = tomllib.load(fh)

    site_raw = raw["site"]
    site = Site(
        title=site_raw["title"],
        subtitle=site_raw.get("subtitle", ""),
        base_url=site_raw["base_url"].rstrip("/"),
        language=site_raw.get("language", "en"),
        feed_max_items=int(site_raw.get("feed_max_items", 60)),
    )

    categories = list(raw.get("arxiv", {}).get("categories", []))
    if not categories:
        raise ValueError("config: [arxiv].categories must list at least one category")

    buckets = []
    for b in raw.get("buckets", []):
        keywords = [k.strip().lower() for k in b.get("keywords", []) if k.strip()]
        if not keywords:
            raise ValueError(f"config: bucket {b.get('name')!r} has no keywords")
        buckets.append(Bucket(name=b["name"], emoji=b.get("emoji", ""), keywords=keywords))
    if not buckets:
        raise ValueError("config: at least one [[buckets]] entry is required")

    return Config(site=site, categories=categories, buckets=buckets)
