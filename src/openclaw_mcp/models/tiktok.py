"""Validated TikTok request models."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PrivacyLevel = Literal[
    "PUBLIC_TO_EVERYONE",
    "MUTUAL_FOLLOW_FRIENDS",
    "FOLLOWER_OF_CREATOR",
    "SELF_ONLY",
]


class TikTokVideoPublish(BaseModel):
    """Request for TikTok Content Posting API Direct Post from a public URL."""

    model_config = ConfigDict(extra="forbid")

    video_url: str = Field(min_length=1, max_length=2_048)
    title: str = Field(default="", max_length=2_200)
    privacy_level: PrivacyLevel = "SELF_ONLY"
    disable_comment: bool = False
    disable_duet: bool = False
    disable_stitch: bool = False
