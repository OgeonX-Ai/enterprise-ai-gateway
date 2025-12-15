from typing import Any, Dict, Optional

import httpx

from ..base import ServiceDeskConnector


class ServiceNowConnector(ServiceDeskConnector):
    def __init__(self, instance_url: str, client_id: str, client_secret: str) -> None:
        self.instance_url = instance_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self._token: Optional[str] = None

    async def _get_token(self) -> str:
        if self._token:
            return self._token
        token_url = f"{self.instance_url}/oauth_token.do"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            self._token = data.get("access_token", "")
        return self._token or ""

    async def _headers(self) -> Dict[str, str]:
        token = await self._get_token()
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    async def create_ticket(self, title: str, body: str, severity: str, requester: str | None = None) -> Dict[str, Any]:
        url = f"{self.instance_url}/api/now/table/incident"
        payload = {"short_description": title, "description": body, "urgency": severity}
        if requester:
            payload["caller_id"] = requester
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=await self._headers(), json=payload)
            resp.raise_for_status()
            data = resp.json().get("result", {})
            return {"id": data.get("number", ""), "raw": data}

    async def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        url = f"{self.instance_url}/api/now/table/incident?sysparm_query=number={ticket_id}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=await self._headers())
            resp.raise_for_status()
            results = resp.json().get("result", [])
            return results[0] if results else {}

    async def search_kb(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        url = f"{self.instance_url}/api/now/table/kb_knowledge?sysparm_query=123TEXTQUERY321={query}&sysparm_limit={top_k}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=await self._headers())
            resp.raise_for_status()
            return resp.json().get("result", [])

    async def validate(self) -> Dict[str, Any]:
        try:
            await self._get_token()
            return {"status": "ok", "reason": "ServiceNow token retrieved"}
        except Exception as exc:  # noqa: BLE001
            return {"status": "error", "reason": str(exc)}
