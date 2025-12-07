"""FastAPI application for design critique service."""

import base64
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from .config import settings
from .models import CritiqueRequest, CritiqueResponse, ErrorResponse, Provider
from .providers import get_provider
from .renderer import optimize_image_for_api, render_html_to_base64


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup: install playwright browsers if needed
    import subprocess
    try:
        subprocess.run(
            ["playwright", "install", "chromium"],
            check=True,
            capture_output=True,
        )
    except Exception:
        pass  # May already be installed
    yield


app = FastAPI(
    title="Design Critic",
    description="AI-powered design critique tool with BYOK (Bring Your Own Key) support",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates
templates_dir = Path(__file__).parent / "templates"
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the web UI."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


@app.post("/api/critique", response_model=CritiqueResponse, responses={400: {"model": ErrorResponse}})
async def critique_design(request: CritiqueRequest):
    """
    Critique a design using AI vision models.

    Supports three input types:
    - image_url: URL of an image to analyze
    - image_base64: Base64 encoded image data
    - html: HTML content to render and analyze

    BYOK: Provide your own API key via the `api_key` field.
    """
    # Validate input - exactly one must be provided
    inputs = [request.image_url, request.image_base64, request.html]
    provided = sum(1 for x in inputs if x is not None)

    if provided == 0:
        raise HTTPException(
            status_code=400,
            detail="Must provide one of: image_url, image_base64, or html",
        )
    if provided > 1:
        raise HTTPException(
            status_code=400,
            detail="Provide only one of: image_url, image_base64, or html",
        )

    try:
        # Get image as base64
        if request.html:
            # Render HTML to screenshot
            image_base64 = await render_html_to_base64(
                request.html,
                width=600 if request.design_type == "email" else 1280,
            )
        elif request.image_url:
            # Fetch image from URL
            async with httpx.AsyncClient() as client:
                response = await client.get(request.image_url, follow_redirects=True)
                response.raise_for_status()
                image_base64 = base64.b64encode(response.content).decode("utf-8")
        else:
            image_base64 = request.image_base64

        # Optimize image for API
        image_base64 = optimize_image_for_api(image_base64)

        # Get provider and run critique
        provider = get_provider(request.provider)
        result = await provider.critique(
            image_base64=image_base64,
            design_type=request.design_type,
            focus_areas=request.focus_areas,
            custom_prompt=request.custom_prompt,
            api_key=request.api_key,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Critique failed: {str(e)}")


@app.get("/api/providers")
async def list_providers():
    """List available AI providers and their status."""
    return {
        "providers": [
            {
                "id": Provider.OPENAI.value,
                "name": "OpenAI GPT-4o",
                "has_default_key": settings.openai_api_key is not None,
            },
            {
                "id": Provider.ANTHROPIC.value,
                "name": "Anthropic Claude",
                "has_default_key": settings.anthropic_api_key is not None,
            },
            {
                "id": Provider.GOOGLE.value,
                "name": "Google Gemini",
                "has_default_key": settings.google_api_key is not None,
            },
        ]
    }


def main():
    """Run the server."""
    import uvicorn

    uvicorn.run(
        "design_critic.api:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
