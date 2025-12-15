from datetime import datetime
from typing import Any, Dict, List

from ..base import LLMConnector


class MockLLMConnector(LLMConnector):
    async def generate(self, messages: List[Dict[str, str]], settings: Dict[str, Any]) -> str:
        last_user = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
        timestamp = datetime.utcnow().isoformat()
        return f"[MockLLM @ {timestamp}] You said: {last_user}. Responding via {settings.get('model', 'echo')}"
