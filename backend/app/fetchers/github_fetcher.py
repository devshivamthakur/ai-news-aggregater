"""Fetch trending AI repositories via the GitHub Search API.

GitHub does not offer an official "trending" endpoint, so we approximate it
with the Search API: repositories created in the last N days that carry
AI-related topics, ordered by stars. This mirrors what the trending page
surfaces and behaves well for a once-a-day fetch.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import requests

from app.fetchers.base import DEFAULT_HEADERS
from app.fetchers.models import RepoItem
from app.logging.logger import logger

GITHUB_API_BASE = "https://api.github.com"

DEFAULT_TOPICS: tuple[str, ...] = (
    "ai",
    "llm",
    "machine-learning",
    "deep-learning",
    "agents",
)


class GitHubTrendingScraper:
    """Fetch trending AI repositories from the GitHub Search API."""

    def fetch_trending(
        self,
        *,
        limit: int = 15,
        lookback_days: int = 7,
        topics: tuple[str, ...] | None = None,
        token: str | None = None,
    ) -> list[RepoItem]:
        """Fetch recently-created AI repos sorted by stars.

        Args:
            limit: Maximum number of repositories to return.
            lookback_days: Only consider repos created in the last N days.
            topics: AI topic qualifiers for the search query. ``None`` uses
                the built-in defaults.
            token: Optional GitHub personal access token for higher rate
                limits (anonymous allows 10 search requests per minute).

        Returns:
            List of ``RepoItem`` models (empty list on failure, mirroring the
            RSS fetcher's behaviour so one bad source never fails the run).
        """
        selected_topics = topics or DEFAULT_TOPICS
        since = datetime.now(timezone.utc) - timedelta(days=lookback_days)
        since_date = since.strftime("%Y-%m-%d")

        headers = dict(DEFAULT_HEADERS)
        headers["Accept"] = "application/vnd.github+json"
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # GitHub's repository Search API does NOT support OR-grouped topic
        # qualifiers (it fails validation or silently matches nothing), so we
        # run one query per topic and merge the results below.
        base_params: dict[str, Any] = {
            "sort": "stars",
            "order": "desc",
            "page": 1,
        }

        logger.info(
            "Fetching GitHub trending AI repos: since=%s topics=%s limit=%d",
            since_date,
            selected_topics,
            limit,
        )

        repos: dict[str, RepoItem] = {}
        search_failures = 0
        for topic in selected_topics:
            params = dict(base_params)
            params["q"] = f"topic:{topic} created:>{since_date}"
            params["per_page"] = limit
            try:
                response = requests.get(
                    f"{GITHUB_API_BASE}/search/repositories",
                    params=params,
                    headers=headers,
                    timeout=20,
                )
                response.raise_for_status()
                payload = response.json()
            except (requests.RequestException, ValueError) as e:
                search_failures += 1
                logger.error("Failed to fetch GitHub trending repos for topic %s: %s", topic, e)
                continue

            for repo in payload.get("items", []):
                repo_id = repo.get("id")
                if not repo_id:
                    continue
                item = self._to_repo_item(repo)
                if item is None:
                    continue
                # Keep the highest-star entry per repo when it appears in
                # multiple topic result sets (items are keyed by repo id).
                existing = repos.get(str(repo_id))
                if existing is None or item.stars > existing.stars:
                    # Preserve the first-seen source so multiple GitHub
                    # sources don't clobber each other.
                    if existing is not None:
                        item = item.model_copy(update={"source": existing.source})
                    repos[str(repo_id)] = item

        trending = sorted(repos.values(), key=lambda item: item.stars, reverse=True)
        if search_failures and not trending:
            logger.error("All GitHub trending queries failed; returning no repos")
            return []

        logger.info("Fetched %d trending AI repos from GitHub", len(trending))
        return trending[:limit]

    def _to_repo_item(self, repo: dict) -> RepoItem | None:
        """Convert a GitHub API repo object into a ``RepoItem``."""
        html_url = repo.get("html_url") or ""
        if not html_url:
            return None

        full_name = repo.get("full_name") or html_url.rstrip("/").split("/")[-1]
        description = (repo.get("description") or "").strip()

        stars = repo.get("stargazers_count") or 0
        language = repo.get("language")
        topics = [
            f"#{t}"
            for t in repo.get("topics") or []
            if t not in ("", None)
        ]

        # Compose a single body string so the analyzer and digest path can use
        # it directly, mirroring how BlogPost.content is consumed downstream.
        meta_parts = []
        if stars:
            meta_parts.append(f"{stars:,} stars")
        if language:
            meta_parts.append(f"Language: {language}")
        if topics:
            meta_parts.append(" ".join(topics[:8]))
        body = description or f"{full_name} is trending on GitHub"
        if meta_parts:
            body = f"{body}\n\n" + " · ".join(meta_parts)

        created_at = repo.get("created_at")
        published_at = self._parse_datetime(created_at)

        return RepoItem(
            title=full_name,
            url=html_url,
            description=body,
            published_at=published_at,
            source="GitHub Trending",
            stars=int(stars or 0),
            language=language,
            topics=[t.lstrip("#") for t in topics],
            author=full_name.split("/")[0] if "/" in full_name else None,
        )

    def _parse_datetime(self, raw: str | None) -> datetime:
        """Parse an ISO-8601 GitHub timestamp, falling back to now."""
        if raw:
            try:
                return datetime.fromisoformat(
                    raw.replace("Z", "+00:00")
                )
            except (TypeError, ValueError):
                pass
        return datetime.now(timezone.utc)


github_scraper = GitHubTrendingScraper()
