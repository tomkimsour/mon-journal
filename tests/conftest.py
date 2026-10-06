import copy
from pathlib import Path

import pytest

from briefing.config import Bucket, Config, Site
from factories import make_paper

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def listing_html():
    return (FIXTURES / "cs_RO_new.html").read_text(encoding="utf-8")


@pytest.fixture
def config():
    return Config(
        site=Site(
            title="Test Briefing",
            subtitle="cs.RO · cs.AI",
            base_url="https://example.org/briefing",
            language="en",
            feed_max_items=60,
        ),
        categories=["cs.RO", "cs.AI"],
        buckets=[
            Bucket(name="Manipulation", emoji="🦾", keywords=["manipulation", "grasping", "dexterous"]),
            Bucket(name="Navigation", emoji="🧭", keywords=["navigation", "slam"]),
            Bucket(name="Generative", emoji="🎨", keywords=["gan", "diffusion"]),
        ],
    )


@pytest.fixture
def snapshot():
    return {
        "date": "2026-10-06",
        "categories": ["cs.RO", "cs.AI"],
        "total": 3,
        "selected": 2,
        "bucket_counts": {"Manipulation": 1, "Navigation": 1, "Generative": 0},
        "papers": [
            make_paper(
                "2610.00001",
                title="Dexterous <grasping> with tactile skins",
                abstract="Grippers slip on glossy objects.",
                bucket="Manipulation",
                badge="RO",
            ),
            make_paper(
                "2610.00002",
                title="Social navigation for quadrupeds",
                abstract="We study navigation.",
                subjects="Robotics (cs.RO); Artificial Intelligence (cs.AI)",
                bucket="Navigation",
                badge="RO/AI",
            ),
        ],
    }


@pytest.fixture
def briefing():
    return {
        "date": "2026-10-06",
        "headline": "Contact becomes a first-class control signal",
        "thesis": "Touch is moving from an auxiliary input to the variable that gates grasp decisions.",
        "clusters": [
            {
                "title": "Touch-gated grasping",
                "why": "Tactile skins decide when to commit to a grasp.",
                "paper_ids": ["2610.00001"],
                "confidence": "medium",
            }
        ],
        "insights": ["Grasp success now hinges on contact sensing rather than vision alone."],
        "must_read": [
            {
                "id": "2610.00001",
                "why": "Clearest evidence that tactile feedback changes grasp outcomes.",
                "key_idea": "Close the grasp loop on slip detection.",
                "evidence": "Abstract reports fewer slips on glossy objects.",
                "caveat": "Abstract-only reading; no real-robot numbers given.",
            }
        ],
        "summaries": {
            "2610.00001": {
                "problem": "Grippers slip on glossy objects",
                "method": "Tactile skin feeds a slip detector",
                "why": "Makes contact a control input",
            }
        },
    }


@pytest.fixture
def clone():
    return copy.deepcopy
