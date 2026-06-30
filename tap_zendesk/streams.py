"""Stream classes for tap-zendesk."""

from __future__ import annotations

import typing as t

from singer_sdk import typing as th

from tap_zendesk.client import (
    ZendeskCursorIncrementalExportStream,
    ZendeskIncrementalExportStream,
    ZendeskOffsetStream,
    ZendeskOptionalFeatureStream,
    ZendeskStream,
)

# th.AnyType produces {} which the SDK rejects during schema emission.
# Use this instead for fields whose value type varies at runtime.
_AnyType = th.CustomType(
    {"type": ["string", "number", "integer", "boolean", "array", "object", "null"]}
)


# ---------------------------------------------------------------------------
# Incremental export streams
# ---------------------------------------------------------------------------


class TicketsStream(ZendeskCursorIncrementalExportStream):
    """Zendesk tickets via cursor-based incremental export."""

    name = "tickets"
    path = "/incremental/tickets/cursor.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "updated_at"
    records_jsonpath = "$.tickets[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("external_id", th.StringType),
        th.Property("type", th.StringType),
        th.Property("subject", th.StringType),
        th.Property("raw_subject", th.StringType),
        th.Property("description", th.StringType),
        th.Property("priority", th.StringType),
        th.Property("status", th.StringType),
        th.Property("recipient", th.StringType),
        th.Property("requester_id", th.IntegerType),
        th.Property("submitter_id", th.IntegerType),
        th.Property("assignee_id", th.IntegerType),
        th.Property("organization_id", th.IntegerType),
        th.Property("group_id", th.IntegerType),
        th.Property("collaborator_ids", th.ArrayType(th.IntegerType)),
        th.Property("follower_ids", th.ArrayType(th.IntegerType)),
        th.Property("email_cc_ids", th.ArrayType(th.IntegerType)),
        th.Property("has_incidents", th.BooleanType),
        th.Property("is_public", th.BooleanType),
        th.Property("due_at", th.DateTimeType),
        th.Property("tags", th.ArrayType(th.StringType)),
        th.Property(
            "custom_fields",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("value", _AnyType),
                ),
            ),
        ),
        th.Property(
            "satisfaction_rating",
            th.ObjectType(
                th.Property("id", th.IntegerType),
                th.Property("score", th.StringType),
                th.Property("comment", th.StringType),
            ),
        ),
        th.Property("sharing_agreement_ids", th.ArrayType(th.IntegerType)),
        th.Property("brand_id", th.IntegerType),
        th.Property("allow_channelback", th.BooleanType),
        th.Property("allow_attachments", th.BooleanType),
        th.Property("from_messaging_channel", th.BooleanType),
        th.Property("generated_timestamp", th.IntegerType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property(
            "via",
            th.ObjectType(
                th.Property("channel", th.StringType),
                th.Property(
                    "source",
                    th.ObjectType(
                        th.Property("from", _AnyType),
                        th.Property("to", _AnyType),
                        th.Property("rel", th.StringType),
                    ),
                ),
            ),
        ),
    ).to_dict()


