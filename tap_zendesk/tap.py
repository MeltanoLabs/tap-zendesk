"""tap-zendesk tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th

from tap_zendesk import streams


class TapZendesk(Tap):
    """Singer tap for Zendesk Support."""

    name = "tap-zendesk"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "subdomain",
            th.StringType,
            required=True,
            description="Your Zendesk subdomain (e.g. 'mycompany' for mycompany.zendesk.com).",  # noqa: E501
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            required=True,
            description="Earliest record date to sync (ISO 8601, e.g. 2020-01-01T00:00:00Z).",  # noqa: E501
        ),
        # --- OAuth (primary auth path) ---
        th.Property(
            "oauth_credentials",
            th.ObjectType(
                th.Property(
                    "access_token",
                    th.StringType,
                    secret=True,
                    description="OAuth2 access token.",
                ),
                th.Property(
                    "refresh_token",
                    th.StringType,
                    secret=True,
                    description="OAuth2 refresh token.",
                ),
                th.Property(
                    "refresh_proxy_url",
                    th.StringType,
                    description="Matatika platform proxy URL for token refresh.",
                ),
                th.Property(
                    "refresh_proxy_url_auth",
                    th.StringType,
                    secret=True,
                    description="Authorization header value for the refresh proxy request.",  # noqa: E501
                ),
            ),
            description="OAuth2 credentials (primary auth path).",
        ),
        # Short-hand alias so the platform can inject access_token at the top level
        th.Property(
            "access_token",
            th.StringType,
            secret=True,
            description="OAuth2 access token (alias for oauth_credentials.access_token).",  # noqa: E501
        ),
        # --- API Token (optional secondary auth path — used by Brandalley) ---
        th.Property(
            "email",
            th.StringType,
            description="Zendesk agent email address (required for API token auth).",
        ),
        th.Property(
            "api_token",
            th.StringType,
            secret=True,
            description="Zendesk API token (optional secondary auth — Basic: {email}/token:{api_token}).",  # noqa: E501
        ),
    ).to_dict()

    def discover_streams(self) -> list:
        """Return all discovered streams."""
        return [
            # Incremental export
            streams.TicketsStream(self),
            streams.UsersStream(self),
            streams.OrganizationsStream(self),
            streams.TicketMetricEventsStream(self),
            # Standard cursor-paginated
            streams.GroupsStream(self),
            streams.GroupMembershipsStream(self),
            streams.MacrosStream(self),
            streams.OrganizationFieldsStream(self),
            streams.OrganizationMembershipsStream(self),
            streams.SatisfactionRatingsStream(self),
            streams.SchedulesStream(self),
            streams.SlaPoliciesStream(self),
            streams.TriggersStream(self),
            streams.AutomationsStream(self),
            streams.ViewsStream(self),
            streams.CustomRolesStream(self),
            # Offset-paginated
            streams.BrandsStream(self),
            streams.TagsStream(self),
            # Field definitions
            streams.TicketFieldsStream(self),
            streams.TicketFormsStream(self),
            streams.TicketMetricsStream(self),
            streams.UserFieldsStream(self),
            # Child stream (per-user)
            streams.UserIdentitiesStream(self),
            # Help Center (Guide API — skipped gracefully if not enabled)
            streams.CategoriesStream(self),
            streams.SectionsStream(self),
            streams.ArticlesStream(self),
            streams.PostsStream(self),
            streams.TopicsStream(self),
        ]


if __name__ == "__main__":
    TapZendesk.cli()
