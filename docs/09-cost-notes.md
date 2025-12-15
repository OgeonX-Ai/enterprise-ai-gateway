# Cost Notes

## Drivers
- LLM tokens (prompt + completion) by provider/model
- Search indexes and replicas for RAG
- Speech minutes for STT/TTS
- Service desk API calls (usually per-request or per-ticket)

## Profiles
- **Dev**: mock providers by default, minimal spend; short TTL on indexes.
- **Prod**: Azure OpenAI + Azure Speech + Azure AI Search with capacity planning and budgets.

See the [Azure Scalability Report](azure/scalability-report.md) for quota-aware sizing guidance that complements these cost checkpoints.

## Guardrails
- Max token and prompt size limits per channel
- Caching and reuse of RAG results where possible
- Rate limits by channel to prevent runaway costs
- Observability dashboards for cost anomalies
