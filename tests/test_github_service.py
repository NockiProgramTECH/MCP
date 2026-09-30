import httpx
import pytest
from pydantic import SecretStr

from openclaw_mcp.config import Settings
from openclaw_mcp.core.errors import ConfigurationError
from openclaw_mcp.core.http import HttpClient
from openclaw_mcp.models.github import GitHubIssueCreate
from openclaw_mcp.services.github import GitHubService


@pytest.mark.asyncio
async def test_github_get_user_sends_bearer_token() -> None:
    settings = Settings(github_token=SecretStr("test-token"), max_retries=0)
    client = HttpClient(settings, allowed_hosts={"api.github.com"})
    seen: dict[str, str] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        seen["authorization"] = request.headers["authorization"]
        seen["version"] = request.headers["x-github-api-version"]
        return httpx.Response(200, json={"login": "octocat"}, request=request)

    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    service = GitHubService(settings, client)
    try:
        result = await service.get_user()
        assert result == {"login": "octocat"}
        assert seen == {"authorization": "Bearer test-token", "version": "2022-11-28"}
    finally:
        await service.aclose()


@pytest.mark.asyncio
async def test_github_create_issue_posts_expected_payload() -> None:
    settings = Settings(github_token=SecretStr("test-token"), max_retries=0)
    client = HttpClient(settings, allowed_hosts={"api.github.com"})
    seen: dict[str, object] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["url"] = str(request.url)
        seen["json"] = request.content
        return httpx.Response(201, json={"number": 12}, request=request)

    client._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    service = GitHubService(settings, client)
    try:
        result = await service.create_issue(
            "owner", "repo", GitHubIssueCreate(title="Bug", labels=["bug"])
        )
        assert result == {"number": 12}
        assert seen["method"] == "POST"
        assert seen["url"] == "https://api.github.com/repos/owner/repo/issues"
        assert b'"title":"Bug"' in seen["json"]  # type: ignore[operator]
    finally:
        await service.aclose()


@pytest.mark.asyncio
async def test_github_requires_configuration() -> None:
    settings = Settings(max_retries=0)
    service = GitHubService(settings)
    with pytest.raises(ConfigurationError, match="GITHUB_TOKEN"):
        await service.get_user()
    await service.aclose()
