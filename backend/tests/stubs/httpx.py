

import sys
from importlib import import_module
from pathlib import Path

STUB_DIR = Path(__file__).resolve().parent
removed = False
if sys.path and sys.path[0] == str(STUB_DIR):
    sys.path.pop(0)
    removed = True

_real_httpx = import_module("httpx")

if removed:
    sys.path.insert(0, str(STUB_DIR))

Client = _real_httpx.Client
BaseTransport = getattr(_real_httpx, "BaseTransport", type("BaseTransport", (), {}))
AsyncBaseTransport = getattr(
    _real_httpx, "AsyncBaseTransport", type("AsyncBaseTransport", (), {})
)
HTTPStatusError = getattr(_real_httpx, "HTTPStatusError", Exception)


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
