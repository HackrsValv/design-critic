#!/usr/bin/env python3
"""
Design Critic Demo Script

This script demonstrates how to use the Design Critic API programmatically.
Run the server first: python -m design_critic.api

Usage:
    # Set your API key first
    export OPENAI_API_KEY=sk-your-key
    # or
    export ANTHROPIC_API_KEY=sk-ant-your-key
    # or
    export GOOGLE_API_KEY=AI-your-key

    # Then run the demo
    python demo.py
"""

import asyncio
import base64
import os
import sys
from pathlib import Path

import httpx

# Configuration
API_URL = "http://localhost:8000"
TIMEOUT = 120.0  # AI responses can take time


def get_api_key():
    """Get API key from environment, checking all providers."""
    for key_name in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]:
        if key := os.environ.get(key_name):
            provider = key_name.replace("_API_KEY", "").lower()
            return key, provider
    return None, None


async def check_server():
    """Check if the server is running."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_URL}/health")
            return response.status_code == 200
        except httpx.ConnectError:
            return False


async def demo_html_critique(api_key: str, provider: str):
    """Demo: Critique HTML content (gets rendered to screenshot automatically)."""
    print("\n" + "=" * 60)
    print("Demo 1: HTML Content Critique")
    print("=" * 60)

    # Sample email HTML
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 40px; border-radius: 8px; }
            h1 { color: #333; font-size: 24px; margin-bottom: 10px; }
            p { color: #666; line-height: 1.6; }
            .cta { display: inline-block; background: #007bff; color: white; padding: 12px 24px;
                   text-decoration: none; border-radius: 4px; margin-top: 20px; }
            .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee;
                      font-size: 12px; color: #999; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to Our Newsletter!</h1>
            <p>Thanks for subscribing. We're excited to have you on board.</p>
            <p>Every week, we'll send you the latest updates, tips, and exclusive offers
               that you won't find anywhere else.</p>
            <a href="#" class="cta">Get Started</a>
            <div class="footer">
                <p>You're receiving this because you signed up at example.com</p>
                <p><a href="#">Unsubscribe</a> | <a href="#">View in browser</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    request_data = {
        "html": html_content,
        "provider": provider,
        "api_key": api_key,
        "design_type": "email",
        "focus_areas": ["visual_hierarchy", "cta_effectiveness", "typography", "whitespace"],
    }

    print(f"Provider: {provider}")
    print(f"Design Type: email")
    print(f"Focus Areas: {request_data['focus_areas']}")
    print("\nSending request...")

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(f"{API_URL}/api/critique", json=request_data)

        if response.status_code == 200:
            result = response.json()
            print_critique(result)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)


async def demo_image_url_critique(api_key: str, provider: str):
    """Demo: Critique an image from URL."""
    print("\n" + "=" * 60)
    print("Demo 2: Image URL Critique")
    print("=" * 60)

    # Using a public example design image
    image_url = "https://via.placeholder.com/800x600/4a90d9/ffffff?text=Landing+Page+Design"

    request_data = {
        "image_url": image_url,
        "provider": provider,
        "api_key": api_key,
        "design_type": "landing_page",
        "focus_areas": ["visual_hierarchy", "color_scheme", "layout"],
    }

    print(f"Provider: {provider}")
    print(f"Image URL: {image_url}")
    print(f"Design Type: landing_page")
    print("\nSending request...")

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(f"{API_URL}/api/critique", json=request_data)

        if response.status_code == 200:
            result = response.json()
            print_critique(result)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)


async def demo_base64_critique(api_key: str, provider: str):
    """Demo: Critique a base64-encoded image."""
    print("\n" + "=" * 60)
    print("Demo 3: Base64 Image Critique")
    print("=" * 60)

    # Check for local test image or create a simple one
    test_image_path = Path(__file__).parent / "test_design.png"

    if test_image_path.exists():
        print(f"Using local image: {test_image_path}")
        with open(test_image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
    else:
        print("No local test_design.png found. Skipping base64 demo.")
        print("To test this, add a test_design.png file to the project root.")
        return

    request_data = {
        "image_base64": image_data,
        "provider": provider,
        "api_key": api_key,
        "design_type": "web_app",
        "focus_areas": ["accessibility", "consistency", "mobile_responsiveness"],
    }

    print(f"Provider: {provider}")
    print(f"Design Type: web_app")
    print(f"Focus Areas: {request_data['focus_areas']}")
    print("\nSending request...")

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(f"{API_URL}/api/critique", json=request_data)

        if response.status_code == 200:
            result = response.json()
            print_critique(result)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)


async def demo_custom_prompt(api_key: str, provider: str):
    """Demo: Using custom prompt for additional context."""
    print("\n" + "=" * 60)
    print("Demo 4: Custom Prompt with Context")
    print("=" * 60)

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: 'Segoe UI', sans-serif; margin: 0; padding: 40px; background: #1a1a2e; color: white; }
            .dashboard { max-width: 1200px; margin: 0 auto; }
            .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
            h1 { font-size: 28px; margin: 0; }
            .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
            .stat-card { background: #16213e; padding: 24px; border-radius: 12px; }
            .stat-value { font-size: 36px; font-weight: bold; color: #4ecca3; }
            .stat-label { color: #888; margin-top: 8px; }
        </style>
    </head>
    <body>
        <div class="dashboard">
            <div class="header">
                <h1>Analytics Dashboard</h1>
                <span>Last updated: Just now</span>
            </div>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">12,543</div>
                    <div class="stat-label">Total Users</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$45.2K</div>
                    <div class="stat-label">Revenue</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">89%</div>
                    <div class="stat-label">Satisfaction</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">2.4s</div>
                    <div class="stat-label">Avg Load Time</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    request_data = {
        "html": html_content,
        "provider": provider,
        "api_key": api_key,
        "design_type": "dashboard",
        "focus_areas": ["visual_hierarchy", "accessibility", "color_scheme"],
        "custom_prompt": """This is a dark-mode analytics dashboard for a B2B SaaS product.
        The target users are data analysts who often work late hours.
        Please pay special attention to:
        1. Eye strain reduction in dark mode
        2. Data visualization clarity
        3. Quick scanability for busy professionals""",
    }

    print(f"Provider: {provider}")
    print(f"Design Type: dashboard")
    print(f"Custom Context: B2B SaaS analytics dashboard for data analysts")
    print("\nSending request...")

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.post(f"{API_URL}/api/critique", json=request_data)

        if response.status_code == 200:
            result = response.json()
            print_critique(result)
        else:
            print(f"Error: {response.status_code}")
            print(response.text)


async def demo_providers_check():
    """Demo: Check available providers and their status."""
    print("\n" + "=" * 60)
    print("Demo: Check Available Providers")
    print("=" * 60)

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/api/providers")

        if response.status_code == 200:
            providers = response.json()
            print("\nAvailable providers:\n")
            for name, info in providers.items():
                status = "✓ Has default key" if info.get("has_default_key") else "○ BYOK required"
                print(f"  {name:12} - {info['model']:30} {status}")
        else:
            print(f"Error: {response.status_code}")


def print_critique(result: dict):
    """Pretty print the critique result."""
    print("\n" + "-" * 40)
    print("CRITIQUE RESULT")
    print("-" * 40)

    print(f"\n📊 Overall Score: {result['overall_score']}/10")
    print(f"🤖 Provider: {result['provider']} ({result['model']})")

    print(f"\n📝 Summary:\n{result['summary']}")

    if result.get("strengths"):
        print("\n✅ Strengths:")
        for strength in result["strengths"]:
            print(f"   • {strength}")

    if result.get("improvements"):
        print("\n🔧 Areas for Improvement:")
        for improvement in result["improvements"]:
            print(f"   • {improvement}")

    if result.get("scores"):
        print("\n📈 Detailed Scores:")
        for score in result["scores"]:
            print(f"\n   {score['category'].replace('_', ' ').title()}: {score['score']}/10")
            print(f"   {score['feedback']}")
            if score.get("suggestions"):
                print("   Suggestions:")
                for suggestion in score["suggestions"]:
                    print(f"     → {suggestion}")


async def main():
    """Run all demos."""
    print("=" * 60)
    print("DESIGN CRITIC DEMO")
    print("=" * 60)

    # Check server
    if not await check_server():
        print("\n❌ Server not running!")
        print("Start the server first:")
        print("  python -m design_critic.api")
        sys.exit(1)

    print("✓ Server is running")

    # Check for API key
    api_key, provider = get_api_key()
    if not api_key:
        print("\n❌ No API key found!")
        print("Set one of these environment variables:")
        print("  export OPENAI_API_KEY=sk-...")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        print("  export GOOGLE_API_KEY=AI...")
        sys.exit(1)

    print(f"✓ Using {provider} provider")

    # Show available providers
    await demo_providers_check()

    # Run demos
    try:
        await demo_html_critique(api_key, provider)
        await demo_image_url_critique(api_key, provider)
        await demo_base64_critique(api_key, provider)
        await demo_custom_prompt(api_key, provider)
    except httpx.ConnectError:
        print("\n❌ Lost connection to server")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Open http://localhost:8000 for the web UI")
    print("  2. Try different providers by setting different API keys")
    print("  3. Experiment with different design types and focus areas")


if __name__ == "__main__":
    asyncio.run(main())
