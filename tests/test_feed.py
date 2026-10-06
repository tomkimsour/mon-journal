import xml.etree.ElementTree as ET

from briefing.feed import build_feed
from briefing.site import Entry


def entries(n=2):
    return [
        Entry("daily", f"2026-10-0{i}", f"2026-10-0{i}", f"posts/2026-10-0{i}.html", f"Day {i}", f"Thesis {i}", i, 10 * i)
        for i in range(1, n + 1)
    ]


def items(xml_text):
    return ET.fromstring(xml_text).findall("./channel/item")


def test_should_produce_parseable_rss(config):
    assert ET.fromstring(build_feed(entries(), config)).tag == "rss"


def test_should_emit_one_item_per_entry(config):
    assert len(items(build_feed(entries(), config))) == 2


def test_should_put_newest_entry_first(config):
    first = items(build_feed(entries(), config))[0]
    assert first.findtext("title") == "Day 2"


def test_should_use_absolute_links_from_base_url(config):
    first = items(build_feed(entries(), config))[0]
    assert first.findtext("link") == "https://example.org/briefing/posts/2026-10-02.html"


def test_should_cap_items_at_feed_max(config):
    config.site.feed_max_items = 3
    assert len(items(build_feed(entries(5), config))) == 3
