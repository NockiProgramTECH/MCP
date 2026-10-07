import httpx
import pytest

from openclaw_mcp.config import Settings
from openclaw_mcp.core.errors import AuthenticationError, RateLimitError
from openclaw_mcp.core.http import HttpClient


@pytest.mark.asyncio
async def test_http_client_maps_authentication_error() -> None:
    settings = Settings(http_timeout_seconds=1, max_retries=0)
    client = HttpClient(settings, allowed_hosts={"api.example.com"})

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, request=request)

    transport = httpx.MockTransport(handler)
    client._client = httpx.AsyncClient(transport=transport)
    try:
        with pytest.raises(AuthenticationError):
            await client.request("GET", "https://api.example.com/resource")
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_http_client_maps_rate_limit_without_retry() -> None:
    settings = Settings(http_timeout_seconds=1, max_retries=0)
    client = HttpClient(settings, allowed_hosts={"api.example.com"})

    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, headers={"retry-after": "4"}, request=request)

    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(RateLimitError) as caught:
            await client.request("GET", "https://api.example.com/resource")
        assert caught.value.retry_after == 4
    finally:
        await client.aclose()
