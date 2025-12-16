# Baseline inventory (pre-microservices)

## Application layout
- **Main FastAPI entrypoint:** `backend/app/main.py` wires middleware, shared runtime state, and routers for health, admin, chat, and audio routes while enforcing a correlation ID on every request.【F:backend/app/main.py†L1-L56】
- **Configuration:** `backend/app/settings.py` defines environment-driven flags for enabling Azure OpenAI, Azure Speech, Azure AI Search, and multiple service desk providers alongside correlation header naming; defaults keep all real connectors disabled for local use.【F:backend/app/settings.py†L1-L61】

## Current endpoints
- `GET /healthz` simple health response.【F:backend/app/api/routes_health.py†L1-L8】
- `GET /v1/registry` returns the registry snapshot of available connectors (filtered when `dev_mode` is false).【F:backend/app/api/routes_admin.py†L13-L20】
- `GET /v1/admin/config/validate` runs connector validation routines.【F:backend/app/api/routes_admin.py†L22-L24】
- `POST /v1/sessions` creates conversation sessions.【F:backend/app/api/routes_chat.py†L14-L18】
- `POST /v1/chat` proxies chat requests to the runtime while propagating correlation IDs.【F:backend/app/api/routes_chat.py†L21-L29】
- `POST /v1/audio/transcribe` accepts base64-encoded audio payloads and forwards them to an STT connector.【F:backend/app/api/routes_audio.py†L13-L24】
- `POST /v1/audio/synthesize` returns base64-encoded audio from a TTS connector.【F:backend/app/api/routes_audio.py†L27-L37】

## Connectors discovered
- Built-in mock connectors for LLM, search, STT, TTS, and service desk are always available.【F:backend/app/registry/service_registry.py†L10-L61】
- Optional real connectors are registered (and flagged with missing env vars when disabled) for Azure OpenAI, Azure AI Search, Azure Speech (STT/TTS), ServiceNow, Jira Service Management, and BMC Remedy.【F:backend/app/registry/service_registry.py†L64-L182】

## Audio handling approach
- Audio transcription currently expects `audio_base64` plus optional locale/model fields and decodes the payload before handing it to the runtime; synthesis returns base64-encoded audio bytes to clients.【F:backend/app/api/routes_audio.py†L13-L37】

## Dependencies in use
- Core runtime dependencies include FastAPI, Uvicorn, Pydantic (and `pydantic-settings`), OpenAI SDK, Azure SDKs (identity, search, speech), and httpx.【F:backend/requirements.txt†L1-L10】

## Baseline tests
- A lightweight pytest suite exercises health, registry, chat, audio flows, and connector validation directly against the runtime and verifies HTTP method declarations. Fixtures reset in-memory state and inject local stubs for unavailable third-party SDKs to keep tests hermetic without network installs.【F:backend/tests/conftest.py†L1-L22】【F:backend/tests/integration/test_api.py†L14-L135】
- Current status: all tests pass (see test run in CI section).
