# Orkest

Python CLI for orchestrating agent workflows.

## Development

Requires Python 3.14 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --extra dev
uv run orkest
```

## API server

Start the FastAPI server:

```bash
uv run orkest serve
```

The API listens on `http://0.0.0.0:8000`.

## Authentication

The API uses JWT bearer tokens issued from client credentials stored in the `client_credentials` database table.

### Client credentials

Insert credentials manually before requesting tokens:

```sql
INSERT INTO client_credentials (client_id, client_secret, name)
VALUES ('my-client', 'my-secret', 'My Application');
```

Set a signing secret for production:

```bash
export ORKEST_JWT_SECRET="your-secret-key"
```

Optionally override the database URL (defaults to `sqlite:///./orkest.db`):

```bash
export ORKEST_DATABASE_URL="sqlite:///./orkest.db"
```

### Request a token

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"client_id": "my-client", "client_secret": "my-secret"}'
```

Response:

```json
{"access_token": "<jwt>", "token_type": "bearer"}
```

### Protecting endpoints

Apply the `@require_auth` decorator to FastAPI route handlers. The authenticated client is injected as the `client` argument:

```python
from fastapi import APIRouter
from orkest.auth.decorators import require_auth
from orkest.db.models import ClientCredential

router = APIRouter()

@router.get("/example")
@require_auth
async def example(client: ClientCredential) -> dict:
    return {"client_id": client.client_id}
```

Call protected endpoints with the bearer token:

```bash
curl http://localhost:8000/agents/ \
  -H "Authorization: Bearer <access_token>"
```

You can also use the `get_current_client` dependency directly when a decorator is not preferred:

```python
from typing import Annotated
from fastapi import Depends
from orkest.auth.dependencies import get_current_client

@router.get("/example")
async def example(client: Annotated[ClientCredential, Depends(get_current_client)]) -> dict:
    return {"client_id": client.client_id}
```

## Tests

```bash
uv run pytest
```
