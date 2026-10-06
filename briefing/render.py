from __future__ import annotations

from datetime import date as Date
from html import escape

from .config import Config
from .weekly import aggregate_week, week_dates

ARXIV_ABS = "https://arxiv.org/abs/"


def e(text) -> str:
    return escape(str(text), quote=True)


def weekday(day: str) -> str:
    return Date.fromisoformat(day).strftime("%a")


def page(title: str, body: str, config: Config, css_href: str, feed_href: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="{e(config.site.language)}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<link rel="stylesheet" href="{css_href}">
<link rel="alternate" type="application/rss+xml" title="{e(config.site.title)}" href="{feed_href}">
</head>
<body>
<main class="container">
{body}
<footer>Generated from arXiv listings for {e(" · ".join(config.categories))}. Summaries are AI-written from abstracts; check the paper before citing.</footer>
</main>
</body>
</html>
"""


def authors_line(authors: list[str], limit: int = 4) -> str:
    if len(authors) <= limit:
        return ", ".join(authors)
    return ", ".join(authors[:limit]) + " et al."


def paper_link(paper: dict) -> str:
    pid = paper["arxiv_id"]
    return f'<a href="{ARXIV_ABS}{e(pid)}">{e(paper["title"])}</a>'


def paper_header(paper: dict) -> str:
    badge = f' <span class="badge">{e(paper["badge"])}</span>' if paper.get("badge") else ""
    return (
        f'<div class="paper-title">{paper_link(paper)}{badge}</div>'
        f'<div class="authors">{e(authors_line(paper.get("authors", [])))} · '
        f'<span class="pid">arXiv:{e(paper["arxiv_id"])}</span></div>'
    )


def summary_block(summary: dict) -> str:
    return (
        '<ul class="summary">'
        f'<li><strong>Problem</strong> {e(summary["problem"])}</li>'
        f'<li><strong>Method</strong> {e(summary["method"])}</li>'
        f'<li><strong>Why it matters</strong> {e(summary["why"])}</li>'
        "</ul>"
    )


def abstract_block(paper: dict) -> str:
    if not paper.get("abstract"):
        return ""
    return f'<details class="abstract"><summary>Abstract</summary><p>{e(paper["abstract"])}</p></details>'


def paper_ref(pid: str, by_id: dict) -> str:
    paper = by_id.get(pid)
    if not paper:
        return e(pid)
    return f'<a href="#p-{e(pid)}" title="{e(paper["title"])}">{e(short_title(paper["title"]))}</a>'


def short_title(title: str) -> str:
    head = title.split(":", 1)[0]
    return head if len(head) <= 48 else head[:45].rstrip() + "…"


def bucket_nav(config: Config, counts: dict) -> str:
    chips = [
        f'<a class="chip" href="#b-{i}">{e(b.emoji)} {e(b.name)} <span>{counts.get(b.name, 0)}</span></a>'
        for i, b in enumerate(config.buckets)
        if counts.get(b.name, 0)
    ]
    return f'<nav class="chips">{"".join(chips)}</nav>'


def clusters_table(clusters: list[dict], by_id: dict) -> str:
    rows = []
    for c in clusters:
        refs = "<br>".join(paper_ref(pid, by_id) for pid in c["paper_ids"])
        level = str(c["confidence"]).lower()
        rows.append(
            f'<tr><td class="c-title">{e(c["title"])}</td><td class="c-papers">{refs}</td>'
            f'<td>{e(c["why"])}</td><td><span class="conf conf-{e(level)}">{e(level)}</span></td></tr>'
        )
    return (
        '<div class="table-wrap"><table class="clusters"><thead><tr>'
        "<th>Cluster</th><th>Papers</th><th>Why it matters</th><th>Confidence</th>"
        f'</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
    )


def must_read_cards(items: list[dict], by_id: dict) -> str:
    cards = []
    for item in items:
        paper = by_id[item["id"]]
        cards.append(
            '<article class="card">'
            f"{paper_header(paper)}"
            "<dl>"
            f'<dt>Why read it</dt><dd>{e(item["why"])}</dd>'
            f'<dt>Key idea</dt><dd>{e(item["key_idea"])}</dd>'
            f'<dt>Evidence</dt><dd>{e(item["evidence"])}</dd>'
            f'<dt>Caveat</dt><dd>{e(item["caveat"])}</dd>'
            "</dl></article>"
        )
    return "".join(cards)


def bucket_sections(snapshot: dict, summaries: dict, config: Config) -> str:
    sections = []
    for i, bucket in enumerate(config.buckets):
        papers = [p for p in snapshot["papers"] if p["bucket"] == bucket.name]
        if not papers:
            continue
        papers.sort(key=lambda p: p["arxiv_id"] not in summaries)
        items = []
        for p in papers:
            detail = summary_block(summaries[p["arxiv_id"]]) if p["arxiv_id"] in summaries else abstract_block(p)
            items.append(f'<li class="paper" id="p-{e(p["arxiv_id"])}">{paper_header(p)}{detail}</li>')
        sections.append(
            f'<section class="bucket" id="b-{i}"><h3>{e(bucket.emoji)} {e(bucket.name)} '
            f'<span class="count">{len(papers)}</span></h3><ul class="papers">{"".join(items)}</ul></section>'
        )
    return "".join(sections)


def render_daily(snapshot: dict, briefing: dict, config: Config) -> str:
    """Render one day's briefing page (served from posts/)."""
    day = snapshot["date"]
    by_id = {p["arxiv_id"]: p for p in snapshot["papers"]}
    summaries = briefing["summaries"]
    insights = briefing.get("insights") or []

    parts = [
        '<a class="home" href="../index.html">← All briefings</a>',
        f"<h1>{e(config.site.title)} <span class='date'>{e(day)} ({weekday(day)})</span></h1>",
        f'<p class="meta">{snapshot["selected"]} of {snapshot["total"]} new papers in '
        f'{e(" · ".join(snapshot["categories"]))} matched a bucket · {len(summaries)} summarized</p>',
        bucket_nav(config, snapshot["bucket_counts"]),
        f'<section class="lead"><p class="headline">{e(briefing["headline"])}</p>'
        f'<p class="thesis">{e(briefing["thesis"])}</p></section>',
        "<h2>Clusters</h2>",
        clusters_table(briefing["clusters"], by_id),
    ]
    if insights:
        parts.append("<h2>Insights</h2><ol class='insights'>" + "".join(f"<li>{e(i)}</li>" for i in insights) + "</ol>")
    if briefing["must_read"]:
        parts += ["<h2>Must-read</h2>", must_read_cards(briefing["must_read"], by_id)]
    parts += ["<h2>Papers by bucket</h2>", bucket_sections(snapshot, summaries, config)]

    return page(f"{config.site.title} — {day}", "\n".join(parts), config, "../assets/style.css", "../feed.xml")


def bucket_bars(counts: dict, config: Config) -> str:
    peak = max(counts.values(), default=0) or 1
    rows = []
    for b in config.buckets:
        n = counts.get(b.name, 0)
        rows.append(
            f'<div class="bar-row"><span class="bar-label">{e(b.emoji)} {e(b.name)}</span>'
            f'<span class="bar"><span style="width:{100 * n / peak:.1f}%"></span></span>'
            f'<span class="bar-value">{n}</span></div>'
        )
    return f'<div class="bars">{"".join(rows)}</div>'


def week_paper_link(pid: str, papers: dict) -> str:
    paper = papers.get(pid)
    if not paper:
        return e(pid)
    return f'<a href="{ARXIV_ABS}{e(pid)}">{e(short_title(paper["title"]))}</a>'


def render_weekly(week_id: str, days: list[tuple[dict, dict]], weekly: dict, config: Config) -> str:
    """Render one ISO week's recap page (served from posts/)."""
    agg = aggregate_week(days)
    papers = agg["papers"]
    dates = week_dates(week_id)

    parts = [
        '<a class="home" href="../index.html">← All briefings</a>',
        f"<h1>{e(config.site.title)} <span class='date'>Weekly {e(week_id)}</span></h1>",
        f'<p class="meta">{e(dates[0])} → {e(dates[-1])} · {len(agg["days"])} daily briefings · '
        f'{agg["selected"]} of {agg["total"]} new papers matched a bucket</p>',
        f'<section class="lead"><p class="headline">{e(weekly["headline"])}</p>'
        f'<p class="thesis">{e(weekly["summary"])}</p></section>',
    ]

    if weekly["trends"]:
        parts.append("<h2>Trends</h2>")
        for t in weekly["trends"]:
            refs = ", ".join(week_paper_link(pid, papers) for pid in t.get("paper_ids", []))
            parts.append(
                f'<section class="trend"><h3>{e(t["title"])}</h3><p>{e(t["body"])}</p>'
                + (f'<p class="refs">Papers: {refs}</p>' if refs else "")
                + "</section>"
            )

    parts.append("<h2>Top papers</h2><ol class='top-papers'>")
    for item in weekly["top_papers"]:
        p = papers[item["id"]]
        parts.append(
            f'<li>{paper_header(p)}<p class="why">{e(item["why"])} '
            f'<a class="day-link" href="{e(p["date"])}.html">{e(p["date"])}</a></p></li>'
        )
    parts.append("</ol>")

    parts.append("<h2>Daily briefings</h2><ul class='days'>")
    for d in agg["days"]:
        parts.append(
            f'<li><a href="{e(d["date"])}.html">{e(d["date"])} ({weekday(d["date"])})</a> — '
            f'{e(d["headline"])} <span class="muted">{d["selected"]}/{d["total"]}</span></li>'
        )
    parts.append("</ul>")

    parts += ["<h2>Bucket volume</h2>", bucket_bars(agg["bucket_counts"], config)]

    if weekly.get("next_week"):
        parts.append("<h2>Watch next week</h2><ul>" + "".join(f"<li>{e(x)}</li>" for x in weekly["next_week"]) + "</ul>")

    return page(f"{config.site.title} — {week_id}", "\n".join(parts), config, "../assets/style.css", "../feed.xml")


def render_index(entries, config: Config) -> str:
    """Render the archive home page listing every briefing, newest first."""
    ordered = sorted(entries, key=lambda x: (x.date, x.kind == "weekly"), reverse=True)
    items = []
    for x in ordered:
        if x.kind == "weekly":
            label = f'{e(x.key)} <span class="weekly-badge">weekly</span>'
        else:
            label = f'{e(x.key)} <span class="dow">{weekday(x.key)}</span>'
        items.append(
            f'<li><a class="archive-link" href="{e(x.href)}"><span class="archive-date">{label}</span>'
            f'<span class="archive-count">{x.selected}/{x.total}</span>'
            f'<span class="archive-headline">{e(x.headline)}</span></a></li>'
        )
    body = (
        f"<h1>{e(config.site.title)}</h1>"
        f'<p class="subtitle">{e(config.site.subtitle)}</p>'
        f'<p class="subscribe">Subscribe with any RSS reader: <a href="feed.xml">feed.xml</a></p>'
        f'<ul class="archive">{"".join(items)}</ul>'
    )
    return page(config.site.title, body, config, "assets/style.css", "feed.xml")
