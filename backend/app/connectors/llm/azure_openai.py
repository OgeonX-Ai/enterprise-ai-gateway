import time
from typing import Any, Dict, List, Optional

from openai import AsyncAzureOpenAI

from ..base import LLMConnector


class AzureOpenAIConnector(LLMConnector):
    def __init__(
        self, endpoint: str, api_key: str, api_version: str, deployment_map: Optional[Dict[str, str]] | None = None
    ) -> None:
        self.client = AsyncAzureOpenAI(azure_endpoint=endpoint, api_key=api_key, api_version=api_version)
        self.deployment_map = deployment_map or {}

    def _resolve_model(self, model: str) -> str:
        return self.deployment_map.get(model, model)

    async def generate(
        self, messages: List[Dict[str, str]], model: str, temperature: float = 0.2, max_tokens: int = 256
    ) -> Dict[str, Any]:
        start = time.time()
        deployment = self._resolve_model(model)
        response = await self.client.chat.completions.create(
            model=deployment,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        text = response.choices[0].message.content or ""
        latency_ms = int((time.time() - start) * 1000)
        usage = response.usage.model_dump() if hasattr(response, "usage") else {}
        return {"text": text, "usage": usage, "latency_ms": latency_ms, "model": deployment}

    async def validate(self) -> Dict[str, Any]:
        try:
            await self.client.models.list()
            return {"status": "ok", "reason": "Azure OpenAI credentials loaded"}
        except Exception as exc:  # noqa: BLE001
            return {"status": "error", "reason": str(exc)}
