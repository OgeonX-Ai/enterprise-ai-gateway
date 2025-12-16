import httpx

from ...common.logging import get_logger
from .config import ServiceNowConfig


class ServiceNowClient:
    def __init__(self, config: ServiceNowConfig):
        if not config.instance_url:
            raise ValueError("ServiceNow instance URL is required for real mode")
        self.config = config
        self.logger = get_logger(__name__)
        self._client = httpx.AsyncClient(
            base_url=config.instance_url.rstrip("/"),
            timeout=10.0,
        )

    async def _request(self, method: str, url: str, **kwargs):
        auth = None
        if self.config.auth_mode == "basic" and self.config.username and self.config.password:
            auth = httpx.BasicAuth(self.config.username, self.config.password)
        response = await self._client.request(method, url, auth=auth, **kwargs)
        response.raise_for_status()
        return response.json()

    async def search_incidents(self, query: str, limit: int = 5):
        params = {"sysparm_query": query, "sysparm_limit": limit}
        return await self._request("GET", "/api/now/table/incident", params=params)

    async def get_incident(self, sys_id: str):
        return await self._request("GET", f"/api/now/table/incident/{sys_id}")

    async def update_incident(self, sys_id: str, fields: dict):
        return await self._request("PATCH", f"/api/now/table/incident/{sys_id}", json=fields)

    async def add_work_note(self, sys_id: str, note: str, visibility: str = "internal"):
        payload = {"work_notes": note, "work_notes_list": [{"visibility": visibility}]}
        return await self.update_incident(sys_id, payload)

    async def close(self):
        await self._client.aclose()
