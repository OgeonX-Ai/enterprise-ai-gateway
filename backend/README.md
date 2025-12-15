# Backend

FastAPI runtime that owns session memory and routes across mocked and stubbed connectors for LLM, RAG, speech, and service desk systems.

## Quickstart

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will run on `http://localhost:8000`. Pair it with `web/index.html` for the static UI.

## Configuration

Environment variables (prefixed with `GATEWAY_`) can be set in a `.env` file:

- `GATEWAY_APP_NAME`: display name for the API
- `GATEWAY_ENVIRONMENT`: environment label
- `GATEWAY_DEBUG`: toggle debug behaviors
- `GATEWAY_CORRELATION_ID_HEADER`: override correlation header name

See `.env.example` for defaults. No secrets are required for mocked connectors.
