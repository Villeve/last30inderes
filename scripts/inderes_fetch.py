#!/usr/bin/env python3
"""Fetch and analyze Inderes forum discussions about a topic.

Usage:
    python3 scripts/inderes_fetch.py "Nokia" --days 30
    python3 scripts/inderes_fetch.py "osingot" --days 7 --deep
    python3 scripts/inderes_fetch.py "asuntomarkkina" --category talous-ja-markkinat
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add parent dir to path so lib imports work when run directly
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.discourse import DiscourseClient
from lib.normalize import enrich_posts, normalize_search_posts
from lib.render import render_markdown
from lib.score import compute_scores, deduplicate_and_rank

INDERES_FORUM_URL = "https://forum.inderes.com"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Hae Inderes-foorumin keskusteluja aiheesta."
    )
    parser.add_argument("topic", help="Haettava aihe (esim. Nokia, osingot)")
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Kuinka monen päivän ajalta haetaan (oletus: 30)",
    )
    parser.add_argument(
        "--deep",
        action="store_true",
        help="Hae viestien koko sisältö (hitaampi)",
    )
    parser.add_argument(
        "--category",
        help="Rajaa kategoriaan (esim. osakkeet, sijoittaminen)",
    )
    parser.add_argument(
        "--max-posts",
        type=int,
        default=30,
        help="Näytettävien viestien enimmäismäärä (oletus: 30)",
    )
    parser.add_argument(
        "--max-per-topic",
        type=int,
        default=3,
        help="Viestejä per keskustelu enintään (oletus: 3)",
    )

    args = parser.parse_args()

    client = DiscourseClient(
        base_url=INDERES_FORUM_URL,
        forum_name="inderes",
    )

    now = datetime.now(timezone.utc)
    after_date = (now - timedelta(days=args.days)).strftime("%Y-%m-%d")
    end_date = now.strftime("%Y-%m-%d")

    # Build search query
    query = args.topic
    if args.category:
        query += f" ##{args.category}"

    print(f"Haetaan: '{args.topic}' ({after_date} – {end_date})...", file=sys.stderr)

    # Phase 1: Discovery via search
    raw = client.search(query, after_date)
    posts, topics = normalize_search_posts(
        raw["posts"], raw["topics"], client, source_forum="inderes"
    )
    total_scanned = len(posts)

    print(
        f"Löytyi {len(posts)} viestiä, {len(topics)} keskustelua.", file=sys.stderr
    )

    # Supplemental: tag-based discovery
    tag_name = args.topic.lower().replace(" ", "-")
    try:
        if client.check_tag_exists(tag_name):
            tag_topics = client.fetch_tag_topics(tag_name)
            existing_ids = {t.id for t in topics}
            new_count = 0
            for tt in tag_topics:
                if tt["id"] not in existing_ids:
                    existing_ids.add(tt["id"])
                    new_count += 1
            if new_count:
                print(
                    f"Tagista '{tag_name}' löytyi {new_count} lisäkeskustelua.",
                    file=sys.stderr,
                )
    except Exception:
        pass  # Tag lookup is best-effort

    if not posts:
        print(f"Ei tuloksia haulle '{args.topic}'.", file=sys.stderr)
        print(f"# Inderes-foorumin tutkimus: {args.topic}")
        print(f"\nEi keskusteluja aiheesta viimeisen {args.days} päivän ajalta.")
        return

    # Phase 2: Scoring
    posts = compute_scores(posts, topics, lookback_days=args.days)

    # Phase 3: Enrichment (deep mode fetches full content for top posts)
    if args.deep:
        # Only enrich top candidates to save API calls
        posts.sort(key=lambda p: p.composite_score, reverse=True)
        top_posts = posts[: args.max_posts * 2]  # Enrich more than we show
        print(
            f"Haetaan {len(top_posts)} viestin koko sisältö...", file=sys.stderr
        )
        top_posts = enrich_posts(top_posts, client)
        # Re-score after enrichment (engagement data may have changed)
        top_posts = compute_scores(top_posts, topics, lookback_days=args.days)
        posts = top_posts

    # Phase 4: Deduplicate and rank
    ranked = deduplicate_and_rank(
        posts,
        max_per_topic=args.max_per_topic,
        max_total=args.max_posts,
    )

    # Phase 5: Render
    output = render_markdown(
        ranked,
        topics,
        query=args.topic,
        start_date=after_date,
        end_date=end_date,
        total_scanned=total_scanned,
        deep=args.deep,
    )

    print(output)


if __name__ == "__main__":
    main()
