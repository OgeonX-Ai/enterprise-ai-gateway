from abc import ABC, abstractmethod
from typing import Any, Dict


class Connector(ABC):
    """Base connector interface for routing targets."""

    name: str

    @abstractmethod
    def run(self, message: str, session_id: str) -> Dict[str, Any]:
        """Execute the connector logic."""
        raise NotImplementedError
