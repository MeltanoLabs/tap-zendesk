"""Tests standard tap features using the built-in SDK tests library.

Requires real Zendesk credentials via environment variables:
  TAP_ZENDESK_SUBDOMAIN, TAP_ZENDESK_EMAIL, TAP_ZENDESK_API_TOKEN, TAP_ZENDESK_START_DATE
"""

import os

from singer_sdk.testing import SuiteConfig, get_tap_test_class

from tap_zendesk.tap import TapZendesk

SAMPLE_CONFIG = {
    "subdomain": os.environ.get("TAP_ZENDESK_SUBDOMAIN", ""),
    "email": os.environ.get("TAP_ZENDESK_EMAIL", ""),
    "api_token": os.environ.get("TAP_ZENDESK_API_TOKEN", ""),
    "start_date": os.environ.get("TAP_ZENDESK_START_DATE", "2010-01-01T00:00:00Z"),
}

TestTapZendesk = get_tap_test_class(
    tap_class=TapZendesk,
    config=SAMPLE_CONFIG,
    suite_config=SuiteConfig(
        max_records_limit=10,
    ),
)
