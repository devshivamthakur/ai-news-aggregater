"""Tests for the GitHub trending repository fetcher."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import requests as requests_module

from app.fetchers.github_fetcher import GitHubTrendingScraper, github_scraper


def _mock_response(payload: dict) -> MagicMock:
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.json.return_value = payload
    return response


def _repo_payload(overrides: dict | None = None) -> dict:
    payload = {
        "id": 1,
        "full_name": "openai/codex",
        "html_url": "https://github.com/openai/codex",
        "description": "CLI coding agent for real-world tasks",
        "stargazers_count": 12345,
        "language": "TypeScript",
        "topics": ["ai", "agents"],
        "created_at": "2026-10-15T10:30:00Z",
    }
    if overrides:
        payload.update(overrides)
    return payload


def test_fetch_trending_queries_each_topic_and_merges():
    ai_repo = _repo_payload()
    llm_repo = _repo_payload(
        {
            "id": 2,
            "full_name": "meta-ai/llm",
            "html_url": "https://github.com/meta-ai/llm",
            "stargazers_count": 9876,
        }
    )
    # Same repo appearing under both topics: should be deduped by repo id.
    duplicate = _repo_payload({"stargazers_count": 1})
    responses = [
        _mock_response({"items": [ai_repo, duplicate]}),
        _mock_response({"items": [llm_repo]}),
    ]
    with patch(
        "app.fetchers.github_fetcher.requests.get", side_effect=responses
    ) as mock_get:
        repos = github_scraper.fetch_trending(limit=5, lookback_days=7, topics=("ai", "llm"))

    assert len(repos) == 2
    assert [r.title for r in repos] == ["openai/codex", "meta-ai/llm"]
    # Star-sorted across merged topics.
    assert repos[0].stars == 12345

    # One request per topic, each with AND-safe qualifiers.
    assert mock_get.call_count == 2
    first_query = mock_get.call_args_list[0].kwargs["params"]["q"]
    assert first_query == "topic:ai created:>2026-10-14"
    second_query = mock_get.call_args_list[1].kwargs["params"]["q"]
    assert second_query == "topic:llm created:>2026-10-14"
    for call in mock_get.call_args_list:
        params = call.kwargs["params"]
        assert params["sort"] == "stars"
        assert params["order"] == "desc"
        assert params["per_page"] == 5


def test_fetch_trending_parses_repo_fields():
    response = _mock_response({"items": [_repo_payload()]})
    with patch("app.fetchers.github_fetcher.requests.get", return_value=response):
        repos = github_scraper.fetch_trending(limit=10, lookback_days=7)

    assert len(repos) == 1
    repo = repos[0]
    assert repo.title == "openai/codex"
    assert repo.url == "https://github.com/openai/codex"
    assert repo.source == "GitHub Trending"
    assert repo.stars == 12345
    assert repo.language == "TypeScript"
    assert repo.author == "openai"
    assert repo.published_at == datetime(2026, 10, 15, 10, 30, tzinfo=timezone.utc)
    assert repo.description is not None
    assert repo.topics == ["ai", "agents"]
    # Body includes description and metadata for the analyzer / digest.
    assert "CLI coding agent for real-world tasks" in repo.description
    assert "12,345 stars" in repo.description


def test_fetch_trending_uses_auth_token_when_provided():
    response = _mock_response({"items": []})
    with patch("app.fetchers.github_fetcher.requests.get", return_value=response) as mock_get:
        github_scraper.fetch_trending(token="test-token")

    headers = mock_get.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer test-token"


def test_fetch_trending_survives_total_failure():
    with patch(
        "app.fetchers.github_fetcher.requests.get",
        side_effect=requests_module.ConnectionError("network down"),
    ):
        repos = github_scraper.fetch_trending(topics=("ai",))

    # Failures return an empty list so one bad source never fails the run.
    assert repos == []


def test_fetch_trending_skips_items_without_url():
    response = _mock_response({"items": [_repo_payload({"html_url": None})]})
    with patch("app.fetchers.github_fetcher.requests.get", return_value=response):
        repos = GitHubTrendingScraper().fetch_trending()

    assert repos == []


def test_get_item_body_handles_repo_items():
    """Regression: RepoItem must not be treated like a video.

    Pydantic models raise AttributeError for missing attributes, so the
    pipeline must type-check instead of relying on or-chains that touch
    ``transcript`` on a RepoItem.
    """
    from datetime import datetime, timezone as tz

    from app.core.pipeline import _get_item_body
    from app.fetchers.models import BlogPost, ChannelVideo, RepoItem

    repo = RepoItem(
        title="owner/repo",
        url="https://github.com/owner/repo",
        description="A trending AI repo",
        published_at=datetime.now(tz.utc),
    )
    assert _get_item_body(repo) == "A trending AI repo"

    post = BlogPost(
        title="t",
        url="https://example.com/post",
        content="article body",
        published_at=datetime.now(tz.utc),
        source="s",
    )
    assert _get_item_body(post) == "article body"

    video = ChannelVideo(
        title="t",
        url="https://youtu.be/x",
        video_id="x",
        description="video description",
        transcript="video transcript",
        published_at=datetime.now(tz.utc),
    )
    assert _get_item_body(video) == "video transcript"

    video_no_transcript = video.model_copy(update={"transcript": None})
    assert _get_item_body(video_no_transcript) == "video description"
