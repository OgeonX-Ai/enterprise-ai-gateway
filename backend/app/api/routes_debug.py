from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from ..common.logging import LogStreamBroadcaster
from ..settings import Settings

router = APIRouter(prefix="/v1/debug")


@router.get("/stream")
async def debug_stream(request: Request) -> StreamingResponse:
    settings: Settings = request.app.state.settings
    broadcaster: LogStreamBroadcaster = request.app.state.log_stream

    if not settings.enable_debug_stream and request.client:
        client_host = request.client.host
        if client_host not in {"127.0.0.1", "localhost", "::1"}:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Debug stream disabled; set ENABLE_DEBUG_STREAM=true for local use.",
            )

    async def event_generator():
        queue = await broadcaster.subscribe()
        try:
            while True:
                line = await queue.get()
                yield f"data: {line}\n\n"
        except asyncio.CancelledError:  # pragma: no cover - streaming cancellation
            raise
        finally:
            broadcaster.unsubscribe(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
