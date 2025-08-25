from typing import Any

from pydantic import BaseModel, Field, RootModel


class LMConfig(BaseModel):
    """Pydantic model for LM configuration."""

    model: str
    temperature: float | None = None
    max_tokens: int | None = None
    top_p: float | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    stop: str | None = None


class RMConfig(BaseModel):
    """Pydantic model for RM configuration."""

    # This is a placeholder. We'll need to define the actual
    # fields for a retrieval model when we add support for it.
    url: str


class Profile(BaseModel):
    """Pydantic model for a single profile."""

    lm: LMConfig | None = None
    rm: RMConfig | None = None
    settings: dict[str, Any] = Field(default_factory=dict)


class Profiles(RootModel[dict[str, Profile]]):
    """Pydantic model for the entire profiles file."""

    pass
