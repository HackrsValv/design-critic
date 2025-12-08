"""AI provider integrations for design critique."""

import json
import re
from abc import ABC, abstractmethod

import anthropic
import google.generativeai as genai
import openai

from .config import settings
from .models import CritiqueResponse, Provider, ScoreItem
from .prompts import SYSTEM_PROMPT, build_critique_prompt


class BaseProvider(ABC):
    """Base class for AI providers."""

    provider: Provider
    model: str

    @abstractmethod
    async def critique(
        self,
        image_base64: str,
        design_type: str,
        focus_areas: list[str],
        custom_prompt: str | None,
        api_key: str | None,
        base_url: str | None = None,
        model_override: str | None = None,
    ) -> CritiqueResponse:
        """Generate design critique from image."""
        pass

    def parse_response(self, content: str) -> dict:
        """Parse JSON response from model output."""
        # Try to extract JSON from the response
        # Models sometimes wrap JSON in markdown code blocks
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", content)
        if json_match:
            content = json_match.group(1)

        # Try direct JSON parse
        try:
            return json.loads(content.strip())
        except json.JSONDecodeError:
            # Try to find JSON object in the content
            json_match = re.search(r"\{[\s\S]*\}", content)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Could not parse JSON from response: {content[:500]}")


class OpenAIProvider(BaseProvider):
    """OpenAI GPT-4 Vision provider."""

    provider = Provider.OPENAI
    model = "gpt-4o"

    async def critique(
        self,
        image_base64: str,
        design_type: str,
        focus_areas: list[str],
        custom_prompt: str | None,
        api_key: str | None,
        base_url: str | None = None,
        model_override: str | None = None,
    ) -> CritiqueResponse:
        key = api_key or settings.openai_api_key
        if not key:
            raise ValueError("OpenAI API key required. Provide via api_key or OPENAI_API_KEY env var.")

        # Support custom base URL (for OpenRouter, proxies, etc.)
        url = base_url or settings.openai_base_url
        client = openai.AsyncOpenAI(api_key=key, base_url=url) if url else openai.AsyncOpenAI(api_key=key)

        # Use model override if provided
        model_to_use = model_override or self.model

        prompt = build_critique_prompt(design_type, focus_areas, custom_prompt)

        response = await client.chat.completions.create(
            model=model_to_use,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                        },
                    ],
                },
            ],
            max_tokens=2000,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        data = self.parse_response(content)

        return CritiqueResponse(
            overall_score=data["overall_score"],
            summary=data["summary"],
            scores=[ScoreItem(**s) for s in data["scores"]],
            strengths=data["strengths"],
            improvements=data["improvements"],
            provider=self.provider,
            model=model_to_use,
        )


class AnthropicProvider(BaseProvider):
    """Anthropic Claude Vision provider."""

    provider = Provider.ANTHROPIC
    model = "claude-sonnet-4-20250514"

    async def critique(
        self,
        image_base64: str,
        design_type: str,
        focus_areas: list[str],
        custom_prompt: str | None,
        api_key: str | None,
        base_url: str | None = None,
        model_override: str | None = None,
    ) -> CritiqueResponse:
        key = api_key or settings.anthropic_api_key
        if not key:
            raise ValueError(
                "Anthropic API key required. Provide via api_key or ANTHROPIC_API_KEY env var."
            )

        # Support custom base URL (for OpenRouter, proxies, etc.)
        url = base_url or settings.anthropic_base_url
        client = anthropic.AsyncAnthropic(api_key=key, base_url=url) if url else anthropic.AsyncAnthropic(api_key=key)

        # Use model override if provided
        model_to_use = model_override or self.model

        prompt = build_critique_prompt(design_type, focus_areas, custom_prompt)

        response = await client.messages.create(
            model=model_to_use,
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )

        content = response.content[0].text
        data = self.parse_response(content)

        return CritiqueResponse(
            overall_score=data["overall_score"],
            summary=data["summary"],
            scores=[ScoreItem(**s) for s in data["scores"]],
            strengths=data["strengths"],
            improvements=data["improvements"],
            provider=self.provider,
            model=model_to_use,
        )


class GoogleProvider(BaseProvider):
    """Google Gemini Vision provider."""

    provider = Provider.GOOGLE
    model = "gemini-1.5-flash"

    async def critique(
        self,
        image_base64: str,
        design_type: str,
        focus_areas: list[str],
        custom_prompt: str | None,
        api_key: str | None,
        base_url: str | None = None,
        model_override: str | None = None,
    ) -> CritiqueResponse:
        key = api_key or settings.google_api_key
        if not key:
            raise ValueError(
                "Google API key required. Provide via api_key or GOOGLE_API_KEY env var."
            )

        genai.configure(api_key=key)

        # Use model override if provided
        model_to_use = model_override or self.model
        model = genai.GenerativeModel(model_to_use)

        prompt = f"{SYSTEM_PROMPT}\n\n{build_critique_prompt(design_type, focus_areas, custom_prompt)}"

        # Gemini expects image as Part
        import base64

        image_bytes = base64.b64decode(image_base64)

        response = await model.generate_content_async(
            [
                prompt,
                {"mime_type": "image/jpeg", "data": image_bytes},
            ],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            ),
        )

        content = response.text
        data = self.parse_response(content)

        return CritiqueResponse(
            overall_score=data["overall_score"],
            summary=data["summary"],
            scores=[ScoreItem(**s) for s in data["scores"]],
            strengths=data["strengths"],
            improvements=data["improvements"],
            provider=self.provider,
            model=model_to_use,
        )


def get_provider(provider: Provider) -> BaseProvider:
    """Get provider instance by name."""
    providers = {
        Provider.OPENAI: OpenAIProvider(),
        Provider.ANTHROPIC: AnthropicProvider(),
        Provider.GOOGLE: GoogleProvider(),
    }
    return providers[provider]
