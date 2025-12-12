# Design Critic

AI-powered design critique tool with BYOK (Bring Your Own Key) support.

Upload a design screenshot, paste HTML, or provide an image URL - get instant, actionable feedback on your design from GPT-4o, Claude, or Gemini.

## Demo

![Demo](demo.gif)

## Features

- **Multiple Input Types**: Upload images, paste HTML (auto-rendered to screenshot), or provide image URLs
- **BYOK Support**: Bring your own API key - keys are sent directly to providers, never stored
- **Multiple AI Providers**: OpenAI GPT-4o, Anthropic Claude, Google Gemini
- **Structured Feedback**: Scores for each design aspect with specific, actionable suggestions
- **Design Type Aware**: Optimized prompts for emails, landing pages, dashboards, mobile apps

## Quick Start

### Using Docker

```bash
docker build -t design-critic .
docker run -p 8000:8000 design-critic
```

Open http://localhost:8000 in your browser.

### Local Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Install Playwright browsers
playwright install chromium

# Run the server
python -m design_critic.api
```

## API Usage

### POST /api/critique

Analyze a design and get structured feedback.

**Request Body:**

```json
{
  "html": "<html>...</html>",
  "provider": "openai",
  "api_key": "sk-your-api-key",
  "design_type": "email",
  "focus_areas": ["visual_hierarchy", "typography", "color_scheme"]
}
```

Or with an image URL:

```json
{
  "image_url": "https://example.com/design.png",
  "provider": "anthropic",
  "api_key": "sk-ant-..."
}
```

Or with base64 image:

```json
{
  "image_base64": "iVBORw0KGgo...",
  "provider": "google",
  "api_key": "AI..."
}
```

**Response:**

```json
{
  "overall_score": 7,
  "summary": "A clean email design with good typography but could improve visual hierarchy...",
  "scores": [
    {
      "category": "visual_hierarchy",
      "score": 6,
      "feedback": "The CTA button competes with the header for attention.",
      "suggestions": [
        "Increase CTA button size by 20%",
        "Add more whitespace above the CTA"
      ]
    }
  ],
  "strengths": ["Clean typography", "Good use of whitespace"],
  "improvements": ["Increase CTA prominence", "Add visual anchors"],
  "provider": "openai",
  "model": "gpt-4o"
}
```

## Supported Providers

| Provider | Model | Notes |
|----------|-------|-------|
| OpenAI | gpt-4o | Best overall quality |
| Anthropic | claude-sonnet-4-20250514 | Great for detailed analysis |
| Google | gemini-1.5-flash | Fast and cost-effective |

## Environment Variables

Optional - only needed if you want to provide default API keys:

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AI...
```

## Focus Areas

Available focus areas for critique:

- `visual_hierarchy` - Eye flow and element prominence
- `typography` - Font choices, sizes, readability
- `color_scheme` - Color harmony, contrast, accessibility
- `whitespace` - Spacing, breathing room, balance
- `cta_effectiveness` - Call-to-action clarity and prominence
- `readability` - Content scanability
- `consistency` - Visual pattern consistency
- `accessibility` - Color contrast, text size, touch targets
- `mobile_responsiveness` - Small screen considerations
- `branding` - Professional cohesion
- `layout` - Grid alignment, structure
- `imagery` - Image quality and relevance

## License

MIT
