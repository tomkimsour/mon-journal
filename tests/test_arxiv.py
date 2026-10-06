import pytest

from briefing.arxiv import parse_listing_date, parse_papers


def test_should_parse_announcement_date_from_listing_header(listing_html):
    assert parse_listing_date(listing_html) == "2026-10-06"


def test_should_raise_when_listing_header_is_missing():
    with pytest.raises(ValueError):
        parse_listing_date("<html><body></body></html>")


def test_should_parse_every_paper_in_listing(listing_html):
    assert len(parse_papers(listing_html)) == 4


def test_should_label_sections_in_listing_order(listing_html):
    sections = [p["section"] for p in parse_papers(listing_html)]
    assert sections == ["new", "new", "cross", "replace"]


def test_should_extract_arxiv_id(listing_html):
    assert parse_papers(listing_html)[0]["arxiv_id"] == "2610.03828"


def test_should_extract_title_without_descriptor(listing_html):
    title = parse_papers(listing_html)[0]["title"]
    assert title == "TACET: Context-Appropriate Acoustic-Social Navigation for Quadrupeds"


def test_should_extract_authors_in_order(listing_html):
    authors = parse_papers(listing_html)[0]["authors"]
    assert authors == ["Sungsan Park", "Young-Sik Shin", "Sanghyun Kim"]


def test_should_take_primary_category_from_primary_subject_span(listing_html):
    assert parse_papers(listing_html)[2]["primary_cat"] == "cond-mat.soft"


def test_should_keep_full_subjects_line(listing_html):
    subjects = parse_papers(listing_html)[1]["subjects"]
    assert subjects == (
        "Robotics (cs.RO); Artificial Intelligence (cs.AI); "
        "Computer Vision and Pattern Recognition (cs.CV)"
    )


def test_should_unescape_html_entities_in_abstract(listing_html):
    assert "a legged robot's locomotion noise" in parse_papers(listing_html)[0]["abstract"]


def test_should_strip_links_from_abstract(listing_html):
    assert "<a " not in parse_papers(listing_html)[0]["abstract"]
