from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    story_prompt: str = Field(
        ...,
        min_length=3,
        max_length=2000
    )

    character_name: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    setting: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    tone: str = Field(
        ...,
        min_length=1,
        max_length=80
    )

    art_style: str = Field(
        ...,
        min_length=1,
        max_length=120
    )

    @field_validator(
        "story_prompt",
        "character_name",
        "setting",
        "tone",
        "art_style"
    )
    @classmethod
    def clean_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty.")

        return value


class ImageTestRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=3,
        max_length=2000
    )


class PanelOutline(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str


class StoryPanel(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
    caption: str
    narration: str


class ComicLayoutPanel(StoryPanel):
    image_path: str


class ComicGenerationResponse(BaseModel):
    message: str
    layout: list[ComicLayoutPanel]
    pdf_url: str