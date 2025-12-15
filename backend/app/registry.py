from typing import Dict, Iterable, Optional

from .connectors.base import Connector


class ConnectorRegistry:
    """In-memory connector registry for demo purposes."""

    def __init__(self) -> None:
        self._connectors: Dict[str, Connector] = {}

    def register(self, connector: Connector) -> None:
        self._connectors[connector.name] = connector

    def list(self) -> Iterable[str]:
        return self._connectors.keys()

    def get(self, target: str) -> Optional[Connector]:
        return self._connectors.get(target)
