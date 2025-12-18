from typing import Any, Dict

import httpx

from ..base import ServiceDeskConnector


class RemedyConnector(ServiceDeskConnector):
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password

    async def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(auth=(self.username, self.password))

    async def create_ticket(self, title: str, body: str, severity: str, requester: str | None = None) -> Dict[str, Any]:
        url = f"{self.base_url}/api/arsys/v1/entry/HPD:IncidentInterface_Create"
        payload = {
            "values": {
                "Description": body,
                "Reported Source": "AI Gateway",
                "Impact": severity,
                "Summary": title,
            }
        }
        async with await self._client() as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return {"id": data.get("Incident Number", ""), "raw": data}

    async def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/api/arsys/v1/entry/HPD:IncidentInterface/{ticket_id}"
        async with await self._client() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

    async def search_kb(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        url = f"{self.base_url}/api/arsys/v1/entry/KB:KnowledgeArticleManager"
        params = {"q": query, "limit": top_k}
        async with await self._client() as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

    async def validate(self) -> Dict[str, Any]:
        try:
            async with await self._client() as client:
                resp = await client.get(f"{self.base_url}/api/arsys/v1/entry")
                return {"status": "ok" if resp.is_success else "error", "reason": f"HTTP {resp.status_code}"}
        except Exception as exc:  # noqa: BLE001
            return {"status": "error", "reason": str(exc)}
