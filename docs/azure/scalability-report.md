# Azure Scalability Report — Speech + LLM Microservices

_Last updated: 2025-12-15_

This report summarizes capacity assumptions, deployment patterns, and operational guidance for running the Enterprise AI Gateway on Azure with Speech + LLM workloads. It is written in an Azure-style format so teams can align gateway routing, speech services, and LLM connectors with standard platform guidance.

## Applies to this repo
- **Components in scope:** FastAPI gateway in `backend/app`, mock + Azure-aligned connectors (LLM, RAG, STT/TTS, service desk), static web client in `web/`.
- **Speech/STT/TTS providers:** `azure-speech` (real) plus mock defaults; current speech routes terminate in the gateway and dispatch to the connector classes under `backend/app/connectors/speech/`.
- **LLM/RAG providers:** Azure OpenAI (via `azure-openai` connector), mock defaults, and Azure AI Search stubs for RAG.
- **Deployment modes:**
  - **Local/dev:** `DEV_MODE=true` with mock connectors and optional local Whisper; runs via `uvicorn app.main:app --app-dir backend`.
  - **Azure:** Containerized FastAPI backend deployed to Azure Container Apps or AKS with managed identity and external ingress (API Management or Front Door) routing to the gateway.

## Architecture summary
- The gateway exposes `/v1/*` APIs for chat, registry, admin config, and speech endpoints. It handles correlation IDs, policy checks, and connector routing.
- Connectors run in-process today; Azure services are called via SDKs. The design can be split into microservices later by hosting each connector behind HTTP while keeping contracts stable.
- Recommended Azure hosting:
  - **Front Door + API Management** for global entry, throttling, WAF, and versioned routes.
  - **Azure Container Apps (ACA)** for the gateway (scale-out on HTTP QPS) and background workers.
  - **Managed Identity + Key Vault** for secrets (Azure OpenAI, Speech, Search, ServiceNow/Jira/Remedy).
  - **Azure Monitor / App Insights** for logs, traces, and metrics.

## Capacity model and assumptions
- **Chat/LLM throughput:** Azure OpenAI GPT-4o supports tens to low hundreds of RPS per region depending on quota; align request fan-out with the provisioned TPM/RPM. Use `temperature` and `max_tokens` limits to cap spend.
- **Speech (Azure Cognitive Services Speech):** Expect ~50 concurrent audio streams per S0/S1 speech unit; scale by adding units or regions. Latency budget per short audio clip is typically 300–800 ms when using compressed formats.
- **Gateway layer:** Stateless HTTP pods; scale horizontally on CPU or RPS. Keep pod memory sized for audio buffering (e.g., 512 MB–1 GB per pod if storing short clips temporarily).
- **Registry + config endpoints:** Light traffic; co-host with the gateway.

## Scaling guidance
### Gateway (FastAPI) tier
- **Scale out on CPU/RPS**: ACA/KEDA HTTP concurrency target of 20–40 req/pod is a good starting point.
- **Connection pooling:** Keep `httpx` client sessions warm for Azure SDK calls; reuse across requests to reduce TLS overhead.
- **Caching:** Cache provider metadata (`/v1/registry`) for 5–10 minutes via API Management or a small in-memory cache.
- **Correlation IDs:** Preserve `X-Correlation-Id` from clients and forward to downstream connectors and Azure SDK calls for traceability.

### Speech connector tier
- **Throughput:** Azure Speech handles concurrent short utterances well; for long-form audio prefer batch transcription or streaming websockets (future). Keep request duration under API Management/Front Door idle timeouts.
- **Regions:** Pin Speech and Azure OpenAI to the same region when possible to reduce cross-region latency.
- **Resilience:** Wrap SDK calls with timeouts/retries on transient failures; map timeout/rate-limit conditions to retryable errors.
- **Cost controls:** Enable content-length validation in the gateway; reject oversize uploads and encourage compressed formats (ogg/mp3) to shrink egress.

### LLM and RAG
- **Token budgets:** Enforce `max_tokens` per request; large context windows inflate latency and cost. Prefer retrieval-augmented prompts for lengthy knowledge bases.
- **Backpressure:** If Azure OpenAI quota is saturated, return retryable errors and optionally fail over to mock connectors for non-critical flows.
- **Search fan-out:** Cap Azure AI Search `top_k` to reduce payload size and downstream tokenization costs.

### Networking and ingress
- **Ingress:** API Management or Front Door terminates TLS and applies rate limits. Route `/v1/*` to ACA/AKS; restrict private traffic for connectors that should only be called server-to-server.
- **Egress:** Use managed identity where possible; otherwise lock down Speech/OpenAI/Search endpoints via trusted IPs or private endpoints.
- **Content delivery:** Host static `web/` assets on static storage (e.g., Azure Storage static website) fronted by CDN; keep gateway only for APIs.

### Observability and reliability
- **Metrics:** Export request counts, latency histograms, and provider failure counters to Azure Monitor. Add `/metrics` endpoints to the gateway and future connector services for Prometheus scraping in AKS.
- **Tracing:** Attach correlation IDs to log entries and Application Insights traces. Enable dependency collection for Azure SDK calls.
- **Health/ready probes:** Keep `/health` fast and `/ready` dependent on downstream config (Key Vault, Azure SDK auth) to avoid cold-start errors.
- **Disaster recovery:** Deploy secondary region with read-only registry and failover DNS/Front Door routing; keep secrets synchronized via Key Vault references.

### Cost and quota management
- Track Azure OpenAI TPM/RPM quotas and Speech unit counts per region. Pre-allocate capacity for peak hours (e.g., call centers) and set API Management rate limits to avoid overage.
- Use daily cost budgets and alerts; surface estimated per-request costs in debug logs for large transcripts.

## How to run scale tests
- Start from the deployed gateway URL (local `http://localhost:8000` or Azure Front Door/APIM endpoint).
- Use load tools such as `k6` or `locust` to replay representative `/v1/chat` and speech transcription requests. Store scripts under `infra/load/` (placeholder path to be added) so they can run in CI or a scheduled job.
- Warm caches by pre-calling `/v1/registry` and a small `/v1/chat` payload before measuring throughput.
- Record metrics from Azure Monitor or `/metrics` endpoints to validate saturation points; compare against quota targets above.

## Migration to microservices
- Present design keeps connectors in-process. When extracting to standalone services (e.g., `services/gateway`, `services/connector_azure_speech`), preserve contracts from `docs/api.md` and keep the scalability assumptions above per tier.
- Prefer per-connector scaling policies (e.g., Speech connector pods scaled on audio concurrency; LLM connector on TPM utilization) while keeping gateway stateless.

## Related docs
- Architecture overview and diagrams: [`docs/architecture.md`](../architecture.md)
- Azure deployment steps: [`docs/07-deployment-azure.md`](../07-deployment-azure.md)
- Connectors overview: [`docs/03-connectors.md`](../03-connectors.md)
- API reference: [`docs/api.md`](../api.md)
