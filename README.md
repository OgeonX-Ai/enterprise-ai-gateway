# Enterprise AI Gateway

Vendor-agnostic enterprise AI gateway that owns a single agent runtime, session memory, and routing across LLM, speech, RAG, and service desk providers. The backend is FastAPI; the frontend is a static HTML client.

## Features
- Unified `/v1/chat` runtime with policy, memory, and provider selections per request
- Service registry exposing available providers/models for dropdowns
- Mock and Azure-aligned stub connectors for LLM, RAG, STT/TTS, and service desk systems
- Correlation IDs and structured logging for traceability
- Static web UI with provider selectors, channel toggle, and debug drawer

## Repository structure
- `docs/`: Overview, architecture, API, connectors, runtime pipeline, security, observability, Azure deployment, service desk integrations, cost notes, and roadmap.
- `backend/`: FastAPI runtime, service registry, connectors, and API routes.
- `web/`: Static frontend that calls the gateway.
- `demo/`: Local demo notes and screenshots.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

Open `web/index.html` in your browser. The UI defaults to `http://localhost:8000` and lets you select providers before sending requests.

## License
MIT
