from typing import Any

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class LanguageModelSettings(BaseModel):
    """Schema for LM settings in a profile."""

    model: str = Field(..., description="The model name, e.g., 'gpt-4o-mini'.")
    api_base: HttpUrl | None = Field(None, description="The API endpoint.")
    api_key: str | None = Field(None, description="The API key.")
    # Allow any other settings to be passed through
    extra_attributes: dict[str, Any] = Field({}, alias="extra_attributes")

    model_config = ConfigDict(extra="allow")


class RetrievalModelSettings(BaseModel):
    """Schema for RM settings in a profile."""

    model: str = Field(..., description="The retrieval model name, e.g., 'colbertv2.0'.")
    # Allow any other settings to be passed through
    extra_attributes: dict[str, Any] = Field({}, alias="extra_attributes")

    model_config = ConfigDict(extra="allow")


class Profile(BaseModel):
    """Schema for a single dspy-profiles configuration."""

    extends: str | None = Field(None, description="The name of a parent profile to inherit from.")
    lm: LanguageModelSettings | None = None
    rm: RetrievalModelSettings | None = None
    # Allow other top-level sections like 'cache' etc.
    extra_sections: dict[str, Any] = Field({}, alias="extra_sections")

    @model_validator(mode="before")
    def _collect_extras(cls, values: dict[str, Any]) -> dict[str, Any]:
        """
        Pydantic doesn't have a clean way to handle dynamic top-level keys.
        This validator collects known fields and moves the rest into dedicated
        'extra' dictionaries to avoid validation errors.
        """
        known_fields = {
            "extends",
            "lm",
            "rm",
        }
        known_lm_fields = set(LanguageModelSettings.model_fields.keys())
        known_rm_fields = set(RetrievalModelSettings.model_fields.keys())

        # Handle extra attributes in lm
        if "lm" in values and isinstance(values["lm"], dict):
            lm_data = values["lm"]
            extra_lm = {k: v for k, v in lm_data.items() if k not in known_lm_fields}
            if extra_lm:
                lm_data["extra_attributes"] = extra_lm
                values["lm"] = {k: v for k, v in lm_data.items() if k in known_lm_fields}

        # Handle extra attributes in rm
        if "rm" in values and isinstance(values["rm"], dict):
            rm_data = values["rm"]
            extra_rm = {k: v for k, v in rm_data.items() if k not in known_rm_fields}
            if extra_rm:
                rm_data["extra_attributes"] = extra_rm
                values["rm"] = {k: v for k, v in rm_data.items() if k in known_rm_fields}

        # Handle extra top-level sections
        extra_sections = {k: v for k, v in values.items() if k not in known_fields}
        if extra_sections:
            values["extra_sections"] = extra_sections
            values = {k: v for k, v in values.items() if k in known_fields}

        return values

    model_config = ConfigDict(extra="forbid")


class ProfilesFile(BaseModel):
    """Schema for the entire profiles.toml file."""

    profiles: dict[str, Profile] = Field(..., description="A dictionary of all profiles.")
