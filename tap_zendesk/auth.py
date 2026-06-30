"""Zendesk Authentication."""

from __future__ import annotations

from singer_sdk.authenticators import OAuthAuthenticator, SingletonMeta


class ZendeskOAuthAuthenticator(OAuthAuthenticator, metaclass=SingletonMeta):
    """OAuth2 authenticator for Zendesk (proxy-refresh pattern)."""

    @property
    def oauth_request_body(self) -> dict:  # noqa: D102
        creds = self.config.get("oauth_credentials", {})
        return {
            "grant_type": "refresh_token",
            "refresh_token": creds.get("refresh_token", ""),
        }

    @property
    def oauth_request_headers(self) -> dict:  # noqa: D102
        creds = self.config.get("oauth_credentials", {})
        proxy_auth = creds.get("refresh_proxy_url_auth")
        if proxy_auth:
            return {"Authorization": proxy_auth}
        return {}
