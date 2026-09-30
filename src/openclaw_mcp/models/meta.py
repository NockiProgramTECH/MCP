"""Validated request models for Meta and Instagram operations."""

from pydantic import BaseModel, ConfigDict, Field


class FacebookPagePost(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=63_206)
    link: str | None = Field(default=None, max_length=2_048)
    published: bool = True


class InstagramMediaContainer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    image_url: str | None = None
    video_url: str | None = None
    caption: str | None = Field(default=None, max_length=2_200)

    def validate_media(self) -> None:
        if (self.image_url is None) == (self.video_url is None):
            raise ValueError("Provide exactly one of image_url or video_url.")
