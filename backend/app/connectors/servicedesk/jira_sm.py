from typing import Any, Dict

import httpx

from ..base import ServiceDeskConnector


class JiraServiceManagementConnector(ServiceDeskConnector):
    def __init__(self, base_url: str, email: str, api_token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.api_token = api_token

    async def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(auth=(self.email, self.api_token))

    async def create_ticket(self, title: str, body: str, severity: str, requester: str | None = None) -> Dict[str, Any]:
        url = f"{self.base_url}/rest/servicedeskapi/request"
        payload = {
            "serviceDeskId": "1",
            "requestTypeId": "1",
            "requestFieldValues": {"summary": title, "description": body},
        }
        async with await self._client() as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return {"id": data.get("issueId", ""), "key": data.get("issueKey", ""), "raw": data}

    async def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/rest/servicedeskapi/request/{ticket_id}"
        async with await self._client() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

    async def search_kb(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        url = f"{self.base_url}/rest/servicedeskapi/knowledgebase/article"
        params = {"query": query, "start": 0, "limit": top_k}
        async with await self._client() as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

    async def validate(self) -> Dict[str, Any]:
        try:
            async with await self._client() as client:
                resp = await client.get(f"{self.base_url}/rest/servicedeskapi/servicedesk")
                if resp.is_success:
                    return {"status": "ok", "reason": "Jira Service Management reachable"}
                return {"status": "error", "reason": f"HTTP {resp.status_code}"}
        except Exception as exc:  # noqa: BLE001
            return {"status": "error", "reason": str(exc)}
