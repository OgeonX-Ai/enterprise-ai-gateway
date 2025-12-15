# Connectors

Connectors implement clear interfaces so the runtime can swap between mock defaults and production providers without UI changes. Secrets are only loaded on the backend via environment variables.

## Contracts
- **LLMConnector**: `generate(messages, model, temperature, max_tokens) -> {text, usage, latency_ms}`
- **STTConnector**: `transcribe(audio_payload, locale, model) -> {text, latency_ms}`
- **TTSConnector**: `synthesize(text, locale, voice) -> {audio_bytes, latency_ms}`
- **RAGConnector**: `search(query, top_k, index_name) -> List[snippets]`
- **ServiceDeskConnector**: `create_ticket(title, body, severity, requester)`, `get_ticket(ticket_id)`, `search_kb(query, top_k)`, `validate()`

## Available implementations
- **LLM**: `mock-llm` (default), `azure-openai` (Azure OpenAI via OpenAI SDK)
- **RAG/Search**: `mock-search` (default), `azure-ai-search` (Azure Search Documents SDK)
- **STT/TTS**: `mock-stt` / `mock-tts` (default), `azure-speech` (Azure Cognitive Services Speech SDK)
- **ServiceDesk**: `mock-servicedesk` (default), `servicenow` (OAuth client credentials), `jira-sm` (PAT/OAuth), `remedy` (basic auth)

## Adding a new connector
1. Implement the relevant protocol in `backend/app/connectors/<type>/`.
2. Register provider metadata (capabilities, supported models/voices, `requires_auth`) in `ServiceRegistry`.
3. Wire the connector instance in `AgentRuntime` keyed by provider ID.
4. Confirm `/v1/registry` exposes it and `/v1/admin/config/validate` returns a status.
