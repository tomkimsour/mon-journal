import json

import pytest

from briefing.pipeline import digest, fetch_day, pending_days, pending_weeks
from briefing.site import BriefingError, build_site


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


@pytest.fixture
def repo(tmp_path, snapshot, briefing):
    write_json(tmp_path / "data/2026-10-06/papers.json", snapshot)
    write_json(tmp_path / "data/2026-10-06/briefing.json", briefing)
    return tmp_path


def test_should_write_daily_post(repo, config):
    build_site(repo, config)
    assert (repo / "posts/2026-10-06.html").exists()


def test_should_write_index(repo, config):
    build_site(repo, config)
    assert "Contact becomes a first-class control signal" in (repo / "index.html").read_text()


def test_should_write_feed(repo, config):
    build_site(repo, config)
    assert (repo / "feed.xml").exists()


def test_should_write_stylesheet(repo, config):
    build_site(repo, config)
    assert (repo / "assets/style.css").exists()


def test_should_skip_day_without_briefing(repo, config, snapshot):
    write_json(repo / "data/2026-10-07/papers.json", dict(snapshot, date="2026-10-07"))
    build_site(repo, config)
    assert not (repo / "posts/2026-10-07.html").exists()


def test_should_raise_on_invalid_briefing(repo, config, briefing):
    briefing["must_read"][0]["id"] = "9999.99999"
    write_json(repo / "data/2026-10-06/briefing.json", briefing)
    with pytest.raises(BriefingError):
        build_site(repo, config)


def test_should_write_weekly_post_when_weekly_briefing_exists(repo, config):
    write_json(
        repo / "data/weekly/2026-W41.json",
        {
            "week": "2026-W41",
            "headline": "Contact sensing week",
            "summary": "Touch dominated.",
            "trends": [],
            "top_papers": [{"id": "2610.00001", "why": "Best."}],
        },
    )
    build_site(repo, config)
    assert (repo / "posts/2026-W41.html").exists()


def fake_fetcher(listing_html):
    def fetch(category):
        return listing_html
    return fetch


def test_should_write_snapshot_for_new_listing(tmp_path, config, listing_html):
    fetch_day(tmp_path, config, fake_fetcher(listing_html))
    assert (tmp_path / "data/2026-10-06/papers.json").exists()


def test_should_report_new_listing_status(tmp_path, config, listing_html):
    assert fetch_day(tmp_path, config, fake_fetcher(listing_html)) == ("new", "2026-10-06")


def test_should_report_existing_listing_status(tmp_path, config, listing_html):
    fetch_day(tmp_path, config, fake_fetcher(listing_html))
    assert fetch_day(tmp_path, config, fake_fetcher(listing_html)) == ("exists", "2026-10-06")


def test_should_list_days_missing_a_briefing(repo, snapshot):
    write_json(repo / "data/2026-10-07/papers.json", dict(snapshot, date="2026-10-07"))
    assert pending_days(repo) == ["2026-10-07"]


def test_should_group_digest_by_bucket(snapshot, config):
    text = digest(snapshot, config)
    assert text.index("Manipulation") < text.index("2610.00001") < text.index("Navigation")


def test_should_include_abstract_in_digest(snapshot, config):
    assert "We study navigation." in digest(snapshot, config)


def test_should_list_finished_week_without_recap(repo):
    assert pending_weeks(repo, today="2026-10-10") == ["2026-W41"]


def test_should_not_list_week_before_its_friday_has_passed(repo):
    assert pending_weeks(repo, today="2026-10-09") == []


def test_should_not_list_week_that_already_has_recap(repo):
    write_json(repo / "data/weekly/2026-W41.json", {})
    assert pending_weeks(repo, today="2026-10-12") == []
