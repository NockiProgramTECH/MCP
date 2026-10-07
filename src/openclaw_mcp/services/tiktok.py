"""Official TikTok API service layer."""

from __future__ import annotations

from typing import Any

from pydantic import TypeAdapter

from ..config import Settings
from ..core.errors import ConfigurationError, ExternalAPIError
from ..core.http import HttpClient
from ..core.security import validate_public_media_url
from ..models.tiktok import TikTokVideoPublish

_TIKTOK_HOSTS = frozenset({"open.tiktokapis.com"})
_TIKTOK_BASE_URL = "https://open.tiktokapis.com"
_JSON_OBJECT = TypeAdapter(dict[str, Any])


class TikTokService:
    """Wrapper for TikTok Login, Display and Content Posting APIs."""

    def __init__(self, settings: Settings, http_client: HttpClient | None = None) -> None:
        self._settings = settings
        self._http = http_client or HttpClient(settings, allowed_hosts=_TIKTOK_HOSTS)

    async def aclose(self) -> None:
        await self._http.aclose()

    def _headers(self) -> dict[str, str]:
        token = self._settings.tiktok_access_token
        if token is None:
            raise ConfigurationError(
                "TikTok is not configured. Set TIKTOK_ACCESS_TOKEN in the environment."
            )
        return {
            "Authorization": f"Bearer {token.get_secret_value()}",
            "Content-Type": "application/json; charset=UTF-8",
        }

    async def get_user(self) -> dict[str, Any]:
        response = await self._http.request(
            "GET",
            f"{_TIKTOK_BASE_URL}/v2/user/info/",
            headers=self._headers(),
            params={"fields": "open_id,display_name,avatar_url"},
        )
        return _api_object(response.json())

    async def get_videos(self, *, max_count: int = 20, cursor: int | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"max_count": max_count}
        if cursor is not None:
            payload["cursor"] = cursor
        response = await self._http.request(
            "POST",
            f"{_TIKTOK_BASE_URL}/v2/video/list/",
            headers=self._headers(),
            json=payload,
        )
        return _api_object(response.json())

    async def publish_video(self, payload: TikTokVideoPublish) -> dict[str, Any]:
        validate_public_media_url(payload.video_url)
        creator_info = await self._creator_info()
        allowed = _privacy_options(creator_info)
        if payload.privacy_level not in allowed:
            raise ExternalAPIError(
                "The requested privacy level is not allowed for this TikTok creator."
            )
        response = await self._http.request(
            "POST",
            f"{_TIKTOK_BASE_URL}/v2/post/publish/video/init/",
            headers=self._headers(),
            json={
                "post_info": {
                    "title": payload.title,
                    "privacy_level": payload.privacy_level,
                    "disable_comment": payload.disable_comment,
                    "disable_duet": payload.disable_duet,
                    "disable_stitch": payload.disable_stitch,
                },
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "video_url": payload.video_url,
                },
            },
        )
        return _api_object(response.json())

    async def _creator_info(self) -> dict[str, Any]:
        response = await self._http.request(
            "POST",
            f"{_TIKTOK_BASE_URL}/v2/post/publish/creator_info/query/",
            headers=self._headers(),
            json={},
        )
        return _api_object(response.json())


def _api_object(value: Any) -> dict[str, Any]:
    result = _JSON_OBJECT.validate_python(value)
    error = result.get("error")
    if isinstance(error, dict) and error.get("code") not in {None, "ok"}:
        description = error.get("message") or error.get("code")
        raise ExternalAPIError(f"TikTok API error: {description}")
    return result


def _privacy_options(value: dict[str, Any]) -> set[str]:
    data = value.get("data")
    if not isinstance(data, dict):
        raise ExternalAPIError("TikTok returned invalid creator information.")
    options = data.get("privacy_level_options")
    if not isinstance(options, list) or not all(isinstance(item, str) for item in options):
        raise ExternalAPIError("TikTok did not return valid privacy options.")
    return set(options)
