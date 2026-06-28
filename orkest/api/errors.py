"""Centralized API error handling."""

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def _format_field_name(loc: tuple[Any, ...]) -> str:
    for part in reversed(loc):
        if isinstance(part, str) and part not in {"body", "query"}:
            return part
    return "field"


def _validation_error_message(exc: RequestValidationError) -> str:
    if not exc.errors():
        return "Invalid request body"

    error = exc.errors()[0]
    error_type = error.get("type", "")
    field_name = _format_field_name(tuple(error.get("loc", ())))

    if error_type == "missing":
        return f"Missing {field_name} on the request body"

    if error_type == "value_error":
        message = str(error.get("msg", ""))
        if message.startswith("Value error, "):
            return message.replace("Value error, ", "", 1)
        return message

    if error_type == "string_too_short":
        return f"{field_name} must be at least {error.get('ctx', {}).get('min_length')} characters"

    return str(error.get("msg", "Invalid request body"))


def register_exception_handlers(app: FastAPI) -> None:
    """Register JSON error handlers for the application."""

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        message = _validation_error_message(exc)
        logger.error("Validation error: %s", message)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": message},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        detail = exc.detail
        if isinstance(detail, dict) and "error" in detail:
            message = detail["error"]
        elif isinstance(detail, str):
            message = detail
        else:
            message = "Request failed"

        if exc.status_code >= 500:
            logger.error("HTTP error %s: %s", exc.status_code, message)
        else:
            logger.error("HTTP error %s: %s", exc.status_code, message)

        return JSONResponse(
            status_code=exc.status_code,
            content={"error": message},
        )
