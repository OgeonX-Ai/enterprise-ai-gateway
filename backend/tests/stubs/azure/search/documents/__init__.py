from typing import Any, Iterable, List

from .models import QueryType


class SearchClient:
    def __init__(self, endpoint: str, index_name: str, credential: Any = None):
        self.endpoint = endpoint
        self.index_name = index_name
        self.credential = credential

    def search(self, query: str, query_type: QueryType | None = None, top: int | None = None) -> Iterable[dict]:
        # Return a simple iterable of mock documents
        return [{"content": f"stub result for {query}", "@search.score": 1.0} for _ in range(top or 1)]
