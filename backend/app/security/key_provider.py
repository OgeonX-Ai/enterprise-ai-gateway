"""Placeholder for future secure key retrieval (e.g., Azure Key Vault)."""

from typing import Optional


def get_secret(name: str) -> Optional[str]:
    """Retrieve secrets from a secure provider.

    In local/mock mode this simply returns None. Integrate with Azure Key Vault or
    another provider before enabling production ServiceNow connectivity.
    """

    return None
