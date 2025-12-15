import uuid
from typing import Any, Dict

from .base import Connector


class MockLLMConnector(Connector):
    name = "llm"

    def run(self, message: str, session_id: str) -> Dict[str, Any]:
        trace_id = str(uuid.uuid4())
        return {
            "target": self.name,
            "response": f"LLM response for '{message}'",
            "trace_id": trace_id,
        }
