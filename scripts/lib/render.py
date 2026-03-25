"""Render scored forum posts as structured markdown for Claude."""

from __future__ import annotations

from collections import Counter
from itertools import groupby

from .schema import ForumPost, TopicSummary


def truncate(text: str, max_len: int = 300) -> str:
    """Truncate text to max_len, adding ellipsis if needed."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rsplit(" ", 1)[0] + "…"


def render_markdown(
    posts: list[ForumPost],
    topics: list[TopicSummary],
    query: str,
    start_date: str,
    end_date: str,
    total_scanned: int,
    deep: bool = False,
) -> str:
    """Render posts into structured markdown output."""
    lines: list[str] = []

    topic_map = {t.id: t for t in topics}
    topic_count = len({p.topic_id for p in posts})

    lines.append(f"# Inderes-foorumin tutkimus: {query}")
    lines.append(f"**Aikaväli:** {start_date} – {end_date}")
    lines.append(
        f"**Analysoitu:** {total_scanned} viestiä, {topic_count} keskustelua"
    )
    lines.append("")

    # Group posts by topic, maintaining score order
    # First, collect topics in order of their best post's score
    topic_order: list[int] = []
    seen: set[int] = set()
    for p in posts:
        if p.topic_id not in seen:
            seen.add(p.topic_id)
            topic_order.append(p.topic_id)

    posts_by_topic: dict[int, list[ForumPost]] = {}
    for p in posts:
        posts_by_topic.setdefault(p.topic_id, []).append(p)

    lines.append("## Keskustelut\n")

    for tid in topic_order:
        topic = topic_map.get(tid)
        topic_posts = posts_by_topic.get(tid, [])
        if not topic_posts:
            continue

        # Topic header
        title = topic.title if topic else topic_posts[0].topic_title
        url = topic.url if topic else ""
        lines.append(f"### [{title}]({url})")

        if topic:
            meta_parts = []
            if topic.views:
                meta_parts.append(f"Katselut: {topic.views:,}")
            if topic.reply_count:
                meta_parts.append(f"Vastaukset: {topic.reply_count:,}")
            if topic.like_count:
                meta_parts.append(f"Tykkäykset: {topic.like_count:,}")
            if topic.tags:
                meta_parts.append(f"Tagit: {', '.join(topic.tags[:5])}")
            if meta_parts:
                lines.append(" | ".join(meta_parts))
        lines.append("")

        # Posts within topic
        for p in topic_posts:
            content = p.content if deep else truncate(p.content)
            date_str = p.created_at.strftime("%Y-%m-%d")
            likes_str = f" – {p.like_count} ♥" if p.like_count else ""
            lines.append(
                f"**{p.username}** (luottamus: {p.trust_level}) – "
                f"{date_str}{likes_str}"
            )
            lines.append(f"> {content}")
            lines.append(f"[Linkki]({p.url})")
            lines.append("")

        lines.append("---\n")

    # Stats section
    lines.append("## Tilastot")
    lines.append(f"- Keskusteluja: {topic_count}")
    lines.append(f"- Viestejä analysoitu: {total_scanned}")
    lines.append(f"- Viestejä näytetty: {len(posts)}")

    # Top contributors
    usernames = [p.username for p in posts]
    top_users = Counter(usernames).most_common(5)
    if top_users:
        users_str = ", ".join(f"{u} ({c})" for u, c in top_users)
        lines.append(f"- Aktiivisimmat: {users_str}")

    # Categories
    cats = Counter(
        topic_map[p.topic_id].category_name
        for p in posts
        if p.topic_id in topic_map and topic_map[p.topic_id].category_name
    )
    if cats:
        cats_str = ", ".join(f"{c} ({n})" for c, n in cats.most_common(5))
        lines.append(f"- Kategoriat: {cats_str}")

    lines.append("")
    return "\n".join(lines)
