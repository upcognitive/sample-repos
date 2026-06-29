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

## API endpoints

All endpoints are served from the base URL `http://localhost:8000`. Unless noted, request and response bodies are JSON.

### POST /auth/token

Obtain a JWT access token using client credentials. Does not require authentication.

**Request body**

| Field | Type | Description |
| --- | --- | --- |
| `client_id` | string | Client identifier |
| `client_secret` | string | Client secret |

**Example request**

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"client_id": "my-client", "client_secret": "my-secret"}'
```

**Example response**

```json
{"access_token": "<jwt>", "token_type": "bearer"}
```

### GET /agents/

List agents for the authenticated client. Requires a bearer token.

**Headers**

| Header | Value |
| --- | --- |
| `Authorization` | `Bearer <access_token>` |

**Example request**

```bash
curl http://localhost:8000/agents/ \
  -H "Authorization: Bearer <access_token>"
```

**Example response**

```json
{"client_id": "my-client", "agents": []}
```

### POST /users

Create a new user. Does not require authentication.

**Request body**

| Field | Type | Description |
| --- | --- | --- |
| `username` | string | Username (minimum 3 characters) |
| `email` | string | User email address |
| `password` | string | Password (minimum 6 characters, must include numbers and special characters) |

**Example request**

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "jane", "email": "jane@example.com", "password": "pass1!"}'
```

**Example response**

```json
{"id": 1, "username": "jane", "email": "jane@example.com"}
```

### GET /users/{user_id}

Find a user by ID. Does not require authentication.

**URI parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `user_id` | integer | User ID |

**Example request**

```bash
curl http://localhost:8000/users/1
```

**Example response**

```json
{"id": 1, "username": "jane", "email": "jane@example.com"}
```

### GET /users

Find a user by email. Does not require authentication.

**Query parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `email` | string | User email address |

**Example request**

```bash
curl "http://localhost:8000/users?email=jane@example.com"
```

**Example response**

```json
{"id": 1, "username": "jane", "email": "jane@example.com"}
```

### PATCH /users/{user_id}

Update the password for an existing user. Does not require authentication.

**URI parameters**

| Parameter | Type | Description |
| --- | --- | --- |
| `user_id` | integer | User ID |

**Request body**

| Field | Type | Description |
| --- | --- | --- |
| `password` | string | New password (minimum 6 characters, must include numbers and special characters) |

**Example request**

```bash
curl -X PATCH http://localhost:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"password": "newpass1!"}'
```

**Example response**

```json
{"id": 1, "username": "jane", "email": "jane@example.com"}
```

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

See [POST /auth/token](#post-authtoken) for the request and response format.

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

See [GET /agents/](#get-agents) for an example of calling a protected endpoint.

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
