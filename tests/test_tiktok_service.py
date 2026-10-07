import httpx
import pytest
from pydantic import SecretStr

from openclaw_mcp.config import Settings
from openclaw_mcp.core.errors import ConfigurationError, ExternalAPIError
from openclaw_mcp.core.http import HttpClient
from openclaw_mcp.models.tiktok import TikTokVideoPublish
from openclaw_mcp.services.tiktok import TikTokService


@pytest.mark.asyncio
async def test_tiktok_get_user_uses_bearer_token() -> None:
    settings = Settings(tiktok_access_token=SecretStr("tiktok-token"), max_retries=0)

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer tiktok-token"
        return httpx.Response(200, json={"data": {"display_name": "creator"}}, request=request)

    client = HttpClient(settings, allowed_hosts={"open.tiktokapis.com"})
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    service = TikTokService(settings, client)
    try:
        assert await service.get_user() == {"data": {"display_name": "creator"}}
    finally:
        await service.aclose()


@pytest.mark.asyncio
async def test_tiktok_publish_initializes_after_creator_info() -> None:
    settings = Settings(tiktok_access_token=SecretStr("tiktok-token"), max_retries=0)
    calls: list[str] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if request.url.path.endswith("creator_info/query/"):
            return httpx.Response(
                200,
                json={"data": {"privacy_level_options": ["SELF_ONLY"]}},
                request=request,
            )
        return httpx.Response(200, json={"data": {"publish_id": "pub-1"}}, request=request)

    client = HttpClient(settings, allowed_hosts={"open.tiktokapis.com"})
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    service = TikTokService(settings, client)
    try:
        result = await service.publish_video(
            TikTokVideoPublish(video_url="https://media.example.com/video.mp4")
        )
        assert result == {"data": {"publish_id": "pub-1"}}
        assert calls == [
            "/v2/post/publish/creator_info/query/",
            "/v2/post/publish/video/init/",
        ]
    finally:
        await service.aclose()


@pytest.mark.asyncio
async def test_tiktok_requires_configuration() -> None:
    service = TikTokService(Settings(tiktok_access_token=None, max_retries=0))
    with pytest.raises(ConfigurationError, match="TIKTOK_ACCESS_TOKEN"):
        await service.get_user()
    await service.aclose()


@pytest.mark.asyncio
async def test_tiktok_rejects_disallowed_privacy_level() -> None:
    settings = Settings(tiktok_access_token=SecretStr("tiktok-token"), max_retries=0)

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"data": {"privacy_level_options": ["SELF_ONLY"]}},
            request=request,
        )

    client = HttpClient(settings, allowed_hosts={"open.tiktokapis.com"})
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    service = TikTokService(settings, client)
    try:
        with pytest.raises(ExternalAPIError, match="privacy level"):
            await service.publish_video(
                TikTokVideoPublish(
                    video_url="https://media.example.com/video.mp4",
                    privacy_level="PUBLIC_TO_EVERYONE",
                )
            )
    finally:
        await service.aclose()
