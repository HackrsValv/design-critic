"""Configuration and settings."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # Optional default API keys (users can override with BYOK)
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    google_api_key: str | None = Field(default=None, alias="GOOGLE_API_KEY")

    # Optional custom base URLs (for OpenRouter, proxies, etc.)
    openai_base_url: str | None = Field(default=None, alias="OPENAI_BASE_URL")
    anthropic_base_url: str | None = Field(default=None, alias="ANTHROPIC_BASE_URL")

    model_config = {"env_prefix": "DESIGN_CRITIC_", "env_file": ".env"}


settings = Settings()
