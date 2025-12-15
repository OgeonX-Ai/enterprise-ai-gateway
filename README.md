# Enterprise AI Gateway

Vendor-agnostic enterprise AI gateway that owns a single agent runtime, session memory, and routing across LLM, speech, RAG, and service desk providers. The backend is FastAPI; the frontend is a static HTML client.

## Features
- Unified `/v1/chat` runtime with policy, memory, and provider selections per request
- Service registry exposing available providers/models for dropdowns
- Mock and Azure-aligned stub connectors for LLM, RAG, STT/TTS, and service desk systems
- Correlation IDs and structured logging for traceability
- Static web UI with provider selectors, channel toggle, and debug drawer

## Supported providers
- Speech-to-Text (STT): local Whisper (faster-whisper), Azure Speech, OpenAI Whisper API, Deepgram (stub)
- Large Language Models (LLM): Azure OpenAI, OpenAI, Anthropic, Ollama (local), LLaMA.cpp (stub)
- Text-to-Speech (TTS): Azure Speech TTS, local TTS stub
- Service Desk: ServiceNow, Jira Service Management, Remedy

## Quickstart (≤10 minutes)
1. Prereqs: Python 3.11+, `make`, and optionally Azure credentials if you want to exercise the Azure connectors (mocks are default).
2. Bootstrap a virtualenv and install dev dependencies:
   ```bash
   make install
   cp backend/.env.example backend/.env
   ```
3. Run the API locally:
   ```bash
   source .venv/bin/activate
   uvicorn app.main:app --app-dir backend --reload
   ```
4. Open `web/index.html` in your browser and point it to `http://localhost:8000`.

## Tests and validation
- Run unit + integration tests with coverage: `make test`
- Lint (ruff) and tests together: `make check`
- Test reports are written to `reports/junit.xml` for CI upload.

## Repository structure
- `docs/`: Architecture, API, security, observability, deployment, routing, and new onboarding docs (`docs/architecture.md`, `docs/api.md`, `docs/contributing.md`, `docs/audit.md`).
- `docs/mockups/`: Lightweight UI wireframes for chat and admin flows.
- `backend/`: FastAPI runtime, service registry, connectors, and API routes.
- `web/`: Static frontend that calls the gateway.
- `demo/`: Local demo notes and screenshots.

## Additional docs
- Architecture overview and sequence diagrams: [`docs/architecture.md`](docs/architecture.md)
- Endpoint reference with examples: [`docs/api.md`](docs/api.md)
- Contribution standards: [`docs/contributing.md`](docs/contributing.md)
- Repo audit and current gaps: [`docs/audit.md`](docs/audit.md)
- UI mockups: [`docs/mockups`](docs/mockups)

## Troubleshooting
- If Azure connectors are enabled via environment flags, ensure the related `AZURE_*` settings are present; otherwise, keep `DEV_MODE=true` to use mocks.
- Delete or recreate `.venv` if dependencies drift: `rm -rf .venv && make install`.
- Set `PYTHONPATH=backend` (already exported in the `Makefile`) when running tools outside `make`.

## License
MIT
