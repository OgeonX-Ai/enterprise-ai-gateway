# Roadmap

## Phase 1: Local mock (current)
- FastAPI runtime with mock and stub connectors
- Static web UI with provider dropdowns and debug drawer

## Phase 2: Azure stubs with env flags
- Wire Azure OpenAI, Speech, and AI Search stubs to read credentials from Key Vault
- Toggle providers via configuration without UI changes

## Phase 3: Entra ID authentication
- Protect delivery plane endpoints with Entra ID
- Add admin plane for registry management

## Phase 4: Productionization
- Move memory to Redis/Cosmos
- Add structured metrics and tracing via OpenTelemetry
- Harden security (private endpoints, WAF, APIM policies)
