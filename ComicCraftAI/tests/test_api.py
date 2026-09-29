import os

os.environ["IMAGE_PROVIDER"] = "mock"


from fastapi.testclient import (
    TestClient
)

from app.main import app

import app.routes as routes


def fake_pipeline(payload):

    from app.schemas import StoryPanel

    story = []

    for i in range(1, 6):

        story.append(
            StoryPanel(
                panel_number=i,
                title=f"Panel {i}",
                scene_description=(
                    "A generated scene."
                ),
                image_prompt=(
                    "A generated comic scene."
                ),
                caption=(
                    "A generated caption."
                ),
                narration=(
                    "A generated narration."
                ),
            )
        )

    paths = [
        f"/static/panels/test{i}.png"
        for i in range(1, 6)
    ]

    layout = routes.build_comic_layout(
        story,
        paths,
    )

    return (
        layout,
        "/static/exports/test.pdf"
    )


def test_home():

    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200

    assert "ComicCraft" in response.text


def test_json_endpoint(
    monkeypatch
):

    monkeypatch.setattr(
        routes,
        "generate_complete_comic",
        fake_pipeline,
    )

    client = TestClient(app)

    response = client.post(
        "/generate-comic/json",

        json={
            "story_prompt": (
                "A fox explores a forest"
            ),
            "character_name": "Finn",
            "setting": "forest",
            "tone": "funny",
            "art_style": "comic book",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(
        data["layout"]
    ) == 5

    assert data[
        "pdf_url"
    ].endswith(".pdf")