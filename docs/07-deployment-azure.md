# Deployment - Azure

A staged path from local mocks to production-grade Azure services.

## Step plan
1. Containerize FastAPI runtime; deploy to Azure Container Apps with managed identity.
2. Store configuration and secrets in Azure Key Vault; mount via managed identity.
3. Front door via API Management or Azure Front Door to expose `/v1/*` with policies.
4. Wire Azure OpenAI, Azure Speech, and Azure AI Search using the provided stubs as interfaces.
5. Add private endpoints to restrict traffic inside the virtual network.
6. Enable CI/CD with GitHub Actions (build, test, container push, deploy to ACA).

## GitHub Actions outline
- Lint and type-check (future)
- Run unit tests
- Build container image
- Push to Azure Container Registry
- Deploy to Azure Container Apps
- Smoke test `/healthz` and `/v1/registry`
