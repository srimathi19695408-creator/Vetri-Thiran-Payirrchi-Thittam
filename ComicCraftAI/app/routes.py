from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)

from fastapi.responses import HTMLResponse

from fastapi.templating import (
    Jinja2Templates,
)

from app.config import get_settings

from app.schemas import (
    ImageTestRequest,
    PromptRequest,
)

from app.services.exporters import (
    save_pdf,
)

from app.services.gemini_flash import (
    generate_outline,
)

from app.services.gemini_pro import (
    generate_story,
)

from app.services.image_generator import (
    generate_image,
)

from app.services.layout_builder import (
    build_comic_layout,
)


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


def generate_complete_comic(
    request_data: PromptRequest,
):

    settings = get_settings()

    # STEP 1
    # Generate five-panel outline

    outline = generate_outline(
        story_prompt=request_data.story_prompt,
        character_name=request_data.character_name,
        setting=request_data.setting,
        tone=request_data.tone,
        art_style=request_data.art_style,
        settings=settings,
    )

    # STEP 2
    # Generate narration/dialogue

    story = generate_story(
        outline=outline,
        character_name=request_data.character_name,
        tone=request_data.tone,
        settings=settings,
    )

    # STEP 3
    # Generate images

    image_paths = []

    for panel in story:

        image_path = generate_image(
            prompt=panel.image_prompt,
            settings=settings,
            panel_number=panel.panel_number,
        )

        image_paths.append(
            image_path
        )

    # STEP 4
    # Build layout

    layout = build_comic_layout(
        story=story,
        image_paths=image_paths,
    )

    # STEP 5
    # Create PDF

    pdf_url = save_pdf(
        layout
    )

    return layout, pdf_url


@router.get(
    "/",
    response_class=HTMLResponse
)
async def home(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "ComicCraft"
        },
    )


@router.post(
    "/generate",
    response_class=HTMLResponse
)
async def generate(
    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...),
):

    try:

        request_data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        layout, pdf_url = (
            generate_complete_comic(
                request_data
            )
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "title": "ComicCraft",
                "error": str(exc),
                "form": {
                    "story_prompt": story_prompt,
                    "character_name": character_name,
                    "setting": setting,
                    "tone": tone,
                    "art_style": art_style,
                },
            },
            status_code=500,
        )

    return templates.TemplateResponse(
        request=request,
        name="comic_preview.html",
        context={
            "title": "Your Comic",
            "layout": layout,
            "pdf_url": pdf_url,
        },
    )


@router.post(
    "/generate-comic/json"
)
async def generate_comic_json(
    payload: PromptRequest
):

    try:

        layout, pdf_url = (
            generate_complete_comic(
                payload
            )
        )

        return {
            "message": (
                "Comic generated successfully."
            ),
            "layout": [
                item.model_dump()
                for item in layout
            ],
            "pdf_url": pdf_url,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.post(
    "/test-image"
)
async def test_image(
    payload: ImageTestRequest
):

    try:

        image_url = generate_image(
            prompt=payload.prompt,
            settings=get_settings(),
            panel_number=0,
        )

        return {
            "message": (
                "Image generated successfully."
            ),
            "image_url": image_url,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.get(
    "/export-success",
    response_class=HTMLResponse,
)
async def export_success(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "title": "Export Complete"
        },
    )