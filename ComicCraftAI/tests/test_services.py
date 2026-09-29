from app.schemas import (
    PanelOutline,
    StoryPanel,
)

from app.services.layout_builder import (
    build_comic_layout,
)


def test_layout_matches_images():

    story = []

    for i in range(1, 6):

        story.append(
            StoryPanel(
                panel_number=i,
                title=f"Panel {i}",
                scene_description="A scene.",
                image_prompt="A picture.",
                caption="Caption.",
                narration="Narration.",
            )
        )

    image_paths = [
        f"/static/panels/p{i}.png"
        for i in range(1, 6)
    ]

    layout = build_comic_layout(
        story,
        image_paths,
    )

    assert len(layout) == 5

    assert (
        layout[2].panel_number
        == 3
    )

    assert (
        layout[2].image_path
        == image_paths[2]
    )


def test_outline_model():

    panel = PanelOutline(
        panel_number=1,
        title="Beginning",
        scene_description=(
            "The hero enters the forest."
        ),
        image_prompt=(
            "Comic hero entering a forest."
        ),
    )

    assert panel.panel_number == 1