# API

Base URL: `http://localhost:8000`

## Endpoints

### `GET /healthz`
Health probe for readiness.

### `GET /v1/registry`
Returns available providers and models for dropdowns. In `DEV_MODE=true`, unconfigured providers are also returned with `configured=false` and `missing_env` hints.

**Response**
```json
{
  "llm": [{"id": "mock-llm", "display_name": "Mock LLM", "supported": ["echo"], "capabilities": ["chat"], "requires_auth": false, "status": "enabled", "configured": true, "missing_env": []}],
  "rag": [...],
  "stt": [...],
  "tts": [...],
  "servicedesk": [...]
}
```

### `GET /v1/admin/config/validate`
Checks each configured connector and returns pass/fail without echoing secrets.

**Response**
```json
{
  "status": "attention",
  "results": [
    {"service_type": "llm", "provider": "mock-llm", "status": "ok", "reason": "mock connector always available"},
    {"service_type": "llm", "provider": "azure-openai", "status": "not_configured", "reason": "Missing env: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY"}
  ]
}
```

### `POST /v1/sessions`
Creates a session id for clients that want to persist conversation context.

**Response**
```json
{"session_id": "uuid"}
```

### `POST /v1/chat`
Primary runtime endpoint that applies policy, builds context, and routes to connectors.

**Request**
```json
{
  "session_id": "optional-uuid",
  "channel": "web",
  "message": "Reset the VPN and open a ticket",
  "provider_selection": {
    "llm_provider": "mock-llm",
    "llm_model": "assistant-lite",
    "rag_provider": "mock-search",
    "rag_index": "default",
    "stt_provider": "mock-stt",
    "stt_model": "narrowband",
    "tts_provider": "mock-tts",
    "tts_voice": "alloy",
    "servicedesk_provider": "servicenow"
  },
  "use_rag": true,
  "include_debug": true
}
```

**Response**
```json
{
  "session_id": "uuid",
  "reply": "...",
  "providers": {"llm_provider": "mock-llm", "llm_model": "assistant-lite", "rag_provider": "mock-search", "rag_index": "default", "stt_provider": "mock-stt", "stt_model": "narrowband", "tts_provider": "mock-tts", "tts_voice": "alloy", "servicedesk_provider": "servicenow"},
  "used_rag": true,
  "servicedesk_action": "create",
  "debug": {"correlation_id": "...", "rag_results": [...], "servicedesk": {...}, "history_length": 2, "llm_usage": {"completion_tokens": 32}}
}
```

### `POST /v1/audio/transcribe`
Transcribes audio payloads using the configured STT provider. Expects base64 audio payloads and locale/model hints.

**Request**
```json
{"stt_provider": "mock-stt", "audio_base64": "...", "locale": "en-US", "model": "default"}
```

**Response**
```json
{"text": "[Mock STT en-US] received 0 bytes via default", "latency_ms": 5}
```

### `POST /v1/audio/synthesize`
Synthesizes text to speech using the selected TTS provider.

**Request**
```json
{"tts_provider": "mock-tts", "voice": "alloy", "locale": "en-US", "text": "Hello"}
```

**Response**
```json
{"audio_base64": "bW9jay1ieXRlcw==", "latency_ms": 5}
```
