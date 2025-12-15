# Agent Runtime

The runtime owns request orchestration from policy enforcement to response shaping. It is intentionally single-agent: all channels and connectors share one memory and policy engine.

## Pipeline steps
1. **Normalize request**: validate provider selection, channel, and message.
2. **Policy gate**: enforce length limits and redact PII before persisting.
3. **Context building**: merge session history with optional RAG snippets.
4. **LLM generation**: call the selected provider/model to craft the assistant reply.
5. **Tool/action calling**: check intent via runtime router and trigger service desk actions (create/status) when rules match.
6. **Response shaping**: store assistant reply, include provider selections and optional debug payload, and return correlation ID.
7. **Logging & correlation**: structured log lines include providers, RAG usage, service desk actions, and correlation IDs for tracing.

## Policy highlights
- Max message length enforcement (4k chars in demo)
- PII redaction for simple patterns (SSNs, card numbers)
- Placeholder for rate limits per channel/provider

## Memory model
- In-memory store keyed by session ID
- Stores both user and assistant turns
- Swappable for Redis or Cosmos with the same interface