class UsersStream(ZendeskIncrementalExportStream):
    """Zendesk users via time-based incremental export."""

    name = "users"
    path = "/incremental/users.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "updated_at"
    records_jsonpath = "$.users[*]"

    def get_child_context(  # noqa: D102
        self,
        record: dict,
        context: t.Mapping[str, t.Any] | None,  # noqa: ARG002
    ) -> dict:
        return {"id": record["id"]}

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("name", th.StringType),
        th.Property("email", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("time_zone", th.StringType),
        th.Property("iana_time_zone", th.StringType),
        th.Property("phone", th.StringType),
        th.Property("shared_phone_number", th.BooleanType),
        th.Property("locale_id", th.IntegerType),
        th.Property("locale", th.StringType),
        th.Property("organization_id", th.IntegerType),
        th.Property("role", th.StringType),
        th.Property("verified", th.BooleanType),
        th.Property("external_id", th.StringType),
        th.Property("tags", th.ArrayType(th.StringType)),
        th.Property("alias", th.StringType),
        th.Property("active", th.BooleanType),
        th.Property("shared", th.BooleanType),
        th.Property("shared_agent", th.BooleanType),
        th.Property("last_login_at", th.DateTimeType),
        th.Property("two_factor_auth_enabled", th.BooleanType),
        th.Property("signature", th.StringType),
        th.Property("details", th.StringType),
        th.Property("notes", th.StringType),
        th.Property("role_type", th.IntegerType),
        th.Property("custom_role_id", th.IntegerType),
        th.Property("moderator", th.BooleanType),
        th.Property("ticket_restriction", th.StringType),
        th.Property("only_private_comments", th.BooleanType),
        th.Property("restricted_agent", th.BooleanType),
        th.Property("suspended", th.BooleanType),
        th.Property("default_group_id", th.IntegerType),
        th.Property("report_csv", th.BooleanType),
    ).to_dict()


class OrganizationsStream(ZendeskIncrementalExportStream):
    """Zendesk organizations via time-based incremental export."""

    name = "organizations"
    path = "/incremental/organizations.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "updated_at"
    records_jsonpath = "$.organizations[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("name", th.StringType),
        th.Property("shared_tickets", th.BooleanType),
        th.Property("shared_comments", th.BooleanType),
        th.Property("external_id", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("domain_names", th.ArrayType(th.StringType)),
        th.Property("details", th.StringType),
        th.Property("notes", th.StringType),
        th.Property("group_id", th.IntegerType),
        th.Property("tags", th.ArrayType(th.StringType)),
        th.Property("custom_fields", th.ObjectType()),
    ).to_dict()


# ---------------------------------------------------------------------------
# Standard cursor-paginated streams
# ---------------------------------------------------------------------------


class GroupsStream(ZendeskStream):
    """Zendesk groups."""

    name = "groups"
    path = "/groups.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.groups[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
        th.Property("default", th.BooleanType),
        th.Property("deleted", th.BooleanType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


class GroupMembershipsStream(ZendeskStream):
    """Zendesk group memberships."""

    name = "group_memberships"
    path = "/group_memberships.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.group_memberships[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("user_id", th.IntegerType),
        th.Property("group_id", th.IntegerType),
        th.Property("default", th.BooleanType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


class MacrosStream(ZendeskStream):
    """Zendesk macros."""

    name = "macros"
    path = "/macros.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.macros[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("title", th.StringType),
        th.Property("active", th.BooleanType),
        th.Property(
            "restriction",
            th.ObjectType(
                th.Property("type", th.StringType),
                th.Property("id", th.IntegerType),
                th.Property("ids", th.ArrayType(th.IntegerType)),
            ),
        ),
        th.Property(
            "actions",
            th.ArrayType(
                th.ObjectType(
                    th.Property("field", th.StringType),
                    th.Property("value", _AnyType),
                ),
            ),
        ),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


class OrganizationFieldsStream(ZendeskStream):
    """Zendesk organization fields."""

    name = "organization_fields"
    path = "/organization_fields.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.organization_fields[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("key", th.StringType),
        th.Property("type", th.StringType),
        th.Property("title", th.StringType),
        th.Property("raw_title", th.StringType),
        th.Property("description", th.StringType),
        th.Property("raw_description", th.StringType),
        th.Property("position", th.IntegerType),
        th.Property("active", th.BooleanType),
        th.Property("system", th.BooleanType),
        th.Property("regexp_for_validation", th.StringType),
        th.Property("tag", th.StringType),
        th.Property(
            "custom_field_options",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("name", th.StringType),
                    th.Property("raw_name", th.StringType),
                    th.Property("value", th.StringType),
                    th.Property("default", th.BooleanType),
                ),
            ),
        ),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


