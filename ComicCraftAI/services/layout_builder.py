from app.schemas import (
    ComicLayoutPanel,
    StoryPanel,
)


def build_comic_layout(
    story: list[StoryPanel],
    image_paths: list[str],
) -> list[ComicLayoutPanel]:

    if len(story) != len(image_paths):
        raise ValueError(
            "Every story panel must have exactly one image."
        )

    layout = []

    for panel, image_path in zip(
        story,
        image_paths
    ):

        layout.append(
            ComicLayoutPanel(
                **panel.model_dump(),
                image_path=image_path,
            )
        )

    return layout