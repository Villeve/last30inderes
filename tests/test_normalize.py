"""Tests for normalize module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from lib.normalize import strip_html, parse_datetime, _extract_tag_names


def test_strip_html_basic():
    assert strip_html("<p>Hello <b>world</b></p>") == "Hello world"


def test_strip_html_br():
    assert "line1\nline2" == strip_html("line1<br/>line2")


def test_strip_html_entities():
    assert strip_html("&amp; &lt; &gt;") == "& < >"


def test_strip_html_empty():
    assert strip_html("") == ""


def test_parse_datetime_iso():
    dt = parse_datetime("2026-03-01T12:00:00.000Z")
    assert dt.year == 2026
    assert dt.month == 3
    assert dt.day == 1


def test_extract_tag_names_strings():
    assert _extract_tag_names(["foo", "bar"]) == ["foo", "bar"]


def test_extract_tag_names_dicts():
    tags = [{"name": "nokia", "id": "nokia"}, {"name": "5G", "id": "5g"}]
    assert _extract_tag_names(tags) == ["nokia", "5G"]


def test_extract_tag_names_mixed():
    tags = ["plain", {"name": "dict-tag"}]
    assert _extract_tag_names(tags) == ["plain", "dict-tag"]


def test_extract_tag_names_empty():
    assert _extract_tag_names([]) == []
