import asyncio


class Response:
    def __init__(self, json_data=None, status_code: int = 200):
        self._json = json_data or {}
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class AsyncClient:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, *args, **kwargs):
        return Response({"access_token": "stub"})

    async def get(self, *args, **kwargs):
        return Response({"result": []})
