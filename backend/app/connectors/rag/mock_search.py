from typing import Any, Dict, List

from ..base import RAGConnector


class MockSearchConnector(RAGConnector):
    async def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        return [
            {"title": "Mock KB", "snippet": f"Answering '{query}' from mock corpus", "score": 0.9},
            {"title": "Playbook", "snippet": "Escalate to service desk if unresolved", "score": 0.6},
        ][:top_k]
