"""GitHub API service layer."""

from __future__ import annotations

from typing import Any

from pydantic import TypeAdapter

from ..config import Settings
from ..core.errors import ConfigurationError, ExternalAPIError
from ..core.http import HttpClient
from ..models.github import GitHubIssueCreate, GitHubRepositoryCreate

_GITHUB_HOSTS = frozenset({"api.github.com"})
_GITHUB_BASE_URL = "https://api.github.com"
_JSON_OBJECT = TypeAdapter(dict[str, Any])
_JSON_LIST = TypeAdapter(list[Any])


class GitHubService:
    """Thin, typed wrapper around the official GitHub REST API."""

    def __init__(self, settings: Settings, http_client: HttpClient | None = None) -> None:
        self._settings = settings
        self._http = http_client or HttpClient(settings, allowed_hosts=_GITHUB_HOSTS)

    async def aclose(self) -> None:
        await self._http.aclose()

    def _headers(self) -> dict[str, str]:
        token = self._settings.github_token
        if token is None:
            raise ConfigurationError(
                "GitHub is not configured. Set GITHUB_TOKEN in the environment."
            )
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token.get_secret_value()}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_user(self) -> dict[str, Any]:
        return await self._get_object("/user")

    async def list_repositories(
        self, *, page: int = 1, per_page: int = 30, visibility: str = "all"
    ) -> list[Any]:
        response = await self._http.request(
            "GET",
            f"{_GITHUB_BASE_URL}/user/repos",
            headers=self._headers(),
            params={
                "page": page,
                "per_page": per_page,
                "visibility": visibility,
                "sort": "updated",
            },
        )
        return _JSON_LIST.validate_python(response.json())

    async def get_repository(self, owner: str, repo: str) -> dict[str, Any]:
        return await self._get_object(f"/repos/{_path_part(owner)}/{_path_part(repo)}")

    async def create_issue(
        self, owner: str, repo: str, payload: GitHubIssueCreate
    ) -> dict[str, Any]:
        return await self._post_object(
            f"/repos/{_path_part(owner)}/{_path_part(repo)}/issues",
            payload.model_dump(exclude_none=True),
        )

    async def list_issues(
        self,
        owner: str,
        repo: str,
        *,
        state: str = "open",
        page: int = 1,
        per_page: int = 30,
    ) -> list[Any]:
        response = await self._http.request(
            "GET",
            f"{_GITHUB_BASE_URL}/repos/{_path_part(owner)}/{_path_part(repo)}/issues",
            headers=self._headers(),
            params={"state": state, "page": page, "per_page": per_page},
        )
        return _JSON_LIST.validate_python(response.json())

    async def create_repository(self, payload: GitHubRepositoryCreate) -> dict[str, Any]:
        return await self._post_object("/user/repos", payload.model_dump(exclude_none=True))

    async def _get_object(self, path: str) -> dict[str, Any]:
        response = await self._http.request(
            "GET", f"{_GITHUB_BASE_URL}{path}", headers=self._headers()
        )
        return _JSON_OBJECT.validate_python(response.json())

    async def _post_object(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = await self._http.request(
            "POST", f"{_GITHUB_BASE_URL}{path}", headers=self._headers(), json=payload
        )
        try:
            return _JSON_OBJECT.validate_python(response.json())
        except (TypeError, ValueError) as exc:
            raise ExternalAPIError("GitHub returned an invalid JSON response.") from exc


def _path_part(value: str) -> str:
    """Validate a repository path component before URL interpolation."""
    if not value or value in {".", ".."} or "/" in value or "\\" in value:
        raise ValueError("GitHub owner and repository names must be a single path component.")
    return value
