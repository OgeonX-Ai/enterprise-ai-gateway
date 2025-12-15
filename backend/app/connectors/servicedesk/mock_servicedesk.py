from typing import Any, Dict, List

from ..base import ServiceDeskConnector


class MockServiceDeskConnector(ServiceDeskConnector):
    async def create_ticket(self, title: str, body: str, severity: str, requester: str | None = None) -> Dict[str, Any]:
        return {"id": "MOCK-1", "summary": title, "severity": severity, "requester": requester, "body": body}

    async def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        return {"id": ticket_id, "status": "In Progress", "summary": "Mock ticket"}

    async def search_kb(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        return [{"text": f"KB result for {query} #{i+1}"} for i in range(top_k)]

    async def validate(self) -> Dict[str, Any]:
        return {"status": "ok", "reason": "mock service desk available"}
