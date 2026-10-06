from __future__ import annotations

import html as htmllib
import re
import time
import urllib.error
import urllib.request
from datetime import datetime

USER_AGENT = "Mozilla/5.0 (arxiv-briefing)"

LISTING_DATE_RE = re.compile(r"Showing new listings for \w+, (\d{1,2} \w+ \d{4})")
SECTION_RE = re.compile(r"<h3[^>]*>([^<]+)</h3>", re.I)
ID_RE = re.compile(r'href\s*=\s*["\']/abs/([^"\']+)["\']', re.I)
TITLE_RE = re.compile(r"list-title[^>]*>\s*<span[^>]*>Title:</span>\s*(.*?)\s*</div>", re.S)
AUTHORS_RE = re.compile(r"list-authors[^>]*>(.*?)</div>", re.S)
SUBJECTS_RE = re.compile(r"list-subjects[^>]*>\s*<span[^>]*>Subjects:</span>\s*(.*?)\s*</div>", re.S)
PRIMARY_RE = re.compile(r'primary-subject[^>]*>[^<]*\(([^)]+)\)</span>', re.S)
ABSTRACT_RE = re.compile(r"<p class=['\"]mathjax['\"][^>]*>(.*?)</p>", re.S)


def listing_url(category: str) -> str:
    return f"https://arxiv.org/list/{category}/new?skip=0&show=2000"


def fetch_listing_html(category: str) -> str:
    """Download the raw /new listing page for one arXiv category."""
    url = listing_url(category)
    last_error: Exception | None = None
    for attempt in range(3):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Cache-Control": "no-cache"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            if exc.code != 429:
                raise
            last_error = exc
        time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"failed to fetch {url}") from last_error


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = htmllib.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def parse_listing_date(page: str) -> str:
    """Return the announcement date of a /new listing page as YYYY-MM-DD."""
    m = LISTING_DATE_RE.search(page)
    if not m:
        raise ValueError("listing page has no 'Showing new listings for ...' header")
    return datetime.strptime(m.group(1), "%d %B %Y").date().isoformat()


def section_kind(heading: str) -> str:
    h = heading.lower()
    if "cross" in h:
        return "cross"
    if "replac" in h:
        return "replace"
    if "new submission" in h:
        return "new"
    return "other"


def split_sections(page: str):
    marks = [(m.start(), section_kind(m.group(1))) for m in SECTION_RE.finditer(page)]
    for i, (pos, kind) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(page)
        if kind != "other":
            yield kind, page[pos:end]


def parse_entry(chunk: str, section: str) -> dict | None:
    mid = ID_RE.search(chunk)
    if not mid:
        return None
    mtitle = TITLE_RE.search(chunk)
    mauthors = AUTHORS_RE.search(chunk)
    msubjects = SUBJECTS_RE.search(chunk)
    mprimary = PRIMARY_RE.search(chunk)
    mabstract = ABSTRACT_RE.search(chunk)
    authors_html = mauthors.group(1) if mauthors else ""
    return {
        "arxiv_id": mid.group(1),
        "title": strip_tags(mtitle.group(1)) if mtitle else "",
        "authors": [strip_tags(a) for a in re.findall(r"<a[^>]*>(.*?)</a>", authors_html, re.S)],
        "subjects": strip_tags(msubjects.group(1)) if msubjects else "",
        "primary_cat": mprimary.group(1).strip() if mprimary else "",
        "section": section,
        "abstract": strip_tags(mabstract.group(1)) if mabstract else "",
    }


def parse_papers(page: str) -> list[dict]:
    """Parse every paper on a /new listing page, labelled new, cross or replace."""
    papers = []
    for section, block in split_sections(page):
        for chunk in re.split(r"""<dt>\s*<a\s+name=["']item""", block)[1:]:
            entry = parse_entry(chunk, section)
            if entry:
                papers.append(entry)
    return papers
