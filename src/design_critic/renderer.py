"""HTML to screenshot rendering using Playwright."""

import asyncio
import base64
from io import BytesIO

from PIL import Image
from playwright.async_api import async_playwright


async def render_html_to_base64(
    html: str,
    width: int = 600,
    full_page: bool = True,
    device_scale_factor: float = 2.0,
) -> str:
    """
    Render HTML content to a base64 encoded PNG image.

    Args:
        html: HTML content to render
        width: Viewport width in pixels (600 is typical for email)
        full_page: Capture full scrollable page or just viewport
        device_scale_factor: Scale factor for retina-quality screenshots

    Returns:
        Base64 encoded PNG image string
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": width, "height": 800},
            device_scale_factor=device_scale_factor,
        )

        # Set content and wait for images to load
        await page.set_content(html, wait_until="networkidle")

        # Take screenshot
        screenshot_bytes = await page.screenshot(full_page=full_page, type="png")

        await browser.close()

    # Encode to base64
    return base64.b64encode(screenshot_bytes).decode("utf-8")


async def render_url_to_base64(
    url: str,
    width: int = 1280,
    full_page: bool = False,
    device_scale_factor: float = 2.0,
) -> str:
    """
    Render a URL to a base64 encoded PNG image.

    Args:
        url: URL to capture
        width: Viewport width in pixels
        full_page: Capture full scrollable page or just viewport
        device_scale_factor: Scale factor for retina-quality screenshots

    Returns:
        Base64 encoded PNG image string
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": width, "height": 800},
            device_scale_factor=device_scale_factor,
        )

        await page.goto(url, wait_until="networkidle")
        screenshot_bytes = await page.screenshot(full_page=full_page, type="png")

        await browser.close()

    return base64.b64encode(screenshot_bytes).decode("utf-8")


def optimize_image_for_api(
    base64_image: str,
    max_dimension: int = 2048,
    quality: int = 85,
) -> str:
    """
    Optimize image size for API submission (reduce tokens/cost).

    Args:
        base64_image: Base64 encoded image
        max_dimension: Maximum width or height
        quality: JPEG quality (1-100)

    Returns:
        Optimized base64 encoded image
    """
    # Decode
    image_bytes = base64.b64decode(base64_image)
    image = Image.open(BytesIO(image_bytes))

    # Resize if needed
    if max(image.size) > max_dimension:
        ratio = max_dimension / max(image.size)
        new_size = tuple(int(dim * ratio) for dim in image.size)
        image = image.resize(new_size, Image.Resampling.LANCZOS)

    # Convert to RGB if needed (for JPEG)
    if image.mode in ("RGBA", "P"):
        background = Image.new("RGB", image.size, (255, 255, 255))
        if image.mode == "P":
            image = image.convert("RGBA")
        background.paste(image, mask=image.split()[-1])
        image = background

    # Encode as JPEG
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=quality, optimize=True)

    return base64.b64encode(buffer.getvalue()).decode("utf-8")
