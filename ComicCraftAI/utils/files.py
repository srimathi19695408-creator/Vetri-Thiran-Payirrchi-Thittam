from pathlib import Path
from uuid import uuid4


BASE_DIR = Path(__file__).resolve().parents[2]

STATIC_DIR = BASE_DIR / "static"

PANELS_DIR = STATIC_DIR / "panels"

EXPORTS_DIR = STATIC_DIR / "exports"


def ensure_directories() -> None:
    PANELS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    EXPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


def unique_name(prefix: str, suffix: str) -> str:
    return (
        f"{prefix}_"
        f"{uuid4().hex[:12]}"
        f"{suffix}"
    )