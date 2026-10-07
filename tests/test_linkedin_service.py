import httpx
import pytest
from pydantic import SecretStr

from openclaw_mcp.config import Settings
from openclaw_mcp.core.errors import ConfigurationError
from openclaw_mcp.core.http import HttpClient
from openclaw_mcp.models.linkedin import LinkedInPostCreate
from openclaw_mcp.services.linkedin import LinkedInService


@pytest.mark.asyncio
async def test_linkedin_get_profile_uses_oidc_userinfo() -> None:
    settings = Settings(linkedin_access_token=SecretStr("linkedin-token"), max_retries=0)

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v2/userinfo"
        assert request.headers["authorization"] == "Bearer linkedin-token"
        return httpx.Response(200, json={"sub": "member-1", "name": "Member"}, request=request)

    client = HttpClient(settings, allowed_hosts={"api.linkedin.com"})
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    service = LinkedInService(settings, client)
    try:
        assert await service.get_profile() == {"sub": "member-1", "name": "Member"}
    finally:
        await service.aclose()


@pytest.mark.asyncio
async def test_linkedin_create_post_returns_restli_id() -> None:
    settings = Settings(linkedin_access_token=SecretStr("linkedin-token"), max_retries=0)

    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v2/userinfo":
            return httpx.Response(200, json={"sub": "member-1"}, request=request)
        assert request.url.path == "/rest/posts"
        assert request.headers["linkedin-version"] == "202601"
        return httpx.Response(
            201, headers={"x-restli-id": "urn:li:share:123"}, request=request
        )

    client = HttpClient(settings, allowed_hosts={"api.linkedin.com"})
    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    service = LinkedInService(settings, client)
    try:
        result = await service.create_post(LinkedInPostCreate(commentary="Hello MCP"))
        assert result == {"id": "urn:li:share:123", "author": "urn:li:person:member-1"}
    finally:
        await service.aclose()


@pytest.mark.asyncio
async def test_linkedin_requires_configuration() -> None:
    service = LinkedInService(Settings(linkedin_access_token=None, max_retries=0))
    with pytest.raises(ConfigurationError, match="LINKEDIN_ACCESS_TOKEN"):
        await service.get_profile()
    await service.aclose()
