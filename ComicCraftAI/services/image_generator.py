from pathlib import Path
from threading import Lock

from PIL import Image, ImageDraw, ImageFont

from app.config import Settings
from app.utils.files import (
    PANELS_DIR,
    ensure_directories,
    unique_name,
)


_PIPELINE = None
_PIPELINE_LOCK = Lock()


def create_mock_image(
    prompt: str,
    output_path: Path,
    width: int,
    height: int,
) -> None:

    image = Image.new(
        "RGB",
        (width, height),
        (245, 236, 215),
    )

    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (
            10,
            10,
            width - 10,
            height - 10,
        ),
        outline=(40, 40, 40),
        width=6,
    )

    try:
        font = ImageFont.truetype(
            "DejaVuSans.ttf",
            24
        )
    except OSError:
        font = ImageFont.load_default()

    draw.text(
        (30, 30),
        "COMICCRAFT",
        fill=(20, 20, 20),
        font=font,
    )

    short_prompt = " ".join(
        prompt.split()
    )

    if len(short_prompt) > 240:
        short_prompt = (
            short_prompt[:237]
            + "..."
        )

    words = short_prompt.split()

    lines = []
    current = ""

    for word in words:

        test = (
            f"{current} {word}"
            .strip()
        )

        if len(test) > 34:
            lines.append(current)
            current = word
        else:
            current = test

    if current:
        lines.append(current)

    y = (
        height // 2
        - min(len(lines), 8) * 16
    )

    for line in lines[:8]:

        draw.text(
            (30, y),
            line,
            fill=(35, 35, 35),
            font=font,
        )

        y += 32

    draw.ellipse(
        (
            width // 2 - 70,
            height // 2 + 100,
            width // 2 + 70,
            height // 2 + 240,
        ),
        outline=(80, 80, 80),
        width=5,
    )

    image.save(
        output_path,
        format="PNG"
    )


def get_diffusion_pipeline(
    settings: Settings
):

    global _PIPELINE

    if _PIPELINE is not None:
        return _PIPELINE

    with _PIPELINE_LOCK:

        if _PIPELINE is not None:
            return _PIPELINE

        import torch

        from diffusers import (
            StableDiffusionPipeline
        )

        kwargs = {}

        if settings.hf_token:
            kwargs["token"] = settings.hf_token

        if torch.cuda.is_available():
            dtype = torch.float16
        else:
            dtype = torch.float32

        pipe = (
            StableDiffusionPipeline
            .from_pretrained(
                settings.image_model_id,
                torch_dtype=dtype,
                **kwargs,
            )
        )

        device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        pipe = pipe.to(device)

        if device == "cuda":
            pipe.enable_attention_slicing()

        _PIPELINE = pipe

    return _PIPELINE


def generate_image(
    prompt: str,
    settings: Settings,
    panel_number: int = 1,
) -> str:

    ensure_directories()

    filename = unique_name(
        f"panel_{panel_number}",
        ".png",
    )

    output_path = (
        PANELS_DIR / filename
    )

    final_prompt = (
        f"{prompt}. "
        "Clean comic illustration, "
        "strong readable composition, "
        "consistent character design, "
        "expressive pose, "
        "detailed environment, "
        "no text, no watermark."
    )

    provider = (
        settings.image_provider
        .lower()
        .strip()
    )

    if provider == "mock":

        create_mock_image(
            final_prompt,
            output_path,
            settings.image_width,
            settings.image_height,
        )

    elif provider == "diffusers":

        pipe = get_diffusion_pipeline(
            settings
        )

        result = pipe(
            prompt=final_prompt,
            negative_prompt=(
                "blurry, low quality, "
                "distorted anatomy, "
                "watermark, text, logo"
            ),
            width=settings.image_width,
            height=settings.image_height,
            num_inference_steps=settings.image_steps,
            guidance_scale=settings.image_guidance,
        )

        result.images[0].save(
            output_path
        )

    else:

        raise ValueError(
            "IMAGE_PROVIDER must be "
            "'mock' or 'diffusers'."
        )

    return (
        f"/static/panels/{filename}"
    )