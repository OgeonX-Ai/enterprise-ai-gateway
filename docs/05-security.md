# Security

## Key principles
- No secrets in the frontend. The backend owns credentials and will later integrate with Azure Key Vault and Managed Identity.
- Centralized policy enforcement and redaction to reduce data leakage.
- RBAC on the control plane when admin APIs are introduced.

## Current secrets model
- Demo uses `.env` only for non-sensitive configuration (app name, correlation header).
- Future: Azure Key Vault + Managed Identity for connector credentials.

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
