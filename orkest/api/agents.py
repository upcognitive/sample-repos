"""Agent API endpoints."""

from fastapi import APIRouter

from orkest.auth.decorators import require_auth
from orkest.db.models import ClientCredential

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/")
@require_auth
async def list_agents(client: ClientCredential) -> dict:
    """List agents for the authenticated client."""
    return {"client_id": client.client_id, "agents": []}
