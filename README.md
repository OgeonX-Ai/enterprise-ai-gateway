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

## Pipelines
- Runner smoke check (self-hosted Windows): [.github/workflows/runner-smoke.yml](.github/workflows/runner-smoke.yml)
- Python CI on the Windows runner: [.github/workflows/ci-python.yml](.github/workflows/ci-python.yml)
- Optional Minikube CD on the same runner: [.github/workflows/cd-minikube.yml](.github/workflows/cd-minikube.yml)
- Overview and usage: [`docs/pipelines.md`](docs/pipelines.md)

All workflows target the self-hosted Windows runner; optional Docker/Minikube tooling is detected gracefully so missing local dependencies will skip CD without failing CI.

## ServiceNow agent tools (mock-first)
- The ServiceNow tool endpoints are exposed under `/v1/tools/servicenow/*` and are designed for agents (e.g., ElevenLabs Agent) to call.
- By default the connector runs in **mock mode** with seeded incidents so you can test without credentials.
- Configure the backend via `backend/.env` (see `backend/.env.example`):
  - `SERVICENOW_MOCK_MODE=true` (default if credentials are missing)
  - `SERVICENOW_INSTANCE_URL`, `SERVICENOW_USERNAME`, `SERVICENOW_PASSWORD` for real mode (basic auth).
  - `CORS_ALLOW_ORIGINS` controls browser access (includes GitHub Pages demo by default).
- Example calls:
  - `POST /v1/tools/servicenow/search {"query":"vpn", "limit":3}`
  - `POST /v1/tools/servicenow/ticket/update {"ticket":{"number":"INC0012345"}, "fields":{"state":"In Progress"}, "reason":"triage"}`
  - `GET /v1/tools/servicenow/capabilities` (reports mock/real mode, instance, auth).
- Logs carry `X-Correlation-ID` headers and are streamed to `/v1/debug/stream` when `ENABLE_DEBUG_STREAM=true`.
- For production, replace local environment variables with a secret provider (e.g., Azure Key Vault placeholder at `backend/app/security/key_provider.py`).

## Speech fallback behavior (ElevenLabs -> local Whisper)
- `/v1/audio/transcribe-file` accepts `provider=auto|elevenlabs|local_whisper` plus optional `model`, `language`, `beam_size`, and `vad` query params.
- When `provider=auto`, ElevenLabs is used if configured and healthy; auth/credit/429 errors mark it unavailable for 10 minutes and the router falls back to local Whisper.
- `GET /v1/runtime/status` reports `stt_provider_active`, whether ElevenLabs is OK, the current mode (`primary` vs `fallback`), and the ServiceNow mode (`mock`/`real`).
- Live backend logs (including STT/tool calls) stream from `/v1/debug/stream` when `ENABLE_DEBUG_STREAM=true`.

## Whisper Playground (Local CPU Demo)
- Start the FastAPI backend as above, then open [`http://127.0.0.1:8000/tools/whisper`](http://127.0.0.1:8000/tools/whisper).
- Use your browser microphone to record, tweak Whisper settings (model, language, beam size, chunk length, VAD), and watch live logs.
- The playground runs entirely on CPU using `faster-whisper`; performance depends on your laptop hardware. Audio is processed in-memory and not stored.

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
- Azure scalability guidance: [`docs/azure/scalability-report.md`](docs/azure/scalability-report.md)
- Android parity + integration checklist: [`docs/android-integration-checklist.md`](docs/android-integration-checklist.md)
- Contribution standards: [`docs/contributing.md`](docs/contributing.md)
- Repo audit and current gaps: [`docs/audit.md`](docs/audit.md)
- UI mockups: [`docs/mockups`](docs/mockups)

## Troubleshooting
- If Azure connectors are enabled via environment flags, ensure the related `AZURE_*` settings are present; otherwise, keep `DEV_MODE=true` to use mocks.
- Delete or recreate `.venv` if dependencies drift: `rm -rf .venv && make install`.
- Set `PYTHONPATH=backend` (already exported in the `Makefile`) when running tools outside `make`.

## License
MIT
