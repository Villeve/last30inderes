"""Generic Discourse forum API client with rate limiting."""

from __future__ import annotations

import time
import urllib.error
import urllib.parse
import urllib.request
import json
from dataclasses import dataclass
from typing import Any


@dataclass
class RateLimiter:
    """Simple token-bucket rate limiter."""

    max_rps: float = 10.0
    _last_request: float = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        min_interval = 1.0 / self.max_rps
        elapsed = now - self._last_request
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self._last_request = time.monotonic()


class DiscourseClient:
    """Client for any Discourse forum's public JSON API."""

    def __init__(
        self,
        base_url: str,
        forum_name: str = "discourse",
        rate_limit_rps: float = 10.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.forum_name = forum_name
        self._limiter = RateLimiter(max_rps=rate_limit_rps)

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        """Make a rate-limited GET request, returning parsed JSON."""
        url = f"{self.base_url}{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params, doseq=True)

        max_retries = 3
        for attempt in range(max_retries):
            self._limiter.wait()
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    return json.loads(resp.read().decode())
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    retry_after = int(e.headers.get("Retry-After", "3"))
                    time.sleep(retry_after)
                    continue
                raise
        raise RuntimeError(f"Rate limited after {max_retries} retries: {url}")

    def search(
        self, query: str, after_date: str, max_pages: int = 3
    ) -> dict[str, Any]:
        """Search the forum. Returns combined results across pages.

        Args:
            query: Search terms.
            after_date: ISO date string (YYYY-MM-DD) for filtering.
            max_pages: Maximum pages to fetch (50 posts per page).

        Returns:
            Dict with 'posts' and 'topics' lists of raw API dicts.
        """
        all_posts: list[dict] = []
        all_topics: list[dict] = []
        seen_topic_ids: set[int] = set()

        full_query = f"{query} after:{after_date}"

        for page in range(1, max_pages + 1):
            data = self._get("/search.json", {"q": full_query, "page": page})

            posts = data.get("posts", [])
            topics = data.get("topics", [])

            all_posts.extend(posts)
            for t in topics:
                if t["id"] not in seen_topic_ids:
                    seen_topic_ids.add(t["id"])
                    all_topics.append(t)

            # Stop if no more pages
            grouped = data.get("grouped_search_result", {})
            if not grouped.get("more_full_page_results"):
                break

        return {"posts": all_posts, "topics": all_topics}

    def fetch_topic_posts(self, topic_id: int, post_ids: list[int]) -> list[dict]:
        """Fetch full post content for specific posts in a topic."""
        if not post_ids:
            return []

        # Discourse accepts post_ids[] as query params
        data = self._get(
            f"/t/{topic_id}/posts.json", {"post_ids[]": post_ids}
        )
        return data.get("post_stream", {}).get("posts", [])

    def fetch_tag_topics(self, tag: str) -> list[dict]:
        """Fetch topics for a given tag."""
        data = self._get(f"/tag/{tag}.json")
        return data.get("topic_list", {}).get("topics", [])

    def fetch_topic(self, topic_id: int) -> dict:
        """Fetch a single topic's metadata and first posts."""
        return self._get(f"/t/{topic_id}.json")

    def check_tag_exists(self, tag: str) -> bool:
        """Check if a tag exists on this forum."""
        try:
            self._get(f"/tag/{tag}.json")
            return True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
            raise

    def post_url(self, topic_slug: str, topic_id: int, post_number: int = 1) -> str:
        """Build a direct URL to a specific post."""
        return f"{self.base_url}/t/{topic_slug}/{topic_id}/{post_number}"

    def topic_url(self, topic_slug: str, topic_id: int) -> str:
        """Build a URL to a topic."""
        return f"{self.base_url}/t/{topic_slug}/{topic_id}"
