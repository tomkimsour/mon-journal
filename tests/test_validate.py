from briefing.validate import validate_briefing, validate_weekly


def test_should_accept_valid_briefing(briefing, snapshot):
    assert validate_briefing(briefing, snapshot) == []


def test_should_report_date_mismatch(briefing, snapshot):
    briefing["date"] = "2026-10-05"
    assert any("date" in e for e in validate_briefing(briefing, snapshot))


def test_should_report_missing_required_field(briefing, snapshot):
    del briefing["headline"]
    assert any("headline" in e for e in validate_briefing(briefing, snapshot))


def test_should_report_unknown_paper_id_in_summaries(briefing, snapshot):
    briefing["summaries"]["9999.99999"] = {"problem": "p", "method": "m", "why": "w"}
    assert any("9999.99999" in e for e in validate_briefing(briefing, snapshot))


def test_should_report_unknown_paper_id_in_clusters(briefing, snapshot):
    briefing["clusters"][0]["paper_ids"].append("9999.99999")
    assert any("9999.99999" in e for e in validate_briefing(briefing, snapshot))


def test_should_report_unknown_paper_id_in_must_read(briefing, snapshot):
    briefing["must_read"][0]["id"] = "9999.99999"
    assert any("9999.99999" in e for e in validate_briefing(briefing, snapshot))


def test_should_report_summary_missing_field(briefing, snapshot):
    del briefing["summaries"]["2610.00001"]["method"]
    assert any("method" in e for e in validate_briefing(briefing, snapshot))


def test_should_report_invalid_confidence_level(briefing, snapshot):
    briefing["clusters"][0]["confidence"] = "certain"
    assert any("confidence" in e for e in validate_briefing(briefing, snapshot))


def test_should_report_must_read_missing_field(briefing, snapshot):
    del briefing["must_read"][0]["caveat"]
    assert any("caveat" in e for e in validate_briefing(briefing, snapshot))


def weekly_briefing():
    return {
        "week": "2026-W41",
        "headline": "Contact sensing week",
        "summary": "Touch dominated the week.",
        "trends": [{"title": "Touch", "body": "More tactile.", "paper_ids": ["2610.00001"]}],
        "top_papers": [{"id": "2610.00002", "why": "Best navigation paper."}],
        "next_week": ["Watch slip detection."],
    }


def test_should_accept_valid_weekly_briefing(snapshot):
    assert validate_weekly(weekly_briefing(), "2026-W41", [snapshot]) == []


def test_should_report_weekly_week_mismatch(snapshot):
    assert any("week" in e for e in validate_weekly(weekly_briefing(), "2026-W40", [snapshot]))


def test_should_report_unknown_paper_id_in_weekly_top_papers(snapshot):
    weekly = weekly_briefing()
    weekly["top_papers"][0]["id"] = "9999.99999"
    assert any("9999.99999" in e for e in validate_weekly(weekly, "2026-W41", [snapshot]))


def test_should_report_unknown_paper_id_in_weekly_trends(snapshot):
    weekly = weekly_briefing()
    weekly["trends"][0]["paper_ids"] = ["9999.99999"]
    assert any("9999.99999" in e for e in validate_weekly(weekly, "2026-W41", [snapshot]))
