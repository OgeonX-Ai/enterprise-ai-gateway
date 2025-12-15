# API

Base URL: `http://localhost:8000`

## Endpoints

### `GET /healthz`
Health probe for readiness.

### `GET /v1/registry`
Returns available providers and models for dropdowns.

**Response**
```json
{
  "llm": [{"id": "mock-llm", "display_name": "Mock LLM", "supported": ["echo"], "capabilities": ["chat"], "requires_auth": false, "status": "enabled"}],
  "rag": [...],
  "stt": [...],
  "tts": [...],
  "servicedesk": [...]
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
  "debug": {"correlation_id": "...", "rag_results": [...], "servicedesk": {...}, "history_length": 2}
}
```

### `POST /v1/audio/transcribe`
Transcribes audio payloads using the configured STT provider. Demo accepts JSON and returns mock text.

**Request**
```json
{"stt_provider": "mock-stt", "payload": "base64"}
```

**Response**
```json
{"text": "[MockSTT] Transcription placeholder for provided audio payload"}
```

### `POST /v1/audio/synthesize`
Synthesizes text to speech using the selected TTS provider.

**Request**
```json
{"tts_provider": "mock-tts", "voice": "alloy", "text": "Hello"}
```

**Response**
```json
{"audio": "[MockTTS:alloy] Audio bytes for text: Hello..."}
```
