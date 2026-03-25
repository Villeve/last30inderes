"""Scoring and ranking logic for forum posts."""

from __future__ import annotations

import math
from datetime import datetime, timezone

from .schema import ForumPost, TopicSummary


def engagement_score(post: ForumPost) -> float:
    """Score based on likes, replies, reads, and trust level (0-100)."""
    raw = (
        0.45 * math.log1p(post.like_count)
        + 0.25 * math.log1p(post.reply_count)
        + 0.20 * math.log1p(post.reads)
        + 0.10 * math.log1p(post.trust_level)
    )
    # Normalize: log1p(1000) ≈ 6.9, so max raw ≈ 6.9
    return min(100.0, raw * 14.5)


def recency_score(post: ForumPost, lookback_days: int = 30) -> float:
    """Linear decay from 100 (today) to 0 (lookback_days ago)."""
    now = datetime.now(timezone.utc)
    age_days = (now - post.created_at).total_seconds() / 86400
    return max(0.0, 100.0 * (1.0 - age_days / lookback_days))


def relevance_score(rank_position: int) -> float:
    """Score based on search result position (0-100)."""
    return max(0.0, 100.0 - rank_position * 2.0)


def topic_bonus(post: ForumPost, topics: list[TopicSummary]) -> float:
    """Bonus multiplier for posts in high-engagement topics."""
    topic_map = {t.id: t for t in topics}
    topic = topic_map.get(post.topic_id)
    if not topic:
        return 1.0
    # High-view topics get up to 15% bonus
    view_bonus = min(0.15, math.log1p(topic.views) / 80.0)
    return 1.0 + view_bonus


def compute_scores(
    posts: list[ForumPost],
    topics: list[TopicSummary],
    lookback_days: int = 30,
) -> list[ForumPost]:
    """Compute composite score for each post.

    Weights: relevance 45%, engagement 30%, recency 25%.
    """
    for rank, post in enumerate(posts):
        eng = engagement_score(post)
        rec = recency_score(post, lookback_days)
        rel = relevance_score(rank)
        bonus = topic_bonus(post, topics)

        post.composite_score = (0.45 * rel + 0.30 * eng + 0.25 * rec) * bonus

    return posts


def deduplicate_and_rank(
    posts: list[ForumPost],
    max_per_topic: int = 3,
    max_total: int = 30,
) -> list[ForumPost]:
    """Deduplicate posts per topic and return top results."""
    # Sort by composite score descending
    posts.sort(key=lambda p: p.composite_score, reverse=True)

    topic_counts: dict[int, int] = {}
    result: list[ForumPost] = []

    for post in posts:
        count = topic_counts.get(post.topic_id, 0)
        if count >= max_per_topic:
            continue
        topic_counts[post.topic_id] = count + 1
        result.append(post)
        if len(result) >= max_total:
            break

    return result
