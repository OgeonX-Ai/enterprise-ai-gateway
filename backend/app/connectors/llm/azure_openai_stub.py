from typing import Any, Dict, List

from ..base import LLMConnector


class AzureOpenAIStub(LLMConnector):
    async def generate(self, messages: List[Dict[str, str]], settings: Dict[str, Any]) -> str:
        model = settings.get("model", "gpt-4o-mini")
        return (
            "[Azure OpenAI stub] Model: "
            f"{model}. This would call Azure OpenAI with managed identity in production."
        )
