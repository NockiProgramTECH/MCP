"""LinkedIn OpenID Connect and Posts API service layer."""

from __future__ import annotations

from typing import Any

from pydantic import TypeAdapter

from ..config import Settings
from ..core.errors import ConfigurationError, ExternalAPIError
from ..core.http import HttpClient
from ..models.linkedin import LinkedInPostCreate

_LINKEDIN_HOSTS = frozenset({"api.linkedin.com"})
_LINKEDIN_BASE_URL = "https://api.linkedin.com"
_JSON_OBJECT = TypeAdapter(dict[str, Any])


class LinkedInService:
    """Wrapper for the official LinkedIn OIDC and REST Posts APIs."""

    def __init__(self, settings: Settings, http_client: HttpClient | None = None) -> None:
        self._settings = settings
        self._http = http_client or HttpClient(settings, allowed_hosts=_LINKEDIN_HOSTS)

    async def aclose(self) -> None:
        await self._http.aclose()

    def _headers(self, *, rest: bool = False) -> dict[str, str]:
        token = self._settings.linkedin_access_token
        if token is None:
            raise ConfigurationError(
                "LinkedIn is not configured. Set LINKEDIN_ACCESS_TOKEN in the environment."
            )
        headers = {"Authorization": f"Bearer {token.get_secret_value()}"}
        if rest:
            headers.update(
                {
                    "LinkedIn-Version": self._settings.linkedin_api_version,
                    "X-Restli-Protocol-Version": "2.0.0",
                    "Content-Type": "application/json",
                }
            )
        return headers

    async def get_profile(self) -> dict[str, Any]:
        response = await self._http.request(
            "GET", f"{_LINKEDIN_BASE_URL}/v2/userinfo", headers=self._headers()
        )
        return _object(response.json())

    async def create_post(self, payload: LinkedInPostCreate) -> dict[str, Any]:
        author = payload.author_urn
        if author is None:
            profile = await self.get_profile()
            subject = profile.get("sub")
            if not isinstance(subject, str) or not subject:
                raise ExternalAPIError("LinkedIn did not return a usable member identifier.")
            author = f"urn:li:person:{subject}"
        _validate_author_urn(author)
        response = await self._http.request(
            "POST",
            f"{_LINKEDIN_BASE_URL}/rest/posts",
            headers=self._headers(rest=True),
            json={
                "author": author,
                "commentary": payload.commentary,
                "visibility": payload.visibility,
                "distribution": {
                    "feedDistribution": "MAIN_FEED",
                    "targetEntities": [],
                    "thirdPartyDistributionChannels": [],
                },
                "lifecycleState": "PUBLISHED",
                "isReshareDisabledByAuthor": False,
            },
        )
        post_id = response.headers.get("x-restli-id")
        if not post_id:
            raise ExternalAPIError("LinkedIn did not return the created post identifier.")
        return {"id": post_id, "author": author}

    async def get_posts(
        self, author_urn: str, *, start: int = 0, count: int = 10
    ) -> dict[str, Any]:
        _validate_author_urn(author_urn)
        response = await self._http.request(
            "GET",
            f"{_LINKEDIN_BASE_URL}/rest/posts",
            headers=self._headers(rest=True),
            params={"q": "author", "author": author_urn, "start": start, "count": count},
        )
        return _object(response.json())


def _object(value: Any) -> dict[str, Any]:
    try:
        return _JSON_OBJECT.validate_python(value)
    except (TypeError, ValueError) as exc:
        raise ExternalAPIError("LinkedIn returned an invalid JSON response.") from exc


def _validate_author_urn(value: str) -> None:
    if not (value.startswith("urn:li:person:") or value.startswith("urn:li:organization:")):
        raise ValueError("author_urn must be a LinkedIn person or organization URN.")
    identifier = value.rsplit(":", 1)[-1]
    if not identifier or not all(char.isalnum() or char in "_-" for char in identifier):
        raise ValueError("author_urn contains an invalid identifier.")
