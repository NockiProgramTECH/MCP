"""MCP tools for LinkedIn."""

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ..models.linkedin import LinkedInPostCreate
from ..services.linkedin import LinkedInService

AuthorUrn = Annotated[str, Field(min_length=1, max_length=200)]
Start = Annotated[int, Field(ge=0, le=10_000)]
Count = Annotated[int, Field(ge=1, le=100)]


def register_linkedin_tools(server: FastMCP, service: LinkedInService) -> None:
    """Register LinkedIn profile and posts tools."""

    @server.tool(description="Gets the authenticated LinkedIn member's OpenID Connect profile.")
    async def linkedin_get_profile() -> dict[str, object]:
        return await service.get_profile()

    @server.tool(
        description=(
            "Creates a real organic text post on a LinkedIn member or organization. "
            "This operation modifies external state and requires explicit user intent. "
            "Organization posts require the appropriate LinkedIn approval and admin role."
        )
    )
    async def linkedin_create_post(
        commentary: Annotated[str, Field(min_length=1, max_length=3_000)],
        author_urn: AuthorUrn | None = None,
        visibility: Annotated[str, Field(pattern=r"^(PUBLIC|CONNECTIONS)$")] = "PUBLIC",
    ) -> dict[str, object]:
        payload = LinkedInPostCreate(
            commentary=commentary, author_urn=author_urn, visibility=visibility
        )
        return await service.create_post(payload)

    @server.tool(
        description=(
            "Lists posts by a LinkedIn author. Reading member posts requires LinkedIn's "
            "restricted read permission; organization reads require the organization scope."
        )
    )
    async def linkedin_get_posts(
        author_urn: AuthorUrn, start: Start = 0, count: Count = 10
    ) -> dict[str, object]:
        return await service.get_posts(author_urn, start=start, count=count)
