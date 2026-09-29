from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ComicCraft"

    gemini_api_key: str = ""

    gemini_flash_model: str = "gemini-2.5-flash"
    gemini_pro_model: str = "gemini-2.5-pro"

    image_provider: str = "mock"

    hf_token: str = ""

    image_model_id: str = (
        "stable-diffusion-v1-5/stable-diffusion-v1-5"
    )

    image_width: int = 512
    image_height: int = 512

    image_steps: int = 20
    image_guidance: float = 7.5

    max_panels: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()