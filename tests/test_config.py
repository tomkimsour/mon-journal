from pathlib import Path

import pytest

from briefing.config import load_config

ROOT = Path(__file__).resolve().parents[1]

MINIMAL = """
[site]
title = "T"
subtitle = "S"
base_url = "https://example.org/b/"
language = "en"

[arxiv]
categories = ["cs.RO", "cs.AI"]

[[buckets]]
name = "Manipulation"
emoji = "🦾"
keywords = ["grasping"]

[[buckets]]
name = "Navigation"
emoji = "🧭"
keywords = ["slam"]
"""


def write(tmp_path, text):
    path = tmp_path / "config.toml"
    path.write_text(text, encoding="utf-8")
    return path


def test_should_load_categories_from_toml(tmp_path):
    assert load_config(write(tmp_path, MINIMAL)).categories == ["cs.RO", "cs.AI"]


def test_should_load_buckets_in_file_order(tmp_path):
    names = [b.name for b in load_config(write(tmp_path, MINIMAL)).buckets]
    assert names == ["Manipulation", "Navigation"]


def test_should_strip_trailing_slash_from_base_url(tmp_path):
    assert load_config(write(tmp_path, MINIMAL)).site.base_url == "https://example.org/b"


def test_should_default_feed_max_items(tmp_path):
    assert load_config(write(tmp_path, MINIMAL)).site.feed_max_items == 60


def test_should_reject_bucket_without_keywords(tmp_path):
    text = MINIMAL.replace('keywords = ["slam"]', "keywords = []")
    with pytest.raises(ValueError):
        load_config(write(tmp_path, text))


def test_should_reject_config_without_categories(tmp_path):
    text = MINIMAL.replace('categories = ["cs.RO", "cs.AI"]', "categories = []")
    with pytest.raises(ValueError):
        load_config(write(tmp_path, text))


def test_should_load_repository_config():
    assert "cs.RO" in load_config(ROOT / "config.toml").categories
