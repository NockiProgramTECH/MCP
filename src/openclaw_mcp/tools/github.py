"""MCP tools exposing the GitHub service."""

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ..models.github import GitHubIssueCreate, GitHubRepositoryCreate
from ..services.github import GitHubService

Page = Annotated[int, Field(ge=1, le=10_000)]
PerPage = Annotated[int, Field(ge=1, le=100)]
Name = Annotated[str, Field(min_length=1, max_length=100)]


def register_github_tools(server: FastMCP, service: GitHubService) -> None:
    """Register all GitHub tools on an MCP server instance."""

    @server.tool(description="Gets the authenticated GitHub user's public account information.")
    async def github_get_user() -> dict[str, object]:
        return await service.get_user()

    @server.tool(description="Lists repositories accessible to the authenticated GitHub user.")
    async def github_list_repositories(
        page: Page = 1,
        per_page: PerPage = 30,
        visibility: Annotated[str, Field(pattern=r"^(all|public|private)$")] = "all",
    ) -> list[object]:
        return await service.list_repositories(page=page, per_page=per_page, visibility=visibility)

    @server.tool(description="Gets details for one GitHub repository by owner and repository name.")
    async def github_get_repository(owner: Name, repo: Name) -> dict[str, object]:
        return await service.get_repository(owner, repo)

    @server.tool(
        description=(
            "Creates a real GitHub issue in the specified repository. "
            "This operation modifies external state and requires explicit user intent."
        )
    )
    async def github_create_issue(
        owner: Name, repo: Name, title: Annotated[str, Field(min_length=1, max_length=256)],
        body: Annotated[str | None, Field(default=None, max_length=65_536)] = None,
        labels: Annotated[list[str], Field(max_length=50)] | None = None,
        assignees: Annotated[list[str], Field(max_length=50)] | None = None,
    ) -> dict[str, object]:
        payload = GitHubIssueCreate(
            title=title, body=body, labels=labels or [], assignees=assignees or []
        )
        return await service.create_issue(owner, repo, payload)

    @server.tool(
        description="Lists issues for a GitHub repository without modifying external state."
    )
    async def github_list_issues(
        owner: Name,
        repo: Name,
        state: Annotated[str, Field(pattern=r"^(open|closed|all)$")] = "open",
        page: Page = 1,
        per_page: PerPage = 30,
    ) -> list[object]:
        return await service.list_issues(owner, repo, state=state, page=page, per_page=per_page)

    @server.tool(
        description=(
            "Creates a real GitHub repository in the authenticated account. "
            "This operation modifies external state and requires explicit user intent."
        )
    )
    async def github_create_repository(
        name: Annotated[str, Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9._-]+$")],
        description: Annotated[str | None, Field(default=None, max_length=350)] = None,
        private: bool = False,
        auto_init: bool = False,
    ) -> dict[str, object]:
        payload = GitHubRepositoryCreate(
            name=name, description=description, private=private, auto_init=auto_init
        )
        return await service.create_repository(payload)
