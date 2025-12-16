# Android integration and backend parity checklist

Last updated: 2025-12-16

## Repo parity status
- No Git remote is configured in this workspace, so parity with GitHub cannot be automatically verified yet. Add the upstream remote (e.g., `git remote add origin <url>`) and fetch before diffing against `origin/main`.
- Working tree is clean on branch `work`; no local modifications are pending.
- Target files to diff once the remote is configured: `backend/app/main.py`, `backend/app/api/`, `backend/app/runtime/`, `backend/app/registry/`, `backend/requirements*.txt`, and `backend/.env.example`.

## Backend runtime health
- Start the FastAPI backend locally from repo root: `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload`.
- Health endpoint: `GET /healthz` returns `{ "status": "ok" }` and should respond without auth. Correlation IDs are accepted from `X-Correlation-ID` and added to responses when missing.
- OpenAPI spec is published at `/openapi.json` from the same base URL.

## API contract inventory
| Method | Path | Request schema | Response schema | Notes |
| --- | --- | --- | --- | --- |
| GET | `/healthz` | none | `{ "status": "ok" }` | Basic liveness probe. |
| GET | `/v1/registry` | none | `RegistryResponse` with provider lists for `llm`, `rag`, `stt`, `tts`, `servicedesk` | Includes unconfigured providers when `DEV_MODE=true`. |
| GET | `/v1/admin/config/validate` | none | `ValidationResponse` entries `{service_type, provider, status, reason}` | Uses connector validation hooks. |
| POST | `/v1/sessions` | none | `{ "session_id": "<uuid>" }` | Allocates a memory session. |
| POST | `/v1/chat` | `ChatRequest` `{ session_id?, channel, message, provider_selection{ llm_provider, llm_model, rag_provider?, rag_index?, stt_provider?, stt_model?, tts_provider?, tts_voice?, servicedesk_provider? }, use_rag, include_debug }` | `ChatResponse` `{ session_id, reply, providers, used_rag, servicedesk_action?, debug? }` | Correlation ID forwarded via header. Errors return HTTP 400/429 from `GatewayException`/`PolicyViolation`. |
| POST | `/v1/audio/transcribe` | JSON `{ stt_provider="mock-stt" default, locale="en-US" default, model="default" default, audio_base64 }` | `{ text, latency_ms }` from provider | Base64-decoded audio bytes sent to STT connector. |
| POST | `/v1/audio/synthesize` | JSON `{ tts_provider="mock-tts" default, locale="en-US" default, voice?, text }` | `{ audio_base64, latency_ms }` | Base64-encoded audio returned. |

## Connectivity checklist for Android
- Emulator base URL: `http://10.0.2.2:8000`; physical device: `http://<host-lan-ip>:8000`. Keep the trailing port aligned with uvicorn startup.
- AndroidManifest must include internet permission; add a network security config if cleartext HTTP is used. Inject the backend base URL via a single source (e.g., `BuildConfig` or an `ApiConfig` singleton) to avoid per-screen drift.
- Verify end-to-end by invoking the chat or audio flows from the app, confirming headers (including `X-Correlation-ID`), payloads, and responses in both Logcat and backend logs.

## Failure-mode expectations
- Missing or disabled providers raise HTTP 400 with a descriptive message when `GatewayException` is triggered.
- Policy rejections return HTTP 429 via `PolicyViolation`.
- Transcription/Synthesis endpoints return connector-specific errors if providers are unavailable; callers should surface meaningful UI errors without crashing and may retry when safe.

## Gaps and follow-ups
- Configure the GitHub remote and diff the target backend files to confirm parity before Android release builds.
- Automate a minimal Android integration test (mock backend flag) alongside existing backend pytest coverage to detect contract drift.
- Add a smoke test that exercises `GET /healthz`, `GET /v1/registry`, `POST /v1/chat`, and `POST /v1/audio/transcribe` against the locally running backend prior to mobile regression runs.
