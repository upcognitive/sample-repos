"""Authentication decorators for FastAPI route handlers."""

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Annotated, Any

from fastapi import Depends

from orkest.auth.dependencies import get_current_client
from orkest.db.models import ClientCredential


def require_auth(route_func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that enforces JWT authentication on a FastAPI endpoint.

    The authenticated client is injected as a ``client`` keyword argument.
    """
    sig = inspect.signature(route_func)
    params = [
        inspect.Parameter(
            "client",
            inspect.Parameter.KEYWORD_ONLY,
            annotation=Annotated[ClientCredential, Depends(get_current_client)],
        )
        if param.name == "client"
        else param
        for param in sig.parameters.values()
    ]
    if not any(param.name == "client" for param in params):
        params.append(
            inspect.Parameter(
                "client",
                inspect.Parameter.KEYWORD_ONLY,
                annotation=Annotated[ClientCredential, Depends(get_current_client)],
            )
        )

    @wraps(route_func)
    async def authenticated_route(**kwargs: Any) -> Any:
        return await route_func(**kwargs)

    authenticated_route.__signature__ = sig.replace(parameters=params)
    return authenticated_route
