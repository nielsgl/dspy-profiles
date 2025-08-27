from pydantic import BaseModel, ConfigDict, Field, RootModel


class LanguageModelSettings(BaseModel):
    """Schema for Language Model (LM) settings within a profile.

    This model validates the structure of the `[profile.<name>.lm]` section
    in the `profiles.toml` file.

    Attributes:
        model (str): The identifier for the language model (e.g., 'gpt-4o-mini').
        api_base (HttpUrl | None): The base URL for the API endpoint, required for
            some providers or local models.
        api_key (str | None): The API key for the service. It's recommended to set
            this via environment variables rather than directly in the file.
    """

    model: str | None = Field(None, description="The model name, e.g., 'gpt-4o-mini'.")
    api_base: str | None = Field(None, description="The API endpoint.")
    api_key: str | None = Field(None, description="The API key.")

    model_config = ConfigDict(extra="allow")


class RetrievalModelSettings(BaseModel):
    """Schema for Retrieval Model (RM) settings within a profile.

    This model validates the structure of the `[profile.<name>.rm]` section
    in the `profiles.toml` file.

    Attributes:
        model (str): The identifier for the retrieval model (e.g., 'colbertv2.0').
    """

    model: str = Field(..., description="The retrieval model name, e.g., 'colbertv2.0'.")

    model_config = ConfigDict(extra="allow")


class Profile(BaseModel):
    """Schema for a single profile configuration.

    This model represents the complete set of configurations for a single profile,
    including its potential parent profile and settings for LM, RM, and other
    custom sections.

    Attributes:
        extends (str | None): The name of a parent profile to inherit from.
        lm (LanguageModelSettings | None): Language model settings.
        rm (RetrievalModelSettings | None): Retrieval model settings.
    """

    extends: str | None = Field(None, description="The name of a parent profile to inherit from.")
    lm: LanguageModelSettings | None = Field(None, alias="lm")
    rm: RetrievalModelSettings | None = Field(None)

    model_config = ConfigDict(extra="allow")


class ProfilesFile(RootModel):
    """Schema for the entire `profiles.toml` file.

    This is the root model for validating the TOML configuration file. It directly
    represents the dictionary of profiles, where each key is a profile name.
    """

    root: dict[str, Profile]
