"""MCP tools for the official TikTok API."""

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ..models.tiktok import TikTokVideoPublish
from ..services.tiktok import TikTokService

Count = Annotated[int, Field(ge=1, le=20)]
Cursor = Annotated[int, Field(ge=0)]


def register_tiktok_tools(server: FastMCP, service: TikTokService) -> None:
    """Register TikTok read and publishing tools."""

    @server.tool(description="Gets the authenticated TikTok user's basic profile information.")
    async def tiktok_get_user() -> dict[str, object]:
        return await service.get_user()

    @server.tool(description="Lists public videos for the authenticated TikTok user.")
    async def tiktok_get_videos(
        max_count: Count = 20, cursor: Cursor | None = None
    ) -> dict[str, object]:
        return await service.get_videos(max_count=max_count, cursor=cursor)

    @server.tool(
        description=(
            "Initializes a real TikTok Direct Post from a public HTTPS video URL. "
            "This is an external publishing action requiring explicit user intent, "
            "TikTok approval for video.publish, and a verified source domain."
        )
    )
    async def tiktok_publish_video(
        video_url: Annotated[str, Field(min_length=1, max_length=2_048)],
        title: Annotated[str, Field(default="", max_length=2_200)] = "",
        privacy_level: Annotated[
            str,
            Field(
                pattern=(
                    r"^(PUBLIC_TO_EVERYONE|MUTUAL_FOLLOW_FRIENDS|"
                    r"FOLLOWER_OF_CREATOR|SELF_ONLY)$"
                )
            ),
        ] = "SELF_ONLY",
        disable_comment: bool = False,
        disable_duet: bool = False,
        disable_stitch: bool = False,
    ) -> dict[str, object]:
        payload = TikTokVideoPublish(
            video_url=video_url,
            title=title,
            privacy_level=privacy_level,
            disable_comment=disable_comment,
            disable_duet=disable_duet,
            disable_stitch=disable_stitch,
        )
        return await service.publish_video(payload)
