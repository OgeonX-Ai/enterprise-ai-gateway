# Security posture (demo-friendly)

The demo favors portability and speed, but the architecture is designed to be hardened for production deployments.

## What is in place

- Clear separation between stateless routing and stateful memory.
- Connector registry keeps provider-specific logic isolated.
- Request/response models enforce payload validation.

## Hardening checklist

- **Authentication & authorization**: Add JWT or OIDC auth and per-tenant permissions on connectors.
- **Secrets management**: Load provider keys from vault-backed environment variables.
- **Transport security**: Terminate TLS at the gateway or a reverse proxy; restrict CORS.
- **Auditability**: Emit structured logs with trace IDs and connector outcomes.
- **Data handling**: Classify message content and redact sensitive fields before logging.
- **Reliability**: Add circuit breakers, retries, and rate limits per connector.

## Network and deployment considerations

- Place the gateway behind an API gateway or ingress controller.
- Run connectors in isolated workloads with least-privilege credentials.
- Store memory in a managed cache (e.g., Redis) for multi-instance deployments.