class OrganizationMembershipsStream(ZendeskStream):
    """Zendesk organization memberships."""

    name = "organization_memberships"
    path = "/organization_memberships.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.organization_memberships[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("user_id", th.IntegerType),
        th.Property("organization_id", th.IntegerType),
        th.Property("default", th.BooleanType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


class SatisfactionRatingsStream(ZendeskStream):
    """Zendesk satisfaction ratings."""

    name = "satisfaction_ratings"
    path = "/satisfaction_ratings.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.satisfaction_ratings[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("assignee_id", th.IntegerType),
        th.Property("group_id", th.IntegerType),
        th.Property("requester_id", th.IntegerType),
        th.Property("ticket_id", th.IntegerType),
        th.Property("score", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("reason", th.StringType),
        th.Property("reason_code", th.IntegerType),
        th.Property("reason_id", th.IntegerType),
        th.Property("comment", th.StringType),
        th.Property("assignee_name", th.StringType),
        th.Property("requester_name", th.StringType),
        th.Property("ticket_subject", th.StringType),
    ).to_dict()


class SchedulesStream(ZendeskOffsetStream):
    """Zendesk business hours schedules."""

    name = "schedules"
    path = "/business_hours/schedules.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.schedules[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("time_zone", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property(
            "intervals",
            th.ArrayType(
                th.ObjectType(
                    th.Property("start_time", th.IntegerType),
                    th.Property("end_time", th.IntegerType),
                ),
            ),
        ),
    ).to_dict()


class SlaPoliciesStream(ZendeskOffsetStream):
    """Zendesk SLA policies."""

    name = "sla_policies"
    path = "/slas/policies.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.sla_policies[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("title", th.StringType),
        th.Property("description", th.StringType),
        th.Property("position", th.IntegerType),
        th.Property("filter", th.ObjectType()),
        th.Property(
            "policy_metrics",
            th.ArrayType(
                th.ObjectType(
                    th.Property("priority", th.StringType),
                    th.Property("metric", th.StringType),
                    th.Property("target", th.IntegerType),
                    th.Property("business_hours", th.BooleanType),
                ),
            ),
        ),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


class TriggersStream(ZendeskStream):
    """Zendesk triggers."""

    name = "triggers"
    path = "/triggers.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.triggers[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("title", th.StringType),
        th.Property("active", th.BooleanType),
        th.Property("position", th.IntegerType),
        th.Property("description", th.StringType),
        th.Property("conditions", th.ObjectType()),
        th.Property(
            "actions",
            th.ArrayType(
                th.ObjectType(
                    th.Property("field", th.StringType),
                    th.Property("value", _AnyType),
                ),
            ),
        ),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


