import pytest

from briefing.classify import assign_bucket, badge, build_snapshot
from factories import make_listing, make_paper


def test_should_assign_bucket_with_most_keyword_hits(config):
    paper = make_paper("1", title="Dexterous manipulation", abstract="no other match")
    assert assign_bucket(paper, config.buckets) == "Manipulation"


def test_should_return_empty_bucket_when_no_keyword_matches(config):
    paper = make_paper("1", title="Protein folding", abstract="Amino acids.")
    assert assign_bucket(paper, config.buckets) == ""


def test_should_not_match_keyword_inside_longer_word(config):
    paper = make_paper("1", title="Organization of team workflows")
    assert assign_bucket(paper, config.buckets) == ""


def test_should_match_plural_form_of_keyword(config):
    paper = make_paper("1", title="GANs for terrain synthesis")
    assert assign_bucket(paper, config.buckets) == "Generative"


def test_should_match_keywords_case_insensitively(config):
    paper = make_paper("1", title="Visual SLAM in forests")
    assert assign_bucket(paper, config.buckets) == "Navigation"


def test_should_weight_title_hits_above_abstract_hits(config):
    paper = make_paper("1", title="Navigation in clutter", abstract="Uses grasping.")
    assert assign_bucket(paper, config.buckets) == "Navigation"


def test_should_put_primary_category_first_in_badge(config):
    paper = make_paper(
        "1",
        subjects="Artificial Intelligence (cs.AI); Robotics (cs.RO)",
        primary_cat="cs.AI",
    )
    assert badge(paper, config.categories) == "AI/RO"


def test_should_badge_only_configured_categories(config):
    paper = make_paper("1", subjects="Robotics (cs.RO); Computer Vision (cs.CV)")
    assert badge(paper, config.categories) == "RO"


def test_should_badge_cross_list_by_configured_category(config):
    paper = make_paper(
        "1",
        subjects="Soft Condensed Matter (cond-mat.soft); Robotics (cs.RO)",
        primary_cat="cond-mat.soft",
    )
    assert badge(paper, config.categories) == "RO"


def test_should_raise_when_listings_have_different_dates(config):
    listings = [
        make_listing("cs.RO", [], date="2026-10-06"),
        make_listing("cs.AI", [], date="2026-10-05"),
    ]
    with pytest.raises(ValueError):
        build_snapshot(listings, config)


def test_should_record_snapshot_date(config):
    snap = build_snapshot([make_listing("cs.RO", [])], config)
    assert snap["date"] == "2026-10-06"


def test_should_drop_replacement_papers(config):
    papers = [make_paper("1", title="Grasping", section="replace")]
    snap = build_snapshot([make_listing("cs.RO", papers)], config)
    assert snap["papers"] == []


def test_should_deduplicate_papers_listed_in_several_categories(config):
    paper = make_paper("1", title="Grasping")
    cross = make_paper("1", title="Grasping", section="cross")
    snap = build_snapshot(
        [make_listing("cs.RO", [paper]), make_listing("cs.AI", [cross])], config
    )
    assert len(snap["papers"]) == 1


def test_should_keep_only_bucketed_papers(config):
    papers = [make_paper("1", title="Grasping"), make_paper("2", title="Protein folding")]
    snap = build_snapshot([make_listing("cs.RO", papers)], config)
    assert [p["arxiv_id"] for p in snap["papers"]] == ["1"]


def test_should_count_all_unique_new_papers_in_total(config):
    papers = [make_paper("1", title="Grasping"), make_paper("2", title="Protein folding")]
    snap = build_snapshot([make_listing("cs.RO", papers)], config)
    assert snap["total"] == 2


def test_should_count_papers_per_bucket(config):
    papers = [make_paper("1", title="Grasping"), make_paper("2", title="SLAM")]
    snap = build_snapshot([make_listing("cs.RO", papers)], config)
    assert snap["bucket_counts"] == {"Manipulation": 1, "Navigation": 1, "Generative": 0}


def test_should_attach_bucket_and_badge_to_selected_papers(config):
    snap = build_snapshot([make_listing("cs.RO", [make_paper("1", title="Grasping")])], config)
    paper = snap["papers"][0]
    assert (paper["bucket"], paper["badge"]) == ("Manipulation", "RO")
