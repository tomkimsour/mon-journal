from __future__ import annotations

from datetime import datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

from .config import Config


def build_feed(entries, config: Config) -> str:
    """Render an RSS 2.0 feed of the newest briefings."""
    site = config.site
    ordered = sorted(entries, key=lambda x: (x.date, x.kind == "weekly"), reverse=True)[: site.feed_max_items]
    items = []
    for x in ordered:
        link = f"{site.base_url}/{x.href}"
        pub = format_datetime(datetime.fromisoformat(x.date).replace(tzinfo=timezone.utc))
        description = f"{x.headline}\n\n{x.summary}".strip()
        items.append(
            "<item>"
            f"<title>{escape(x.headline)}</title>"
            f"<link>{escape(link)}</link>"
            f'<guid isPermaLink="true">{escape(link)}</guid>'
            f"<pubDate>{pub}</pubDate>"
            f"<description>{escape(description)}</description>"
            "</item>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0"><channel>'
        f"<title>{escape(site.title)}</title>"
        f"<link>{escape(site.base_url)}/</link>"
        f"<description>{escape(site.subtitle)}</description>"
        f"<language>{escape(site.language)}</language>"
        + "".join(items)
        + "</channel></rss>\n"
    )
