# Routing

Routing is intentionally simple to make the control-plane concept easy to demo.

## Request model

```json
{
  "session_id": "abc-123",
  "target": "llm",
  "message": "Summarize this support ticket"
}
```

- `session_id`: Used to bind context in memory.
- `target`: Lookup key for the connector registry.
- `message`: Content for the connector to process.

## Response model

```json
{
  "target": "llm",
  "response": "Mocked summary...",
  "trace_id": "generated-uuid",
  "memory": {
    "history": [
      {
        "sender": "user",
        "content": "Summarize this support ticket"
      },
      {
        "sender": "llm",
        "content": "Mocked summary..."
      }
    ]
  }
}
```

## Current strategy

1. Validate the request with Pydantic models.
2. Resolve a connector by `target`; return 404 if missing.
3. Execute the connector’s `run` method, capturing a trace ID.
4. Update memory history for the session.
5. Return a normalized payload to the caller.

## Extending routing rules

- Add policy checks (e.g., allowed providers per tenant or role).
- Route based on message type or metadata (e.g., audio vs. text).
- Implement circuit breakers and retries per connector.
- Emit structured events to an audit log or observability pipeline.
