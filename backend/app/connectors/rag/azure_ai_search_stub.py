from typing import Any, Dict, List

from ..base import RAGConnector


class AzureAISearchStub(RAGConnector):
    async def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Azure AI Search stub",
                "snippet": f"Semantic result for '{query}'",
                "score": 0.82,
            }
        ][:top_k]
