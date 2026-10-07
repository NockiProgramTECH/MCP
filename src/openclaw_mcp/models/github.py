"""GitHub request and response models."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GitHubIssueCreate(BaseModel):
    """Payload for creating a real GitHub issue."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=256)
    body: str | None = Field(default=None, max_length=65_536)
    labels: list[str] = Field(default_factory=list, max_length=50)
    assignees: list[str] = Field(default_factory=list, max_length=50)


class GitHubRepositoryCreate(BaseModel):
    """Payload for creating a real repository in the authenticated account."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9._-]+$")
    description: str | None = Field(default=None, max_length=350)
    private: bool = False
    auto_init: bool = False


class GitHubResult(BaseModel):
    """Validated envelope for a GitHub JSON response."""

    model_config = ConfigDict(extra="allow")

    data: dict[str, Any] | list[Any]
