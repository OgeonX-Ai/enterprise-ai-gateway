# Connectors

Connectors implement clear interfaces so the runtime can swap between mock, stub, and production providers without UI changes.

## Contracts
- **LLMConnector**: `generate(messages, settings) -> str`
- **SpeechConnector**: `transcribe(audio_payload, settings) -> str` and `synthesize(text, settings) -> str`
- **RAGConnector**: `search(query, top_k=3) -> List[Dict]`
- **ServiceDeskConnector**: `create_ticket(title, description)`, `update_ticket(ticket_id, comment)`, `get_ticket(ticket_id)`

## Available implementations
- **LLM**: `mock-llm`, `azure-openai` (stub)
- **RAG/Search**: `mock-search`, `azure-ai-search` (stub)
- **STT**: `mock-stt`, `azure-speech-stt` (stub)
- **TTS**: `mock-tts`, `azure-speech-tts` (stub)
- **ServiceDesk**: `servicenow`, `remedy`, `jira-sm` (stubs)

## Adding a new connector
1. Implement the relevant protocol in `backend/app/connectors/<type>/`.
2. Register the provider metadata in `ServiceRegistry` with capabilities and supported models.
3. Wire the connector instance in `AgentRuntime` so it can be selected by ID.
4. Confirm `/v1/registry` exposes it for UI dropdowns.
