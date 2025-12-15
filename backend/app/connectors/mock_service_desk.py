import uuid
from typing import Any, Dict

from .base import Connector


class MockServiceDeskConnector(Connector):
    name = "service_desk"

    def run(self, message: str, session_id: str) -> Dict[str, Any]:
        trace_id = str(uuid.uuid4())
        return {
            "target": self.name,
            "response": f"Ticket created for '{message}'",
            "trace_id": trace_id,
        }
