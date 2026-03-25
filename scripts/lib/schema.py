"""Data models for forum post representation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ForumPost:
    """Unified representation of a forum post, source-agnostic."""

    id: int
    topic_id: int
    topic_title: str
    topic_slug: str
    username: str
    trust_level: int  # 0-4 for Discourse
    created_at: datetime
    content: str  # Plain text (HTML stripped)
    content_html: str  # Original HTML
    url: str  # Direct link to post
    like_count: int = 0
    reply_count: int = 0
    reads: int = 0
    discourse_score: float = 0.0  # Discourse's internal score
    category_id: int = 0
    category_name: str = ""
    tags: list[str] = field(default_factory=list)
    source_forum: str = "inderes"

    # Computed scoring fields (set by score.py)
    composite_score: float = 0.0


@dataclass
class TopicSummary:
    """Summary metadata for a discussion topic."""

    id: int
    title: str
    slug: str
    url: str
    views: int = 0
    posts_count: int = 0
    reply_count: int = 0
    like_count: int = 0
    category_id: int = 0
    category_name: str = ""
    tags: list[str] = field(default_factory=list)


@dataclass
class SearchResult:
    """Container for a full search result from one forum."""

    posts: list[ForumPost]
    topics: list[TopicSummary]
    total_posts_scanned: int = 0
    source_forum: str = "inderes"
