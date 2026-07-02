"""Unit tests for tap-zendesk rate-limit handling (no network required)."""

from __future__ import annotations

import typing as t

import pytest

from tap_zendesk.streams import GroupsStream
from tap_zendesk.tap import TapZendesk

CONFIG = {
    "subdomain": "d3v-meltano",
    "email": "test@example.com",
    "api_token": "token",
    "start_date": "2020-01-01T00:00:00Z",
}


class _FakeResponse:
    def __init__(self, status_code: int, headers: dict | None = None) -> None:
        self.status_code = status_code
        self.headers = headers or {}


class _FakeError(Exception):
    def __init__(self, response: _FakeResponse) -> None:
        self.response = response


def _stream() -> GroupsStream:
    tap = TapZendesk(config=CONFIG, validate_config=False)
    return GroupsStream(tap=tap)


def _wait_for(stream: GroupsStream, exc: Exception) -> float:
    gen = stream.backoff_wait_generator()
    next(gen)  # prime the generator up to the first (bare) yield
    return gen.send(exc)  # type: ignore[arg-type]


class TestRateLimitBackoff:
    """Offline unit tests for the Retry-After-aware backoff on ZendeskStream."""

    @pytest.fixture(autouse=True)
    def inject_mock_records(self) -> t.Iterator[None]:
        """Shadow the live-suite autouse fixture (needs a real sync runner)."""
        yield

    def test_backoff_max_tries_increased(self) -> None:
        assert _stream().backoff_max_tries() == 10

    def test_backoff_honors_retry_after_header(self) -> None:
        exc = _FakeError(_FakeResponse(429, {"Retry-After": "93"}))
        assert _wait_for(_stream(), exc) == 93.0

    def test_backoff_429_without_header_waits_full_minute(self) -> None:
        exc = _FakeError(_FakeResponse(429, {}))
        assert _wait_for(_stream(), exc) == 60.0

    def test_backoff_other_retriable_errors_short_wait(self) -> None:
        exc = _FakeError(_FakeResponse(503, {}))
        assert _wait_for(_stream(), exc) == 5.0
