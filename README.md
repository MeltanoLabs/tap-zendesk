# `tap-zendesk`

`tap-zendesk` is a Singer tap for the [Zendesk Support API](https://developer.zendesk.com/api-reference/ticketing/introduction/) and [Help Center (Guide) API](https://developer.zendesk.com/api-reference/help_center/help-center-api/introduction/).

Built with the [Meltano Singer SDK](https://sdk.meltano.com).

## Capabilities

* `catalog`
* `state`
* `discover`
* `about`
* `stream-maps`

## Streams

### Incremental streams

State is written after each sync so subsequent runs only fetch changes since the last bookmark.

| Stream | Endpoint | Replication Key | Description |
|:-------|:---------|:---------------:|:------------|
| `tickets` | `GET /api/v2/incremental/tickets/cursor.json` | `updated_at` | Support tickets (cursor-based incremental export) |
| `users` | `GET /api/v2/incremental/users.json` | `updated_at` | Zendesk users — agents, admins, end-users (time-based incremental export) |
| `organizations` | `GET /api/v2/incremental/organizations.json` | `updated_at` | Organizations associated with users and tickets (time-based incremental export) |
| `ticket_metric_events` | `GET /api/v2/incremental/ticket_metric_events.json` | `time` | Individual metric milestone events — reply time, agent work time, requester wait time |

### Full table streams

| Stream | Endpoint | Description |
|:-------|:---------|:------------|
| `automations` | `GET /api/v2/automations.json` | Time-based automation rules |
| `brands` | `GET /api/v2/brands.json` | Brand configurations (multi-brand setups) |
| `custom_roles` | `GET /api/v2/custom_roles.json` | Custom agent roles |
| `group_memberships` | `GET /api/v2/group_memberships.json` | Agent-to-group memberships |
| `groups` | `GET /api/v2/groups.json` | Agent groups |
| `macros` | `GET /api/v2/macros.json` | Macros for bulk-updating tickets |
| `organization_fields` | `GET /api/v2/organization_fields.json` | Custom fields defined on organizations |
| `organization_memberships` | `GET /api/v2/organization_memberships.json` | User-to-organization memberships |
| `satisfaction_ratings` | `GET /api/v2/satisfaction_ratings.json` | CSAT ratings submitted by end-users |
| `schedules` | `GET /api/v2/business_hours/schedules.json` | Business hours schedules |
| `sla_policies` | `GET /api/v2/slas/policies.json` | SLA policy definitions |
| `tags` | `GET /api/v2/tags.json` | Tag vocabulary with usage counts |
| `ticket_fields` | `GET /api/v2/ticket_fields.json` | Ticket field definitions (system and custom) |
| `ticket_forms` | `GET /api/v2/ticket_forms.json` | Ticket form definitions — skipped gracefully if not available on your plan |
| `ticket_metrics` | `GET /api/v2/ticket_metrics.json` | Per-ticket SLA and timing metrics (one row per ticket) |
| `triggers` | `GET /api/v2/triggers.json` | Event-based automation triggers |
| `user_fields` | `GET /api/v2/user_fields.json` | Custom user field definitions |
| `user_identities` | `GET /api/v2/users/{id}/identities.json` | Email addresses, phone numbers and social accounts per user (child of `users`) |
| `views` | `GET /api/v2/views.json` | Shared and personal ticket views |

### Help Center streams (Guide API)

These streams are skipped gracefully (returning zero records) when the Zendesk Guide / Help Center product is not enabled on the instance.

| Stream | Endpoint | Description |
|:-------|:---------|:------------|
| `articles` | `GET /api/v2/help_center/articles.json` | Knowledge base articles |
| `categories` | `GET /api/v2/help_center/categories.json` | Top-level Help Center categories |
| `posts` | `GET /api/v2/help_center/posts.json` | Community posts |
| `sections` | `GET /api/v2/help_center/sections.json` | Sections within categories |
| `topics` | `GET /api/v2/community/topics.json` | Community discussion topics |

`user_identities` is a child stream of `users` — identities are fetched for every user emitted by the parent in the current sync window. Because Zendesk updates a user's `updated_at` when their identities change, incremental syncs of `users` automatically bring in changed identities.

`ticket_forms` and `custom_roles` are available on higher Zendesk plans only. The tap handles 403 Forbidden responses from these endpoints gracefully and continues syncing other streams.

## Installation

Install from GitHub:

```bash
uv tool install git+https://github.com/MeltanoLabs/tap-zendesk.git
```

Or for local development:

```bash
uv sync
```

## Configuration

### Accepted Config Options

| Setting | Required | Default | Description |
|:--------|:--------:|:-------:|:------------|
| `subdomain` | ✅ | — | Your Zendesk subdomain (e.g. `mycompany` for `mycompany.zendesk.com`) |
| `start_date` | ✅ | — | Earliest record date to sync (`YYYY-MM-DDTHH:mm:ssZ`) |
| `email` | OAuth or Token | — | Agent email address — required for API Token auth |
| `api_token` | OAuth or Token | — | Zendesk API token — required for API Token auth |
| `oauth_credentials.access_token` | OAuth or Token | — | OAuth2 access token — required for OAuth auth |
| `oauth_credentials.refresh_token` | False | — | OAuth2 refresh token |
| `oauth_credentials.refresh_proxy_url` | False | — | Meltano platform proxy URL for token refresh |
| `oauth_credentials.refresh_proxy_url_auth` | False | — | Authorization header value for the refresh proxy request |

One authentication group must be satisfied:

* **OAuth2:** `subdomain` + `start_date` + `oauth_credentials.access_token`
* **OAuth2 with refresh:** `subdomain` + `start_date` + `oauth_credentials.refresh_token` + `oauth_credentials.refresh_proxy_url`
* **API Token:** `subdomain` + `start_date` + `email` + `api_token`

A full list of supported settings and capabilities is available by running:

```bash
tap-zendesk --about
```

### Authentication

#### OAuth2 (primary)

OAuth2 is the primary auth path used by the Meltano platform. The platform manages the token exchange and injects 
`oauth_credentials.access_token` at runtime. No additional setup is required when connecting through Meltano.

For direct use, obtain an OAuth access token by registering an OAuth client in **Zendesk Admin Center → Apps and integrations → OAuth clients** and completing the authorization code flow.

#### API Token (secondary)

Generate an API token in **Zendesk Admin Center → Apps and integrations → Zendesk API → API token**, then provide:

* `email` — the Zendesk agent email address
* `api_token` — the generated token

The tap authenticates using HTTP Basic auth with the username `{email}/token` and the token as the password.

### Configure using environment variables

```bash
# API Token auth
export TAP_ZENDESK_SUBDOMAIN=mycompany
export TAP_ZENDESK_START_DATE=2024-01-01T00:00:00Z
export TAP_ZENDESK_EMAIL=agent@mycompany.com
export TAP_ZENDESK_API_TOKEN=your_api_token

# OAuth auth
export TAP_ZENDESK_SUBDOMAIN=mycompany
export TAP_ZENDESK_START_DATE=2024-01-01T00:00:00Z
export TAP_ZENDESK_OAUTH_CREDENTIALS__ACCESS_TOKEN=your_access_token
```

Alternatively, create a `config.json`:

```json
{
  "subdomain": "mycompany",
  "start_date": "2024-01-01T00:00:00Z",
  "email": "agent@mycompany.com",
  "api_token": "your_api_token"
}
```

## Usage

### Executing the tap directly

```bash
tap-zendesk --version
tap-zendesk --help
tap-zendesk --config config.json --discover > catalog.json
tap-zendesk --config config.json --catalog catalog.json
```

### Using with Meltano

```bash
# Install Meltano
uv tool install meltano

# Test invocation
meltano invoke tap-zendesk --version

# Discover streams
meltano invoke tap-zendesk --discover

# Run a test EL pipeline
meltano run tap-zendesk target-jsonl
```

## Developer Resources

### Initialize your development environment

Prerequisites: Python 3.10+, [uv](https://docs.astral.sh/uv/)

```bash
uv sync
```

### Run tests

Tests require a live Zendesk instance. Provide credentials via environment variables:

```bash
export TAP_ZENDESK_SUBDOMAIN=mycompany
export TAP_ZENDESK_EMAIL=agent@mycompany.com
export TAP_ZENDESK_API_TOKEN=your_api_token
export TAP_ZENDESK_START_DATE=2024-01-01T00:00:00Z

uv run pytest
```

### Lint and type-check

```bash
uv run tox -e lint
```

### SDK Dev Guide

See the [Singer SDK dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more details on building taps.
