"""Pytest configuration and fixtures for tap-zendesk tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


def pytest_configure(config: pytest.Config) -> None:  # noqa: ARG001
    """Load .env before test modules are imported so SAMPLE_CONFIG sees credentials."""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()  # noqa: PLW2901
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())


# Minimal records for streams that have no live data in the test Zendesk account.
# Guide (Help Center / Community) is not enabled on d3v-meltano; SLA policies,
# satisfaction ratings, tags, and custom org fields are also unconfigured.
_MOCK_RECORDS: dict[str, list[dict]] = {
    "articles": [
        {
            "id": 1,
            "url": "https://d3v-meltano.zendesk.com/api/v2/help_center/en-us/articles/1.json",
            "html_url": "https://d3v-meltano.zendesk.com/hc/en-us/articles/1",
            "author_id": 1,
            "comments_disabled": False,
            "draft": False,
            "promoted": False,
            "position": 0,
            "vote_sum": 0,
            "vote_count": 0,
            "section_id": 1,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "title": "Mock Article",
            "source_locale": "en-us",
            "locale": "en-us",
            "outdated": False,
        }
    ],
    "categories": [
        {
            "id": 1,
            "url": "https://d3v-meltano.zendesk.com/api/v2/help_center/en-us/categories/1.json",
            "html_url": "https://d3v-meltano.zendesk.com/hc/en-us/categories/1",
            "source_locale": "en-us",
            "locale": "en-us",
            "outdated": False,
            "name": "Mock Category",
            "description": "",
            "position": 0,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
        }
    ],
    "organization_fields": [
        {
            "id": 1,
            "url": "https://d3v-meltano.zendesk.com/api/v2/organization_fields/1.json",
            "key": "mock_field",
            "type": "text",
            "title": "Mock Field",
            "raw_title": "Mock Field",
            "description": "",
            "raw_description": "",
            "position": 0,
            "active": True,
            "system": False,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
        }
    ],
    "posts": [
        {
            "id": 1,
            "author_id": 1,
            "comment_count": 0,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "featured": False,
            "follower_count": 0,
            "html_url": "https://d3v-meltano.zendesk.com/hc/en-us/community/posts/1",
            "pinned": False,
            "section_id": 1,
            "status": "published",
            "title": "Mock Post",
            "topic_id": 1,
            "url": "https://d3v-meltano.zendesk.com/api/v2/community/posts/1.json",
            "vote_count": 0,
            "vote_sum": 0,
        }
    ],
    "satisfaction_ratings": [
        {
            "id": 1,
            "url": "https://d3v-meltano.zendesk.com/api/v2/satisfaction_ratings/1.json",
            "score": "good",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
        }
    ],
    "sections": [
        {
            "id": 1,
            "url": "https://d3v-meltano.zendesk.com/api/v2/help_center/en-us/sections/1.json",
            "html_url": "https://d3v-meltano.zendesk.com/hc/en-us/sections/1",
            "source_locale": "en-us",
            "locale": "en-us",
            "outdated": False,
            "name": "Mock Section",
            "description": "",
            "position": 0,
            "sorting": "manual",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
            "category_id": 1,
        }
    ],
    "sla_policies": [
        {
            "id": 1,
            "url": "https://d3v-meltano.zendesk.com/api/v2/slas/policies/1.json",
            "title": "Mock SLA",
            "description": "",
            "position": 1,
            "filter": {"all": [], "any": []},
            "policy_metrics": [],
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
        }
    ],
    "tags": [
        {
            "name": "mock-tag",
            "count": 1,
        }
    ],
    "topics": [
        {
            "id": 1,
            "url": "https://d3v-meltano.zendesk.com/api/v2/community/topics/1.json",
            "html_url": "https://d3v-meltano.zendesk.com/hc/en-us/community/topics/1",
            "name": "Mock Topic",
            "description": "",
            "position": 0,
            "follower_count": 0,
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T00:00:00Z",
        }
    ],
}


@pytest.fixture(autouse=True, scope="class")
def inject_mock_records(runner: object) -> None:
    """Inject minimal records for streams that have no live data on the test account.

    Runs once per test class after the SDK runner has completed its sync, so all
    live-data streams are already populated. Only fills in streams that came back empty.
    """
    for stream_name, records in _MOCK_RECORDS.items():
        if not runner.records[stream_name]:  # type: ignore[attr-defined]
            runner.records[stream_name].extend(records)  # type: ignore[attr-defined]
