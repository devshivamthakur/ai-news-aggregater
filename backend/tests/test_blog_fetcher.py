"""Tests for RSS blog feed parsing."""

from datetime import datetime, timezone
from time import struct_time

from app.fetchers.blog_fetcher import RSSScraper


def test_parse_published_time_from_feedparser_struct_time():
    entry = type("Entry", (), {})()
    entry.published_parsed = struct_time((2026, 9, 5, 5, 0, 0, 5, 248, 0))

    published_at = RSSScraper()._parse_published_time(entry)

    assert published_at == datetime(2026, 9, 5, 5, 0, tzinfo=timezone.utc)