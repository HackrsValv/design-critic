"""Prompts for design critique."""

SYSTEM_PROMPT = """You are an expert UI/UX designer and design critic with 15+ years of experience reviewing digital designs. You provide constructive, actionable feedback on visual designs.

Your critiques are:
- Specific and actionable (not vague)
- Balanced (acknowledge strengths, not just problems)
- Prioritized (most impactful issues first)
- Professional and respectful

You evaluate designs against industry best practices and modern design principles."""


def build_critique_prompt(design_type: str, focus_areas: list[str], custom_prompt: str | None) -> str:
    """Build the critique prompt based on options."""

    focus_descriptions = {
        "visual_hierarchy": "Visual Hierarchy: How well does the design guide the eye? Are the most important elements prominent?",
        "typography": "Typography: Font choices, sizes, line heights, readability, consistency",
        "color_scheme": "Color Scheme: Color harmony, contrast, accessibility, emotional impact",
        "whitespace": "Whitespace/Spacing: Breathing room, balance, visual rhythm",
        "cta_effectiveness": "CTA Effectiveness: Are calls-to-action clear, compelling, and easy to find?",
        "readability": "Readability: Can users easily scan and read the content?",
        "consistency": "Consistency: Are visual patterns and styles consistent throughout?",
        "accessibility": "Accessibility: Color contrast, text size, touch targets",
        "mobile_responsiveness": "Mobile Responsiveness: How will this look on smaller screens?",
        "branding": "Branding: Does it feel cohesive and professional?",
        "layout": "Layout: Overall structure, grid alignment, visual balance",
        "imagery": "Imagery: Quality, relevance, and integration of images",
    }

    focus_list = "\n".join(
        f"- {focus_descriptions.get(area, area)}"
        for area in focus_areas
    )

    prompt = f"""Analyze this {design_type} design and provide a detailed critique.

FOCUS AREAS:
{focus_list}

RESPONSE FORMAT:
Provide your response as a JSON object with this exact structure:
{{
    "overall_score": <1-10>,
    "summary": "<2-3 sentence overall assessment>",
    "scores": [
        {{
            "category": "<focus area name>",
            "score": <1-10>,
            "feedback": "<specific feedback for this area>",
            "suggestions": ["<actionable improvement 1>", "<actionable improvement 2>"]
        }}
    ],
    "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
    "improvements": ["<priority improvement 1>", "<priority improvement 2>", "<priority improvement 3>"]
}}

Score guide:
- 1-3: Poor, needs significant work
- 4-5: Below average, notable issues
- 6-7: Good, some room for improvement
- 8-9: Very good, minor refinements possible
- 10: Excellent, professional quality

Be specific in your feedback. Instead of "improve typography", say "increase body text line-height from 1.2 to 1.5 for better readability"."""

    if custom_prompt:
        prompt += f"\n\nADDITIONAL CONTEXT:\n{custom_prompt}"

    return prompt
