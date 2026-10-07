import httpx
import pytest
from pydantic import SecretStr

from openclaw_mcp.config import Settings
from openclaw_mcp.core.errors import ConfigurationError, ExternalAPIError
from openclaw_mcp.core.http import HttpClient
from openclaw_mcp.models.meta import InstagramMediaContainer
from openclaw_mcp.services.meta import MetaService


@pytest.mark.asyncio
async def test_meta_pages_redact_page_access_tokens() -> None:
    settings = Settings(meta_access_token=SecretStr("meta-token"), max_retries=0)

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == "Bearer meta-token"
        return httpx.Response(
            200,
            json={"data": [{"id": "123", "name": "Page", "access_token": "secret"}]},
            request=request,
        )

    client = HttpClient(settings, allowed_hosts={"graph.facebook.com"})
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    service = MetaService(settings, client)
    try:
        result = await service.get_pages()
        assert result == [{"id": "123", "name": "Page"}]
    finally:
        await service.aclose()


@pytest.mark.asyncio
async def test_instagram_container_rejects_private_url() -> None:
    settings = Settings(instagram_access_token=SecretStr("instagram-token"), max_retries=0)
    service = MetaService(settings)
    with pytest.raises(ExternalAPIError, match="Private"):
        await service.create_instagram_media_container(
            "17841400000000000",
            InstagramMediaContainer(image_url="https://127.0.0.1/image.jpg"),
        )
    await service.aclose()


@pytest.mark.asyncio
async def test_meta_requires_configuration() -> None:
    service = MetaService(Settings(max_retries=0))
    with pytest.raises(ConfigurationError, match="META_ACCESS_TOKEN"):
        await service.get_pages()
    await service.aclose()
