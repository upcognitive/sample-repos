"""FastAPI application factory."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from orkest.api.agents import router as agents_router
from orkest.api.errors import register_exception_handlers
from orkest.api.middleware import RequestLoggingMiddleware
from orkest.api.users import router as users_router
from orkest.auth.router import router as auth_router
from orkest.db.session import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Initialize resources on startup."""
    init_db()
    yield


def create_app() -> FastAPI:
    """Create and configure the Orkest API application."""
    app = FastAPI(title="Orkest API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(RequestLoggingMiddleware)
    register_exception_handlers(app)
    app.include_router(auth_router)
    app.include_router(agents_router)
    app.include_router(users_router)
    return app
