from typing import Any, Dict, List

from ..base import RAGConnector


class MockSearchConnector(RAGConnector):
    async def search(self, query: str, top_k: int, index_name: str) -> List[Dict[str, Any]]:
        return [
            {"text": f"Mock snippet {i+1} from {index_name} about {query}", "score": 1 - i * 0.1}
            for i in range(top_k)
        ]

    async def validate(self) -> Dict[str, Any]:
        return {"status": "ok", "reason": "mock search available"}
