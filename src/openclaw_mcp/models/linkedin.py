"""Validated LinkedIn request models."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LinkedInPostCreate(BaseModel):
    """Payload for creating an organic LinkedIn text post."""

    model_config = ConfigDict(extra="forbid")

    commentary: str = Field(min_length=1, max_length=3_000)
    author_urn: str | None = Field(default=None, max_length=200)
    visibility: Literal["PUBLIC", "CONNECTIONS"] = "PUBLIC"
