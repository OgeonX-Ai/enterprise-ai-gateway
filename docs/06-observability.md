# Observability

## Correlation and tracing
- Every request receives an `X-Correlation-ID` header (generated if missing).
- Structured logs include providers, RAG usage, service desk actions, and history length.

## Metrics to track
- Request latency by channel and provider
- Token usage per LLM model
- RAG query counts and latency
- Speech minutes (STT/TTS) by locale/voice
- Service desk ticket operations and statuses
- Error rate and policy violations

## Future mapping
- Export logs and metrics to Azure Monitor / Application Insights
- Use OpenTelemetry for traces across runtime and connectors
- Enable dashboards for cost, latency, and ticket throughput