class CustomRolesStream(ZendeskOffsetStream):
    """Zendesk custom roles."""

    name = "custom_roles"
    path = "/custom_roles.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.custom_roles[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
        th.Property("configuration", th.ObjectType()),
        th.Property("role_type", th.IntegerType),
        th.Property("team_member_count", th.IntegerType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


class UserIdentitiesStream(ZendeskStream):
    """Zendesk user identities — child stream of UsersStream.

    Synced for each user emitted by the parent in the current sync window.
    Zendesk updates a user's updated_at when identities change, so incremental
    parent + child correctly captures identity mutations.

    WARNING: issues one API call per user on first sync. Accounts with hundreds
    of thousands of users will hit rate limits and take many hours. Deselect this
    stream in meltano.yml if not needed, or run with a narrow start_date window.
    """

    name = "user_identities"
    parent_stream_type = UsersStream
    path = "/users/{id}/identities.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.identities[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("user_id", th.IntegerType),
        th.Property("type", th.StringType),
        th.Property("value", th.StringType),
        th.Property("verified", th.BooleanType),
        th.Property("primary", th.BooleanType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("undeliverable_count", th.IntegerType),
        th.Property("deliverable_state", th.StringType),
    ).to_dict()


# ---------------------------------------------------------------------------
# Help Center streams (Guide API — /api/v2/help_center/...)
# ---------------------------------------------------------------------------


class ZendeskHelpCenterStream(ZendeskOptionalFeatureStream):
    """Base for Help Center (Guide) streams.

    Returns empty records on 404/403 — Guide is an optional Zendesk product
    that is not enabled on all plans or trial instances.
    """


class CategoriesStream(ZendeskHelpCenterStream):
    """Zendesk Help Center categories."""

    name = "categories"
    path = "/help_center/categories.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.categories[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("html_url", th.StringType),
        th.Property("source_locale", th.StringType),
        th.Property("locale", th.StringType),
        th.Property("outdated", th.BooleanType),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
        th.Property("position", th.IntegerType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


class SectionsStream(ZendeskHelpCenterStream):
    """Zendesk Help Center sections."""

    name = "sections"
    path = "/help_center/sections.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.sections[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("html_url", th.StringType),
        th.Property("source_locale", th.StringType),
        th.Property("locale", th.StringType),
        th.Property("outdated", th.BooleanType),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
        th.Property("position", th.IntegerType),
        th.Property("sorting", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("parent_section_id", th.IntegerType),
        th.Property("category_id", th.IntegerType),
        th.Property("theme_template", th.StringType),
    ).to_dict()


class PostsStream(ZendeskHelpCenterStream):
    """Zendesk Help Center posts."""

    name = "posts"
    path = "/help_center/posts.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.posts[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("author_id", th.IntegerType),
        th.Property("comment_count", th.IntegerType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("details", th.StringType),
        th.Property("featured", th.BooleanType),
        th.Property("follower_count", th.IntegerType),
        th.Property("html_url", th.StringType),
        th.Property("label_names", th.ArrayType(th.StringType)),
        th.Property("non_author_editor_id", th.IntegerType),
        th.Property("non_author_last_edited_at", th.DateTimeType),
        th.Property("pinned", th.BooleanType),
        th.Property("section_id", th.IntegerType),
        th.Property("status", th.StringType),
        th.Property("title", th.StringType),
        th.Property("topic_id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("vote_count", th.IntegerType),
        th.Property("vote_sum", th.IntegerType),
    ).to_dict()


class ArticlesStream(ZendeskHelpCenterStream):
    """Zendesk Help Center knowledge base articles."""

    name = "articles"
    path = "/help_center/articles.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.articles[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("html_url", th.StringType),
        th.Property("author_id", th.IntegerType),
        th.Property("comments_disabled", th.BooleanType),
        th.Property("draft", th.BooleanType),
        th.Property("promoted", th.BooleanType),
        th.Property("position", th.IntegerType),
        th.Property("vote_sum", th.IntegerType),
        th.Property("vote_count", th.IntegerType),
        th.Property("section_id", th.IntegerType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("name", th.StringType),
        th.Property("title", th.StringType),
        th.Property("source_locale", th.StringType),
        th.Property("locale", th.StringType),
        th.Property("outdated", th.BooleanType),
        th.Property("outdated_locales", th.ArrayType(th.StringType)),
        th.Property("label_names", th.ArrayType(th.StringType)),
        th.Property("body", th.StringType),
    ).to_dict()


class TopicsStream(ZendeskHelpCenterStream):
    """Zendesk Help Center community topics."""

    name = "topics"
    path = "/community/topics.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.topics[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("html_url", th.StringType),
        th.Property("name", th.StringType),
        th.Property("description", th.StringType),
        th.Property("position", th.IntegerType),
        th.Property("follower_count", th.IntegerType),
        th.Property("topic_type", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


# ---------------------------------------------------------------------------
# Additional incremental export streams
# ---------------------------------------------------------------------------


class TicketMetricEventsStream(ZendeskIncrementalExportStream):
    """Zendesk ticket metric events via time-based incremental export.

    Tracks metric milestones (reply_time, agent_work_time, requester_wait_time)
    as individual events. Per Zendesk docs the endpoint returns max 100 per page.
    """

    name = "ticket_metric_events"
    path = "/incremental/ticket_metric_events.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = "time"
    records_jsonpath = "$.ticket_metric_events[*]"
    _per_page = 100

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("ticket_id", th.IntegerType),
        th.Property("metric", th.StringType),
        th.Property("instance_id", th.IntegerType),
        th.Property("type", th.StringType),
        th.Property("time", th.DateTimeType),
        th.Property("deleted", th.BooleanType),
    ).to_dict()


# ---------------------------------------------------------------------------
# Additional full-table streams
# ---------------------------------------------------------------------------


class TicketFieldsStream(ZendeskStream):
    """Zendesk ticket field definitions (system and custom)."""

    name = "ticket_fields"
    path = "/ticket_fields.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.ticket_fields[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("type", th.StringType),
        th.Property("title", th.StringType),
        th.Property("raw_title", th.StringType),
        th.Property("description", th.StringType),
        th.Property("raw_description", th.StringType),
        th.Property("position", th.IntegerType),
        th.Property("active", th.BooleanType),
        th.Property("required", th.BooleanType),
        th.Property("collapsed_for_agents", th.BooleanType),
        th.Property("regexp_for_validation", th.StringType),
        th.Property("title_in_portal", th.StringType),
        th.Property("raw_title_in_portal", th.StringType),
        th.Property("visible_in_portal", th.BooleanType),
        th.Property("editable_in_portal", th.BooleanType),
        th.Property("required_in_portal", th.BooleanType),
        th.Property("tag", th.StringType),
        th.Property(
            "system_field_options",
            th.ArrayType(
                th.ObjectType(
                    th.Property("name", th.StringType),
                    th.Property("value", th.StringType),
                ),
            ),
        ),
        th.Property(
            "custom_field_options",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("name", th.StringType),
                    th.Property("raw_name", th.StringType),
                    th.Property("value", th.StringType),
                    th.Property("default", th.BooleanType),
                ),
            ),
        ),
        th.Property("removable", th.BooleanType),
        th.Property("agent_description", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


class TicketFormsStream(ZendeskOptionalFeatureStream):
    """Zendesk ticket forms (Enterprise only — skipped on 403/404)."""

    name = "ticket_forms"
    path = "/ticket_forms.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.ticket_forms[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("name", th.StringType),
        th.Property("raw_name", th.StringType),
        th.Property("display_name", th.StringType),
        th.Property("raw_display_name", th.StringType),
        th.Property("active", th.BooleanType),
        th.Property("end_user_visible", th.BooleanType),
        th.Property("default", th.BooleanType),
        th.Property("ticket_field_ids", th.ArrayType(th.IntegerType)),
        th.Property("in_all_brands", th.BooleanType),
        th.Property("restricted_brand_ids", th.ArrayType(th.IntegerType)),
        th.Property("position", th.IntegerType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


class TicketMetricsStream(ZendeskStream):
    """Zendesk per-ticket SLA and timing metrics."""

    name = "ticket_metrics"
    path = "/ticket_metrics.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.ticket_metrics[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("ticket_id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("group_stations", th.IntegerType),
        th.Property("assignee_stations", th.IntegerType),
        th.Property("reopens", th.IntegerType),
        th.Property("replies", th.IntegerType),
        th.Property("assignee_updated_at", th.DateTimeType),
        th.Property("requester_updated_at", th.DateTimeType),
        th.Property("status_updated_at", th.DateTimeType),
        th.Property("initially_assigned_at", th.DateTimeType),
        th.Property("assigned_at", th.DateTimeType),
        th.Property("solved_at", th.DateTimeType),
        th.Property("latest_comment_added_at", th.DateTimeType),
        th.Property(
            "first_resolution_time_in_minutes",
            th.ObjectType(
                th.Property("calendar", th.IntegerType),
                th.Property("business", th.IntegerType),
            ),
        ),
        th.Property(
            "reply_time_in_minutes",
            th.ObjectType(
                th.Property("calendar", th.IntegerType),
                th.Property("business", th.IntegerType),
            ),
        ),
        th.Property(
            "full_resolution_time_in_minutes",
            th.ObjectType(
                th.Property("calendar", th.IntegerType),
                th.Property("business", th.IntegerType),
            ),
        ),
        th.Property(
            "agent_wait_time_in_minutes",
            th.ObjectType(
                th.Property("calendar", th.IntegerType),
                th.Property("business", th.IntegerType),
            ),
        ),
        th.Property(
            "requester_wait_time_in_minutes",
            th.ObjectType(
                th.Property("calendar", th.IntegerType),
                th.Property("business", th.IntegerType),
            ),
        ),
        th.Property(
            "on_hold_time_in_minutes",
            th.ObjectType(
                th.Property("calendar", th.IntegerType),
                th.Property("business", th.IntegerType),
            ),
        ),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


class UserFieldsStream(ZendeskStream):
    """Zendesk user field definitions."""

    name = "user_fields"
    path = "/user_fields.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.user_fields[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("key", th.StringType),
        th.Property("type", th.StringType),
        th.Property("title", th.StringType),
        th.Property("raw_title", th.StringType),
        th.Property("description", th.StringType),
        th.Property("raw_description", th.StringType),
        th.Property("position", th.IntegerType),
        th.Property("active", th.BooleanType),
        th.Property("system", th.BooleanType),
        th.Property("regexp_for_validation", th.StringType),
        th.Property("tag", th.StringType),
        th.Property(
            "custom_field_options",
            th.ArrayType(
                th.ObjectType(
                    th.Property("id", th.IntegerType),
                    th.Property("name", th.StringType),
                    th.Property("raw_name", th.StringType),
                    th.Property("value", th.StringType),
                    th.Property("default", th.BooleanType),
                ),
            ),
        ),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


class BrandsStream(ZendeskOffsetStream):
    """Zendesk brands (multi-brand configurations)."""

    name = "brands"
    path = "/brands.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.brands[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("name", th.StringType),
        th.Property("brand_url", th.StringType),
        th.Property("has_help_center", th.BooleanType),
        th.Property("help_center_state", th.StringType),
        th.Property("active", th.BooleanType),
        th.Property("default", th.BooleanType),
        th.Property("logo", th.ObjectType()),
        th.Property("ticket_form_ids", th.ArrayType(th.IntegerType)),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("subdomain", th.StringType),
        th.Property("host_mapping", th.StringType),
        th.Property("is_deleted", th.BooleanType),
    ).to_dict()


class AutomationsStream(ZendeskStream):
    """Zendesk time-based automation rules."""

    name = "automations"
    path = "/automations.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.automations[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("title", th.StringType),
        th.Property("active", th.BooleanType),
        th.Property("position", th.IntegerType),
        th.Property("conditions", th.ObjectType()),
        th.Property(
            "actions",
            th.ArrayType(
                th.ObjectType(
                    th.Property("field", th.StringType),
                    th.Property("value", _AnyType),
                ),
            ),
        ),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


class ViewsStream(ZendeskStream):
    """Zendesk ticket views (shared and personal)."""

    name = "views"
    path = "/views.json"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    records_jsonpath = "$.views[*]"

    schema = th.PropertiesList(
        th.Property("id", th.IntegerType),
        th.Property("url", th.StringType),
        th.Property("title", th.StringType),
        th.Property("active", th.BooleanType),
        th.Property("position", th.IntegerType),
        th.Property("description", th.StringType),
        th.Property("restriction", th.ObjectType()),
        th.Property("execution", th.ObjectType()),
        th.Property("conditions", th.ObjectType()),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
    ).to_dict()


class TagsStream(ZendeskOffsetStream):
    """Zendesk tags with usage counts."""

    name = "tags"
    path = "/tags.json"
    primary_keys: t.ClassVar[list[str]] = ["name"]
    records_jsonpath = "$.tags[*]"

    schema = th.PropertiesList(
        th.Property("name", th.StringType),
        th.Property("count", th.IntegerType),
    ).to_dict()
