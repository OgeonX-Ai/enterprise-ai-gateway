# API

All endpoints are served from the FastAPI application in `app/main.py`. Mock providers are enabled by default so no external credentials are required for local testing.

## Base URL
```
http://localhost:8000
```

## Endpoints

### Health check
- **GET** `/healthz`
- **Response**: `{ "status": "ok" }`

### Registry
- **GET** `/v1/registry`
- **Description**: Lists providers grouped by service type with configuration state.
- **Response** (truncated):
```json
{
  "llm": [{"id": "mock-llm", "configured": true, "supported": ["echo", "assistant-lite"]}],
  "rag": [{"id": "mock-search", "configured": true, "supported": ["default"]}],
  "stt": [{"id": "mock-stt", "configured": true, "supported": ["narrowband"]}],
  "tts": [{"id": "mock-tts", "configured": true, "supported": ["alloy"]}],
  "servicedesk": [{"id": "mock-servicedesk", "configured": true, "supported": ["incident"]}]
}
```

### Admin validation
- **GET** `/v1/admin/config/validate`
- **Description**: Runs `validate()` on each configured connector and returns per-provider status.
- **Response**:
```json
{
  "status": "attention",
  "results": [
    {"service_type": "llm", "provider": "mock-llm", "status": "ok", "reason": "mock connector always available"}
  ]
}
```

### Create session
- **POST** `/v1/sessions`
- **Description**: Allocates a new in-memory chat session identifier.
- **Response**: `{ "session_id": "<uuid>" }`

### Chat
- **POST** `/v1/chat`
- **Request body**:
```json
{
  "session_id": "optional-existing-session",
  "channel": "web",
  "message": "What can you do?",
  "provider_selection": {
    "llm_provider": "mock-llm",
    "llm_model": "echo",
    "rag_provider": "mock-search",
    "rag_index": "default",
    "stt_provider": null,
    "stt_model": null,
    "tts_provider": null,
    "tts_voice": null,
    "servicedesk_provider": null
  },
  "use_rag": false,
  "include_debug": true
}
```
- **Response body**:
```json
{
  "session_id": "...",
  "reply": "[MockLLM @ ...] You said: What can you do?. Responding via echo",
  "providers": {"llm_provider": "mock-llm", "llm_model": "echo", "rag_provider": "mock-search", "rag_index": "default", "servicedesk_provider": null, "stt_provider": null, "tts_provider": null, "tts_voice": null, "stt_model": null},
  "used_rag": false,
  "servicedesk_action": null,
  "debug": {"correlation_id": "...", "history_length": 1}
}
```
- **Error conditions**: returns `400` for unknown or unconfigured providers, and `429` for policy violations.

### Audio transcription
- **POST** `/v1/audio/transcribe`
- **Description**: Converts base64-encoded audio to text via the selected STT provider.
- **Request body**:
```json
{
  "audio_base64": "<base64>",
  "stt_provider": "mock-stt",
  "locale": "en-US",
  "model": "narrowband"
}
```
- **Response**: `{ "text": "[Mock STT en-US] received 9 bytes via narrowband", "latency_ms": 5 }`
- **Errors**: returns `400` if the provider id is unknown.

### Audio synthesis
- **POST** `/v1/audio/synthesize`
- **Description**: Converts text to base64 audio via the selected TTS provider.
- **Request body**:
```json
{
  "text": "hello",
  "tts_provider": "mock-tts",
  "voice": "alloy",
  "locale": "en-US"
}
```
- **Response**: `{ "audio_base64": "bW9jay1ieXRlcw==", "latency_ms": 5 }`
- **Errors**: returns `400` if the provider id is unknown.

## Error model
Errors raised by the runtime use FastAPI's `HTTPException` with JSON bodies such as:
```json
{"detail": "LLM provider not configured; missing env: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY"}
```
