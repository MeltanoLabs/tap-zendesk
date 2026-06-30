"""REST client and base stream classes for tap-zendesk."""

from __future__ import annotations

import typing as t
from datetime import datetime
from functools import cached_property
from http import HTTPStatus
from urllib.parse import parse_qs, urlparse

from singer_sdk.authenticators import BasicAuthenticator, BearerTokenAuthenticator
from singer_sdk.pagination import BaseAPIPaginator
from singer_sdk.streams import RESTStream

from tap_zendesk.auth import ZendeskOAuthAuthenticator

if t.TYPE_CHECKING:
    import requests
    from singer_sdk.helpers.types import Context


class ZendeskOffsetPaginator(BaseAPIPaginator):
    """Offset/page-number paginator for older Zendesk endpoints.

    Used by endpoints that reject cursor params (e.g. custom_roles, schedules,
    sla_policies) and expect page=<integer>&per_page=<integer> instead.
    """

    def get_next(self, response: requests.Response) -> int | None:  # noqa: D102
        if response.json().get("next_page"):
            return self.current_value + 1
        return None


class ZendeskCursorPaginator(BaseAPIPaginator):
    """Cursor paginator for standard Zendesk endpoints.

    Reads meta.has_more / meta.after_cursor from the response body.
    """

    def get_next(self, response: requests.Response) -> str | None:  # noqa: D102
        data = response.json()
        meta = data.get("meta", {})
        if meta.get("has_more"):
            return meta.get("after_cursor")
        return None


class ZendeskNextPagePaginator(BaseAPIPaginator):
    """next_page URL paginator for time-based incremental export (users, organizations).

    Zendesk returns next_page even after catching up to now (it's the resume cursor
    for the next sync). Stop when count < per_page — a partial page means the current
    window is fully drained and the next_page is a future-facing bookmark, not more
    data.
    """

    def __init__(self, start_value: None, per_page: int = 1000) -> None:  # noqa: D107
        super().__init__(start_value)
        self._per_page = per_page

    def get_next(self, response: requests.Response) -> str | None:  # noqa: D102
        data = response.json()
        if data.get("count", 0) < self._per_page:
            return None
        return data.get("next_page")


class ZendeskCursorIncrementalPaginator(BaseAPIPaginator):
    """Cursor paginator for cursor-based incremental export (tickets).

    Reads after_cursor and terminates when end_of_stream is true.
    """

    def get_next(self, response: requests.Response) -> str | None:  # noqa: D102
        data = response.json()
        if data.get("end_of_stream"):
            return None
        return data.get("after_cursor")


class ZendeskStream(RESTStream):
    """Base stream for standard Zendesk Support API cursor-paginated endpoints."""

    @property
    def url_base(self) -> str:  # noqa: D102
        return f"https://{self.config['subdomain']}.zendesk.com/api/v2"

    @cached_property
    def authenticator(self) -> t.Callable:  # noqa: D102
        if self.config.get("api_token") and self.config.get("email"):
            return BasicAuthenticator(
                self,
                username=f"{self.config['email']}/token",
                password=self.config["api_token"],
            )
        creds = self.config.get("oauth_credentials", {})
        if creds.get("refresh_token"):
            refresh_url = creds.get("refresh_proxy_url") or (
                f"https://{self.config['subdomain']}.zendesk.com/oauth/tokens"
            )
            return ZendeskOAuthAuthenticator(self, auth_endpoint=refresh_url)
        access_token = creds.get("access_token") or self.config.get("access_token", "")
        return BearerTokenAuthenticator(self, token=access_token)

    @property
    def http_headers(self) -> dict:  # noqa: D102
        return {"Content-Type": "application/json"}

    def get_new_paginator(self) -> BaseAPIPaginator:  # noqa: D102
        return ZendeskCursorPaginator(None)

    def get_url_params(  # noqa: D102
        self,
        context: Context | None,  # noqa: ARG002
        next_page_token: str | None,
    ) -> dict[str, t.Any]:
        params: dict[str, t.Any] = {"page[size]": 100}
        if next_page_token:
            params["page[after]"] = next_page_token
        return params


