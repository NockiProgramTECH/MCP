"""MCP tools for Facebook Pages and Instagram Graph API."""

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ..models.meta import FacebookPagePost, InstagramMediaContainer
from ..services.meta import MetaService

ObjectId = Annotated[str, Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9_-]+$")]
Limit = Annotated[int, Field(ge=1, le=100)]


def register_meta_tools(server: FastMCP, service: MetaService) -> None:
    """Register Facebook and Instagram tools."""

    @server.tool(description="Lists Facebook Pages accessible with the configured Meta token.")
    async def facebook_get_pages() -> list[object]:
        return await service.get_pages()

    @server.tool(description="Gets public details for a Facebook Page.")
    async def facebook_get_page(page_id: ObjectId) -> dict[str, object]:
        return await service.get_page(page_id)

    @server.tool(
        description=(
            "Creates a real post on a Facebook Page using the official Meta API. "
            "This operation modifies external state and requires explicit user intent."
        )
    )
    async def facebook_create_page_post(
        page_id: ObjectId,
        message: Annotated[str, Field(min_length=1, max_length=63_206)],
        link: Annotated[str | None, Field(default=None, max_length=2_048)] = None,
        published: bool = True,
    ) -> dict[str, object]:
        return await service.create_page_post(
            page_id, FacebookPagePost(message=message, link=link, published=published)
        )

    @server.tool(description="Lists recent posts published on a Facebook Page.")
    async def facebook_get_page_posts(page_id: ObjectId, limit: Limit = 25) -> list[object]:
        return await service.get_page_posts(page_id, limit=limit)

    @server.tool(description="Gets an Instagram professional account profile.")
    async def instagram_get_profile(instagram_user_id: ObjectId) -> dict[str, object]:
        return await service.get_instagram_profile(instagram_user_id)

    @server.tool(description="Lists media from an Instagram professional account.")
    async def instagram_get_media(
        instagram_user_id: ObjectId, limit: Limit = 25
    ) -> list[object]:
        return await service.get_instagram_media(instagram_user_id, limit=limit)

    @server.tool(
        description=(
            "Creates an Instagram media container from a publicly reachable HTTPS "
            "image or video URL. This starts a real publishing workflow but does "
            "not publish the media yet."
        )
    )
    async def instagram_create_media_container(
        instagram_user_id: ObjectId,
        image_url: Annotated[str | None, Field(default=None, max_length=2_048)] = None,
        video_url: Annotated[str | None, Field(default=None, max_length=2_048)] = None,
        caption: Annotated[str | None, Field(default=None, max_length=2_200)] = None,
    ) -> dict[str, object]:
        payload = InstagramMediaContainer(
            image_url=image_url, video_url=video_url, caption=caption
        )
        return await service.create_instagram_media_container(instagram_user_id, payload)

    @server.tool(
        description=(
            "Publishes an existing Instagram media container. "
            "This operation publishes real external content and requires explicit user intent."
        )
    )
    async def instagram_publish_media(
        instagram_user_id: ObjectId, creation_id: ObjectId
    ) -> dict[str, object]:
        return await service.publish_instagram_media(instagram_user_id, creation_id)
