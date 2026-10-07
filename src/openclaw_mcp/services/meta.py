"""Official Meta Graph API service for Facebook Pages and Instagram."""

from __future__ import annotations

from typing import Any

from pydantic import TypeAdapter

from ..config import Settings
from ..core.errors import ConfigurationError, ExternalAPIError
from ..core.http import HttpClient
from ..core.security import validate_public_media_url
from ..models.meta import FacebookPagePost, InstagramMediaContainer

_META_HOSTS = frozenset({"graph.facebook.com"})
_JSON_OBJECT = TypeAdapter(dict[str, Any])
_JSON_LIST = TypeAdapter(list[Any])
_SECRET_KEYS = {"access_token", "appsecret_proof", "token"}


class MetaService:
    """Wrapper around the official Meta Graph API.

    Facebook operations use META_ACCESS_TOKEN. Page write operations obtain a
    Page access token internally from /me/accounts and never return it.
    Instagram operations use INSTAGRAM_ACCESS_TOKEN and target professional
    Instagram accounts only.
    """

    def __init__(self, settings: Settings, http_client: HttpClient | None = None) -> None:
        self._settings = settings
        self._http = http_client or HttpClient(settings, allowed_hosts=_META_HOSTS)

    async def aclose(self) -> None:
        await self._http.aclose()

    @property
    def _base_url(self) -> str:
        return f"https://graph.facebook.com/{self._settings.meta_graph_api_version}"

    def _meta_headers(self) -> dict[str, str]:
        token = self._settings.meta_access_token
        if token is None:
            raise ConfigurationError(
                "Meta is not configured. Set META_ACCESS_TOKEN in the environment."
            )
        return {"Authorization": f"Bearer {token.get_secret_value()}"}

    def _instagram_headers(self) -> dict[str, str]:
        token = self._settings.instagram_access_token
        if token is None:
            raise ConfigurationError(
                "Instagram is not configured. Set INSTAGRAM_ACCESS_TOKEN in the environment."
            )
        return {"Authorization": f"Bearer {token.get_secret_value()}"}

    async def get_pages(self) -> list[Any]:
        response = await self._http.request(
            "GET",
            f"{self._base_url}/me/accounts",
            headers=self._meta_headers(),
            params={"fields": "id,name,tasks", "limit": 100},
        )
        return _safe_list(response.json())

    async def get_page(self, page_id: str) -> dict[str, Any]:
        response = await self._http.request(
            "GET",
            f"{self._base_url}/{_id(page_id)}",
            headers=self._meta_headers(),
            params={"fields": "id,name,about,fan_count,link"},
        )
        return _safe_object(response.json())

    async def create_page_post(self, page_id: str, payload: FacebookPagePost) -> dict[str, Any]:
        page_token = await self._get_page_token(page_id)
        params: dict[str, Any] = {"message": payload.message, "published": payload.published}
        if payload.link is not None:
            validate_public_media_url(payload.link)
            params["link"] = payload.link
        response = await self._http.request(
            "POST", f"{self._base_url}/{_id(page_id)}/feed", headers=page_token, params=params
        )
        return _safe_object(response.json())

    async def get_page_posts(self, page_id: str, *, limit: int = 25) -> list[Any]:
        response = await self._http.request(
            "GET",
            f"{self._base_url}/{_id(page_id)}/feed",
            headers=self._meta_headers(),
            params={
                "fields": "id,message,created_time,permalink_url,is_published",
                "limit": limit,
            },
        )
        return _safe_list(response.json())

    async def get_instagram_profile(self, instagram_user_id: str) -> dict[str, Any]:
        response = await self._http.request(
            "GET",
            f"{self._base_url}/{_id(instagram_user_id)}",
            headers=self._instagram_headers(),
            params={"fields": "id,username,name,biography,followers_count,media_count"},
        )
        return _safe_object(response.json())

    async def get_instagram_media(self, instagram_user_id: str, *, limit: int = 25) -> list[Any]:
        response = await self._http.request(
            "GET",
            f"{self._base_url}/{_id(instagram_user_id)}/media",
            headers=self._instagram_headers(),
            params={
                "fields": "id,caption,media_type,media_url,permalink,timestamp,thumbnail_url",
                "limit": limit,
            },
        )
        return _safe_list(response.json())

    async def create_instagram_media_container(
        self, instagram_user_id: str, payload: InstagramMediaContainer
    ) -> dict[str, Any]:
        payload.validate_media()
        params: dict[str, Any] = {}
        if payload.image_url is not None:
            validate_public_media_url(payload.image_url)
            params["image_url"] = payload.image_url
        if payload.video_url is not None:
            validate_public_media_url(payload.video_url)
            params["video_url"] = payload.video_url
            params["media_type"] = "VIDEO"
        if payload.caption is not None:
            params["caption"] = payload.caption
        response = await self._http.request(
            "POST",
            f"{self._base_url}/{_id(instagram_user_id)}/media",
            headers=self._instagram_headers(),
            params=params,
        )
        return _safe_object(response.json())

    async def publish_instagram_media(
        self, instagram_user_id: str, creation_id: str
    ) -> dict[str, Any]:
        response = await self._http.request(
            "POST",
            f"{self._base_url}/{_id(instagram_user_id)}/media_publish",
            headers=self._instagram_headers(),
            params={"creation_id": _id(creation_id)},
        )
        return _safe_object(response.json())

    async def _get_page_token(self, page_id: str) -> dict[str, str]:
        response = await self._http.request(
            "GET",
            f"{self._base_url}/me/accounts",
            headers=self._meta_headers(),
            params={"fields": "id,access_token", "limit": 100},
        )
        data = _JSON_LIST.validate_python(response.json())
        for page in data:
            if isinstance(page, dict) and page.get("id") == page_id:
                token = page.get("access_token")
                if isinstance(token, str) and token:
                    return {"Authorization": f"Bearer {token}"}
        raise ExternalAPIError("No usable Page access token was found for this Page.")


def _id(value: str) -> str:
    valid_chars = all(char.isalnum() or char in "_-" for char in value)
    if not value or len(value) > 128 or not valid_chars:
        raise ValueError("The external object ID is invalid.")
    return value


def _safe_object(value: Any) -> dict[str, Any]:
    result = _JSON_OBJECT.validate_python(value)
    return _redact(result)


def _safe_list(value: Any) -> list[Any]:
    if isinstance(value, dict) and isinstance(value.get("data"), list):
        value = value["data"]
    result = _JSON_LIST.validate_python(value)
    return [_redact(item) for item in result]


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _redact(item)
            for key, item in value.items()
            if key.lower() not in _SECRET_KEYS
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value
