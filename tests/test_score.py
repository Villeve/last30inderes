"""Tests for score module."""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from lib.schema import ForumPost, TopicSummary
from lib.score import (
    engagement_score,
    recency_score,
    relevance_score,
    compute_scores,
    deduplicate_and_rank,
)


def _make_post(
    id=1,
    topic_id=1,
    like_count=0,
    reply_count=0,
    reads=0,
    trust_level=0,
    days_old=0,
    **kwargs,
):
    now = datetime.now(timezone.utc)
    return ForumPost(
        id=id,
        topic_id=topic_id,
        topic_title="Test",
        topic_slug="test",
        username="user",
        trust_level=trust_level,
        created_at=now - timedelta(days=days_old),
        content="test content",
        content_html="<p>test content</p>",
        url="https://example.com/t/test/1",
        like_count=like_count,
        reply_count=reply_count,
        reads=reads,
        **kwargs,
    )


def test_engagement_score_zero():
    post = _make_post(like_count=0, reply_count=0, reads=0)
    assert engagement_score(post) == 0.0


def test_engagement_score_high():
    post = _make_post(like_count=100, reply_count=50, reads=500, trust_level=4)
    score = engagement_score(post)
    assert score > 50


def test_recency_score_today():
    post = _make_post(days_old=0)
    score = recency_score(post, lookback_days=30)
    assert score > 95


def test_recency_score_old():
    post = _make_post(days_old=30)
    score = recency_score(post, lookback_days=30)
    assert score < 5


def test_recency_score_beyond_window():
    post = _make_post(days_old=60)
    score = recency_score(post, lookback_days=30)
    assert score == 0.0


def test_relevance_score_first():
    assert relevance_score(0) == 100.0


def test_relevance_score_50th():
    assert relevance_score(50) == 0.0


def test_deduplicate_and_rank_limits_per_topic():
    posts = [_make_post(id=i, topic_id=1, like_count=100 - i) for i in range(10)]
    posts = compute_scores(posts, [], lookback_days=30)
    result = deduplicate_and_rank(posts, max_per_topic=3, max_total=30)
    assert len(result) == 3


def test_deduplicate_and_rank_limits_total():
    posts = [_make_post(id=i, topic_id=i, like_count=10) for i in range(50)]
    posts = compute_scores(posts, [], lookback_days=30)
    result = deduplicate_and_rank(posts, max_per_topic=3, max_total=10)
    assert len(result) == 10


def test_compute_scores_assigns_values():
    posts = [_make_post(id=1, like_count=10)]
    scored = compute_scores(posts, [], lookback_days=30)
    assert scored[0].composite_score > 0
