from pathlib import Path
from urllib.parse import urlparse

from fpdf import FPDF

from app.schemas import ComicLayoutPanel
from app.utils.files import (
    BASE_DIR,
    EXPORTS_DIR,
    ensure_directories,
    unique_name,
)


def get_local_image_path(
    image_url: str
) -> Path:

    parsed = urlparse(image_url)

    relative_path = parsed.path.lstrip("/")

    image_path = (
        BASE_DIR / relative_path
    )

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    return image_path


def save_pdf(
    layout: list[ComicLayoutPanel]
) -> str:

    ensure_directories()

    filename = unique_name(
        "comic",
        ".pdf",
    )

    output_path = (
        EXPORTS_DIR / filename
    )

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15,
    )

    for panel in layout:

        pdf.add_page()

        pdf.set_font(
            "Helvetica",
            "B",
            18,
        )

        pdf.multi_cell(
            0,
            10,
            (
                f"Panel "
                f"{panel.panel_number}: "
                f"{panel.title}"
            ),
        )

        pdf.ln(2)

        image_path = (
            get_local_image_path(
                panel.image_path
            )
        )

        pdf.image(
            str(image_path),
            x=15,
            y=35,
            w=180,
        )

        pdf.set_y(145)

        pdf.set_font(
            "Helvetica",
            "I",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            panel.scene_description,
        )

        pdf.ln(3)

        pdf.set_font(
            "Helvetica",
            "B",
            11,
        )

        pdf.multi_cell(
            0,
            6,
            "Caption",
        )

        pdf.set_font(
            "Helvetica",
            "",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            panel.caption,
        )

        pdf.ln(2)

        pdf.set_font(
            "Helvetica",
            "B",
            11,
        )

        pdf.multi_cell(
            0,
            6,
            "Narration",
        )

        pdf.set_font(
            "Helvetica",
            "",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            panel.narration,
        )

    pdf.output(
        str(output_path)
    )

    return (
        f"/static/exports/{filename}"
    )