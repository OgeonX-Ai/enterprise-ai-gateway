from typing import Any, Dict, List

from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType

from ..base import RAGConnector


class AzureAISearchConnector(RAGConnector):
    def __init__(self, endpoint: str, key: str) -> None:
        self.endpoint = endpoint
        self.key = key

    def _client(self, index_name: str) -> SearchClient:
        return SearchClient(endpoint=self.endpoint, index_name=index_name, credential=self.key)

    async def search(self, query: str, top_k: int, index_name: str) -> List[Dict[str, Any]]:
        client = self._client(index_name)
        results = client.search(query, query_type=QueryType.SIMPLE, top=top_k)
        snippets = []
        for doc in results:
            snippets.append({"text": doc.get("content", ""), "score": doc.get("@search.score", 0)})
        return snippets

    async def validate(self) -> Dict[str, Any]:
        try:
            client = self._client("dummy")
            _ = client._client  # type: ignore[attr-defined]
            return {"status": "ok", "reason": "Azure AI Search client constructed"}
        except Exception as exc:  # noqa: BLE001
            return {"status": "error", "reason": str(exc)}
