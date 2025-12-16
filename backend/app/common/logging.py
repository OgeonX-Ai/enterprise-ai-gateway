from __future__ import annotations

import logging
import threading
from collections import deque
from typing import Deque, Optional, Set


LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] [correlation_id=%(correlation_id)s] %(message)s"


class CorrelationIdFilter(logging.Filter):
    """Ensure every log record has a correlation_id to keep formatting safe."""

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - trivial
        if not hasattr(record, "correlation_id"):
            record.correlation_id = "-"
        return True


class LogStreamBroadcaster:
    """In-memory log buffer with broadcast support for SSE consumers."""

    def __init__(self, maxlen: int = 200, replay: int = 50) -> None:
        self.buffer: Deque[str] = deque(maxlen=maxlen)
        self.replay = replay
        self.listeners: Set["asyncio.Queue[str]"] = set()
        self._lock = threading.Lock()

    async def subscribe(self) -> "asyncio.Queue[str]":
        import asyncio

        queue: asyncio.Queue[str] = asyncio.Queue()
        with self._lock:
            # Seed with recent history so new listeners see immediate output
            for line in list(self.buffer)[-self.replay :]:
                queue.put_nowait(line)
            self.listeners.add(queue)
        return queue

    def unsubscribe(self, queue: "asyncio.Queue[str]") -> None:
        with self._lock:
            self.listeners.discard(queue)

    def publish(self, line: str) -> None:
        import asyncio

        with self._lock:
            self.buffer.append(line)
            listeners_snapshot = list(self.listeners)
        for queue in listeners_snapshot:
            try:
                queue.put_nowait(line)
            except asyncio.QueueFull:
                # Drop if consumer is too slow; SSE clients will reconnect
                continue


class BroadcastLogHandler(logging.Handler):
    """Logging handler that forwards formatted lines to the broadcaster."""

    def __init__(self, broadcaster: LogStreamBroadcaster) -> None:
        super().__init__(level=logging.INFO)
        self.broadcaster = broadcaster

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - thin wrapper
        try:
            msg = self.format(record)
            self.broadcaster.publish(msg)
        except Exception:  # noqa: BLE001
            self.handleError(record)


def configure_logging(level: int = logging.INFO) -> LogStreamBroadcaster:
    broadcaster = LogStreamBroadcaster()
    handler = BroadcastLogHandler(broadcaster)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.addFilter(CorrelationIdFilter())

    # Ensure standard output still receives logs
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    stream_handler.addFilter(CorrelationIdFilter())
    root_logger.addHandler(stream_handler)

    return broadcaster


def get_logger(name: str) -> logging.LoggerAdapter:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logging.LoggerAdapter(logger, {"correlation_id": "-"})


def bind_correlation_id(logger: logging.LoggerAdapter, correlation_id: Optional[str]) -> logging.LoggerAdapter:
    logger.extra["correlation_id"] = correlation_id or "-"
    return logger
