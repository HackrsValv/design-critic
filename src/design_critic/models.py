"""Data models for design critique."""

from enum import Enum

from pydantic import BaseModel, Field


class Provider(str, Enum):
    """Supported AI providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


class InputType(str, Enum):
    """Type of design input."""

    IMAGE_URL = "image_url"
    IMAGE_BASE64 = "image_base64"
    HTML = "html"


class CritiqueRequest(BaseModel):
    """Request for design critique."""

    # Input - one of these must be provided
    image_url: str | None = Field(default=None, description="URL of image to critique")
    image_base64: str | None = Field(default=None, description="Base64 encoded image")
    html: str | None = Field(default=None, description="HTML to render and critique")

    # Provider configuration
    provider: Provider = Field(default=Provider.OPENAI, description="AI provider to use")
    api_key: str | None = Field(default=None, description="Your API key (BYOK)")

    # Critique options
    design_type: str = Field(
        default="email",
        description="Type of design: email, landing_page, dashboard, mobile_app, etc.",
    )
    focus_areas: list[str] = Field(
        default_factory=lambda: [
            "visual_hierarchy",
            "typography",
            "color_scheme",
            "whitespace",
            "cta_effectiveness",
            "readability",
        ],
        description="Areas to focus critique on",
    )
    custom_prompt: str | None = Field(
        default=None, description="Custom prompt to add to the critique"
    )


class ScoreItem(BaseModel):
    """Individual score for a design aspect."""

    category: str
    score: int = Field(ge=1, le=10)
    feedback: str
    suggestions: list[str] = Field(default_factory=list)


class CritiqueResponse(BaseModel):
    """Response from design critique."""

    overall_score: int = Field(ge=1, le=10)
    summary: str
    scores: list[ScoreItem]
    strengths: list[str]
    improvements: list[str]
    provider: Provider
    model: str


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    detail: str | None = None