class ZendeskOptionalFeatureStream(ZendeskStream):
    """Base for Zendesk features that may not be available on all plans.

    Returns empty records on 403 (plan restriction) or 404 (feature not enabled)
    rather than raising a fatal error, so the tap continues syncing other streams.
    """

    def validate_response(self, response: requests.Response) -> None:  # noqa: D102
        if response.status_code in (HTTPStatus.NOT_FOUND, HTTPStatus.FORBIDDEN):
            self.logger.warning(
                "'%s' returned %s — this feature may not be available on your"
                " Zendesk plan.",
                self.name,
                response.status_code,
            )
        else:
            super().validate_response(response)

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:  # noqa: D102
        if response.status_code in (HTTPStatus.NOT_FOUND, HTTPStatus.FORBIDDEN):
            return []
        return super().parse_response(response)


class ZendeskIncrementalExportStream(ZendeskStream):
    """Base for time-based incremental export streams (users, organizations).

    Uses /api/v2/incremental/{resource}.json?start_time=<unix_ts>.
    Paginates via next_page URL; state stored as replication_key (updated_at).
    Subclasses may override _per_page to match the endpoint's max page size.
    """

    replication_method = "INCREMENTAL"
    replication_key = "updated_at"
    _per_page: int = 1000

    def get_new_paginator(self) -> ZendeskNextPagePaginator:  # noqa: D102
        return ZendeskNextPagePaginator(None, per_page=self._per_page)

    def get_url_params(  # noqa: D102
        self,
        context: Context | None,
        next_page_token: str | None,
    ) -> dict[str, t.Any]:
        if next_page_token:
            parsed = urlparse(next_page_token)
            return {k: v[0] for k, v in parse_qs(parsed.query).items()}
        start = self.get_starting_replication_key_value(context)
        raw = start or self.config.get("start_date", "2020-01-01T00:00:00Z")
        start_dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return {"start_time": int(start_dt.timestamp()), "per_page": self._per_page}


class ZendeskOffsetStream(ZendeskStream):
    """Base for Zendesk endpoints that use offset (page=<int>) pagination.

    Used by endpoints that reject cursor params — e.g. custom_roles, schedules,
    sla_policies. The response's next_page field is used to detect whether more
    pages exist; the page number is incremented on each call.
    """

    def get_new_paginator(self) -> ZendeskOffsetPaginator:  # noqa: D102
        return ZendeskOffsetPaginator(1)

    def get_url_params(  # noqa: D102
        self,
        context: Context | None,  # noqa: ARG002
        next_page_token: int | str | None,
    ) -> dict[str, t.Any]:
        params: dict[str, t.Any] = {"per_page": 100}
        if next_page_token:
            params["page"] = next_page_token
        return params


class ZendeskCursorIncrementalExportStream(ZendeskStream):
    """Base for cursor-based incremental export streams (tickets).

    Uses /api/v2/incremental/tickets/cursor.json.
    First page uses start_time; subsequent pages use cursor param.
    Terminates when end_of_stream is true.
    """

    replication_method = "INCREMENTAL"
    replication_key = "updated_at"

    def get_new_paginator(self) -> ZendeskCursorIncrementalPaginator:  # noqa: D102
        return ZendeskCursorIncrementalPaginator(None)

    def get_url_params(  # noqa: D102
        self,
        context: Context | None,
        next_page_token: str | None,
    ) -> dict[str, t.Any]:
        if next_page_token:
            return {"cursor": next_page_token}
        start = self.get_starting_replication_key_value(context)
        raw = start or self.config.get("start_date", "2020-01-01T00:00:00Z")
        start_dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return {"start_time": int(start_dt.timestamp())}
