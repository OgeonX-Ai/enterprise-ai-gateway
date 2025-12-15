# Backend

FastAPI runtime that owns session memory and routes across mock and Azure-aligned connectors for LLM, RAG, speech, and service desk systems.

## Quickstart

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The API will run on `http://localhost:8000`. Pair it with `web/index.html` for the static UI.

## Configuration

Set environment variables in `.env` (already referenced by `pydantic-settings`). Feature flags keep mocks as defaults until you opt into real connectors:

- `DEV_MODE`: expose debug fields and list unconfigured providers in `/v1/registry` (default `true`).
- `USE_AZURE_OPENAI`, `USE_AZURE_SPEECH`, `USE_AZURE_SEARCH`: enable Azure connectors when keys/endpoints are present.
- `USE_SERVICENOW`, `USE_JIRASM`, `USE_REMEDY`: enable service desk connectors when credentials are present.

Populate the relevant `AZURE_*`, `SERVICENOW_*`, `JIRA_*`, and `REMEDY_*` variables as shown in `.env.example`. No secrets are required to run with mocks.

## Validation

Call `/v1/admin/config/validate` to verify which connectors are ready. The endpoint never echoes secret values; it only returns pass/fail + reason.
