# Backend (FastAPI)

A minimal FastAPI app that simulates an enterprise AI gateway. It exposes a `/health` endpoint, a `/connectors` listing, and a `/route` endpoint that dispatches to mocked connectors and stores conversation context in memory.

## Running locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --app-dir backend/app --reload
```

## Key modules

- `main.py`: Application setup and dependency wiring.
- `router.py`: API routes for health checks, connector listing, and routing requests.
- `registry.py`: In-memory connector registry.
- `memory.py`: Simple conversation memory store keyed by session.
- `connectors/`: Mock connector implementations.
