"""Tests for render module."""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from lib.render import truncate, render_markdown
from lib.schema import ForumPost, TopicSummary


def test_truncate_short():
    assert truncate("hello", 10) == "hello"


def test_truncate_long():
    text = "word " * 100
    result = truncate(text, 20)
    assert len(result) <= 20
    assert result.endswith("…")


def test_render_markdown_basic():
    post = ForumPost(
        id=1,
        topic_id=10,
        topic_title="Test Topic",
        topic_slug="test-topic",
        username="testuser",
        trust_level=2,
        created_at=datetime(2026, 3, 1, tzinfo=timezone.utc),
        content="This is test content",
        content_html="<p>This is test content</p>",
        url="https://forum.inderes.com/t/test-topic/10/1",
        like_count=5,
        composite_score=50.0,
    )
    topic = TopicSummary(
        id=10,
        title="Test Topic",
        slug="test-topic",
        url="https://forum.inderes.com/t/test-topic/10",
        views=100,
        reply_count=10,
        like_count=20,
    )

    output = render_markdown(
        [post], [topic], query="test", start_date="2026-02-01",
        end_date="2026-03-01", total_scanned=1,
    )

    assert "# Inderes-foorumin tutkimus: test" in output
    assert "Test Topic" in output
    assert "testuser" in output
    assert "5 ♥" in output
    assert "[Linkki]" in output
    assert "Tilastot" in output


def test_render_empty():
    output = render_markdown(
        [], [], query="empty", start_date="2026-02-01",
        end_date="2026-03-01", total_scanned=0,
    )
    assert "empty" in output
    assert "0" in output
