import json

from google import genai
from google.genai import types

from app.config import Settings
from app.schemas import PanelOutline, StoryPanel


def extract_json(text: str) -> list[dict]:
    text = text.strip()

    if text.startswith("```"):
        text = text.replace(
            "```json",
            "",
            1
        )

        text = text.replace(
            "```",
            "",
            1
        )

        text = text.strip()

    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1:
        raise ValueError(
            "Gemini did not return a valid JSON array."
        )

    return json.loads(
        text[start:end + 1]
    )


def generate_story(
    outline: list[PanelOutline],
    character_name: str,
    tone: str,
    settings: Settings,
) -> list[StoryPanel]:

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    outline_json = json.dumps(
        [
            panel.model_dump()
            for panel in outline
        ],
        ensure_ascii=False
    )

    prompt = f"""
Expand this 5-panel comic outline into a complete comic story.

Main character:
{character_name}

Tone:
{tone}

Outline:
{outline_json}

Return ONLY a JSON array containing exactly 5 objects.

Preserve these fields:

panel_number
title
scene_description
image_prompt

Add these fields:

caption
narration

caption:
A short comic-style environmental or atmospheric caption.

narration:
The story action, emotions, dialogue and character interaction.

The five panels must form one continuous story.

Keep the character consistent.

Do not use markdown.
Do not use code fences.
Do not add explanations outside the JSON.
"""

    response = client.models.generate_content(
        model=settings.gemini_pro_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.9,
            response_mime_type="application/json",
        ),
    )

    data = extract_json(
        response.text or ""
    )

    if len(data) != 5:
        raise ValueError(
            f"Expected exactly 5 story panels, got {len(data)}."
        )

    return [
        StoryPanel.model_validate(item)
        for item in data
    ]