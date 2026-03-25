"""Normalize raw Discourse API responses into ForumPost objects."""

from __future__ import annotations

import html
import re
from datetime import datetime, timezone

from .discourse import DiscourseClient
from .schema import ForumPost, TopicSummary


def strip_html(text: str) -> str:
    """Strip HTML tags and decode entities to plain text."""
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"</?p>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    # Collapse multiple newlines/whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_tag_names(tags: list) -> list[str]:
    """Extract tag name strings from tags that may be dicts or strings."""
    result = []
    for t in tags:
        if isinstance(t, str):
            result.append(t)
        elif isinstance(t, dict):
            result.append(t.get("name", t.get("id", str(t))))
        else:
            result.append(str(t))
    return result


def parse_datetime(dt_str: str) -> datetime:
    """Parse Discourse datetime string to datetime object."""
    # Discourse uses ISO 8601 format
    dt_str = dt_str.replace("Z", "+00:00")
    return datetime.fromisoformat(dt_str)


def normalize_search_posts(
    raw_posts: list[dict],
    raw_topics: list[dict],
    client: DiscourseClient,
    source_forum: str = "inderes",
) -> tuple[list[ForumPost], list[TopicSummary]]:
    """Convert raw search API results into normalized objects.

    Args:
        raw_posts: Posts from search.json response.
        raw_topics: Topics from search.json response.
        client: DiscourseClient for URL building.
        source_forum: Forum identifier.

    Returns:
        Tuple of (ForumPost list, TopicSummary list).
    """
    # Build topic lookup
    topic_map: dict[int, dict] = {t["id"]: t for t in raw_topics}

    posts = []
    for rp in raw_posts:
        topic = topic_map.get(rp.get("topic_id", 0), {})
        topic_slug = topic.get("slug", "")
        topic_id = rp.get("topic_id", 0)
        post_number = rp.get("post_number", 1)

        posts.append(
            ForumPost(
                id=rp["id"],
                topic_id=topic_id,
                topic_title=topic.get("title", rp.get("name", "")),
                topic_slug=topic_slug,
                username=rp.get("username", ""),
                trust_level=rp.get("trust_level", 0),
                created_at=parse_datetime(rp["created_at"]),
                content=strip_html(rp.get("blurb", "")),
                content_html=rp.get("blurb", ""),
                url=client.post_url(topic_slug, topic_id, post_number),
                like_count=rp.get("like_count", 0),
                reply_count=0,  # Not available in search results
                reads=0,  # Not available in search results
                discourse_score=0.0,
                category_id=topic.get("category_id", 0),
                category_name="",  # Resolved later if needed
                tags=_extract_tag_names(topic.get("tags", [])),
                source_forum=source_forum,
            )
        )

    topics = []
    for rt in raw_topics:
        slug = rt.get("slug", "")
        tid = rt["id"]
        topics.append(
            TopicSummary(
                id=tid,
                title=rt.get("title", ""),
                slug=slug,
                url=client.topic_url(slug, tid),
                views=rt.get("views", 0),
                posts_count=rt.get("posts_count", 0),
                reply_count=rt.get("reply_count", 0),
                like_count=rt.get("like_count", 0),
                category_id=rt.get("category_id", 0),
                tags=_extract_tag_names(rt.get("tags", [])),
            )
        )

    return posts, topics


def enrich_posts(
    posts: list[ForumPost],
    client: DiscourseClient,
) -> list[ForumPost]:
    """Fetch full post content for a list of posts, replacing blurb data.

    Groups posts by topic_id and fetches in batches.
    """
    # Group post IDs by topic
    topic_posts: dict[int, list[int]] = {}
    post_lookup: dict[int, ForumPost] = {}
    for p in posts:
        topic_posts.setdefault(p.topic_id, []).append(p.id)
        post_lookup[p.id] = p

    for topic_id, post_ids in topic_posts.items():
        try:
            full_posts = client.fetch_topic_posts(topic_id, post_ids)
        except Exception:
            continue  # Skip on error, keep blurb data

        for fp in full_posts:
            pid = fp.get("id")
            if pid in post_lookup:
                post = post_lookup[pid]
                post.content_html = fp.get("cooked", post.content_html)
                post.content = strip_html(post.content_html)
                post.reads = fp.get("reads", 0)
                post.reply_count = fp.get("reply_count", 0)
                post.like_count = fp.get("like_count", post.like_count)
                post.discourse_score = fp.get("score", 0.0)

    return posts
