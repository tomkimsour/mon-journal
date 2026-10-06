from briefing.render import render_daily, render_index, render_weekly
from briefing.site import Entry


def test_should_link_each_paper_to_its_arxiv_abstract(snapshot, briefing, config):
    html = render_daily(snapshot, briefing, config)
    assert 'href="https://arxiv.org/abs/2610.00002"' in html


def test_should_escape_html_in_paper_titles(snapshot, briefing, config):
    html = render_daily(snapshot, briefing, config)
    assert "Dexterous &lt;grasping&gt; with tactile skins" in html


def test_should_show_summary_for_summarized_paper(snapshot, briefing, config):
    html = render_daily(snapshot, briefing, config)
    assert "Tactile skin feeds a slip detector" in html


def test_should_fall_back_to_abstract_for_unsummarized_paper(snapshot, briefing, config):
    html = render_daily(snapshot, briefing, config)
    assert "We study navigation." in html


def test_should_render_headline(snapshot, briefing, config):
    html = render_daily(snapshot, briefing, config)
    assert "Contact becomes a first-class control signal" in html


def test_should_render_cluster_titles(snapshot, briefing, config):
    html = render_daily(snapshot, briefing, config)
    assert "Touch-gated grasping" in html


def test_should_render_must_read_key_idea(snapshot, briefing, config):
    html = render_daily(snapshot, briefing, config)
    assert "Close the grasp loop on slip detection." in html


def test_should_render_insights(snapshot, briefing, config):
    html = render_daily(snapshot, briefing, config)
    assert "Grasp success now hinges on contact sensing" in html


def test_should_link_stylesheet_relative_to_posts_dir(snapshot, briefing, config):
    html = render_daily(snapshot, briefing, config)
    assert 'href="../assets/style.css"' in html


def test_should_omit_empty_buckets(snapshot, briefing, config):
    html = render_daily(snapshot, briefing, config)
    assert "Generative" not in html


def test_should_render_daily_without_optional_insights(snapshot, briefing, config):
    del briefing["insights"]
    assert "Touch-gated grasping" in render_daily(snapshot, briefing, config)


def weekly_briefing():
    return {
        "week": "2026-W41",
        "headline": "Contact sensing week",
        "summary": "Touch dominated the week.",
        "trends": [{"title": "Touch everywhere", "body": "More tactile.", "paper_ids": ["2610.00001"]}],
        "top_papers": [{"id": "2610.00002", "why": "Best navigation paper."}],
        "next_week": ["Watch slip detection."],
    }


def test_should_render_weekly_top_paper_title(snapshot, briefing, config):
    html = render_weekly("2026-W41", [(snapshot, briefing)], weekly_briefing(), config)
    assert "Social navigation for quadrupeds" in html


def test_should_render_weekly_trend_title(snapshot, briefing, config):
    html = render_weekly("2026-W41", [(snapshot, briefing)], weekly_briefing(), config)
    assert "Touch everywhere" in html


def test_should_link_weekly_to_its_daily_posts(snapshot, briefing, config):
    html = render_weekly("2026-W41", [(snapshot, briefing)], weekly_briefing(), config)
    assert 'href="2026-10-06.html"' in html


def entries():
    return [
        Entry("daily", "2026-10-05", "2026-10-05", "posts/2026-10-05.html", "Older day", "Thesis A", 10, 50),
        Entry("daily", "2026-10-06", "2026-10-06", "posts/2026-10-06.html", "Newer day", "Thesis B", 12, 60),
    ]


def test_should_list_index_entries_newest_first(config):
    html = render_index(entries(), config)
    assert html.index("Newer day") < html.index("Older day")


def test_should_link_index_entries_to_posts(config):
    assert 'href="posts/2026-10-06.html"' in render_index(entries(), config)


def test_should_link_index_to_feed(config):
    assert 'href="feed.xml"' in render_index(entries(), config)
