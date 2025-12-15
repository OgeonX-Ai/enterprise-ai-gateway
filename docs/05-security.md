# Security

## Key principles
- No secrets in the frontend. The backend owns credentials and loads them from `.env` locally; future state uses Azure Key Vault + Managed Identity.
- Centralized policy enforcement and redaction to reduce data leakage.
- RBAC on the control plane when admin APIs are introduced.

## Current secrets model
- `.env` carries connector keys (Azure OpenAI, Speech, Search, ServiceNow/Jira/Remedy) only on the backend.
- Feature flags (`USE_*`) keep mocks active unless explicitly enabled.
- `/v1/registry` and `/v1/admin/config/validate` expose configuration state without ever echoing secret values.

## Redaction strategy
- Regex-based PII redaction for common identifiers before persistence or connector calls.
- Extend with classification-based redaction when moving to production.

## Audit logging plan
- Structured logs with correlation IDs per request.
- Capture provider selections, RAG usage, and service desk actions for traceability.
- Target alignment with ISO 27001-style controls (immutability, retention policies).

## RBAC concept
- Delivery plane is open for demo; in production, protect `/v1/*` with Entra ID or OAuth2.
- Control plane (registry/admin) to require admin role and enforce least privilege scopes.
