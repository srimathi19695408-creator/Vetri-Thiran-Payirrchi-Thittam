from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.staticfiles import (
    StaticFiles,
)

from app.config import get_settings

from app.routes import router

from app.utils.files import (
    ensure_directories,
)


@asynccontextmanager
async def lifespan(
    app: FastAPI
):

    ensure_directories()

    yield


settings = get_settings()

app = FastAPI(
    title=settings.app_name,

    description=(
        "AI Comic Story Creator "
        "using Gemini and Stable Diffusion."
    ),

    version="1.0.0",

    lifespan=lifespan,
)


app.mount(
    "/static",
    StaticFiles(
        directory="static"
    ),
    name="static",
)


app.include_router(
    router
)