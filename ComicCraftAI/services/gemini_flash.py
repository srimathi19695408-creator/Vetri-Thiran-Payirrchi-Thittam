import json

from google import genai
from google.genai import types

from app.config import Settings
from app.schemas import PanelOutline


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

    json_text = text[start:end + 1]

    return json.loads(json_text)


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
    settings: Settings,
) -> list[PanelOutline]:

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    client = genai.Client(
        api_key=settings.gemini_api_key
    )

    prompt = f"""
Create a coherent 5-panel comic outline.

Story idea:
{story_prompt}

Main character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

Return ONLY a JSON array containing exactly 5 objects.

Each object must contain:

panel_number
title
scene_description
image_prompt

panel_number must be an integer from 1 to 5.

scene_description should describe what happens in the panel.

image_prompt should be a detailed visual prompt for an image generation model.

Keep the main character visually consistent across all five panels.

Do not include markdown.
Do not include code fences.
Do not include explanations outside the JSON.
"""

    response = client.models.generate_content(
        model=settings.gemini_flash_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            response_mime_type="application/json",
        ),
    )

    text = response.text or ""

    data = extract_json(text)

    if len(data) != 5:
        raise ValueError(
            f"Expected exactly 5 panels, got {len(data)}."
        )

    return [
        PanelOutline.model_validate(item)
        for item in data
    ]