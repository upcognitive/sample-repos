"""FastAPI application factory."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from orkest.api.agents import router as agents_router
from orkest.auth.router import router as auth_router
from orkest.db.session import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Initialize resources on startup."""
    init_db()
    yield


def create_app() -> FastAPI:
    """Create and configure the Orkest API application."""
    app = FastAPI(title="Orkest API", version="0.1.0", lifespan=lifespan)
    app.include_router(auth_router)
    app.include_router(agents_router)
    return app
