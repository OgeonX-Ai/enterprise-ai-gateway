# Roadmap

## Near term

- Add authentication middleware and role-based connector access.
- Replace mock connectors with SDK-backed adapters (Azure OpenAI, AWS Bedrock, Google, etc.).
- Persist memory to Redis and add TTL-based cleanup.
- Add CI checks for linting, type safety, and tests.

## Azure migration path

1. Containerize the FastAPI gateway; publish to Azure Container Registry.
2. Run the service on Azure Container Apps or AKS with managed identity.
3. Store secrets in Azure Key Vault; mount via environment variables.
4. Use Azure Cache for Redis for session memory.
5. Add Azure Application Gateway or API Management for ingress, throttling, and observability.

## Stretch goals

- WebSocket streaming for LLM and TTS responses.
- Admin UI for connector management and policy configuration.
- Event export to SIEM/observability tools (e.g., Azure Monitor, Datadog, Splunk).
- Pluggable tracing (OpenTelemetry) to instrument connectors.
