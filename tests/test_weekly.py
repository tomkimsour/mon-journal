from briefing.weekly import aggregate_week, iso_week_id, week_dates


def test_should_compute_iso_week_id():
    assert iso_week_id("2026-10-06") == "2026-W41"


def test_should_pad_single_digit_week_number():
    assert iso_week_id("2026-01-05") == "2026-W02"


def test_should_list_seven_dates_in_week():
    assert len(week_dates("2026-W41")) == 7


def test_should_start_week_on_monday():
    assert week_dates("2026-W41")[0] == "2026-10-05"


def test_should_end_week_on_sunday():
    assert week_dates("2026-W41")[-1] == "2026-10-11"


def second_day(snapshot):
    other = dict(snapshot, date="2026-10-07", total=5, selected=4)
    other["bucket_counts"] = {"Manipulation": 3, "Navigation": 0, "Generative": 1}
    return other


def test_should_sum_totals_across_days(snapshot, briefing):
    agg = aggregate_week([(snapshot, briefing), (second_day(snapshot), briefing)])
    assert agg["total"] == 8


def test_should_sum_selected_across_days(snapshot, briefing):
    agg = aggregate_week([(snapshot, briefing), (second_day(snapshot), briefing)])
    assert agg["selected"] == 6


def test_should_merge_bucket_counts_across_days(snapshot, briefing):
    agg = aggregate_week([(snapshot, briefing), (second_day(snapshot), briefing)])
    assert agg["bucket_counts"] == {"Manipulation": 4, "Navigation": 1, "Generative": 1}


def test_should_index_papers_by_id_with_their_date(snapshot, briefing):
    agg = aggregate_week([(snapshot, briefing)])
    assert agg["papers"]["2610.00002"]["date"] == "2026-10-06"


def test_should_keep_daily_headlines_in_date_order(snapshot, briefing):
    later = dict(briefing, headline="Later")
    agg = aggregate_week([(second_day(snapshot), later), (snapshot, briefing)])
    assert [d["date"] for d in agg["days"]] == ["2026-10-06", "2026-10-07"]
