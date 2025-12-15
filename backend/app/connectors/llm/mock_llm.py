import time
from datetime import datetime
from typing import Any, Dict, List

from ..base import LLMConnector


class MockLLMConnector(LLMConnector):
    async def generate(
        self, messages: List[Dict[str, str]], model: str, temperature: float = 0.2, max_tokens: int = 256
    ) -> Dict[str, Any]:
        start = time.time()
        last_user = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")
        timestamp = datetime.utcnow().isoformat()
        reply = f"[MockLLM @ {timestamp}] You said: {last_user}. Responding via {model}"
        return {
            "text": reply,
            "usage": {"prompt_tokens": len(last_user.split()), "completion_tokens": min(max_tokens, 32)},
            "latency_ms": int((time.time() - start) * 1000),
            "model": model,
        }

    async def validate(self) -> Dict[str, Any]:
        return {"status": "ok", "reason": "mock connector always available"}
