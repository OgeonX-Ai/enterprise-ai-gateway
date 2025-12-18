from __future__ import annotations

import asyncio
import datetime
import json
import logging
import threading
from collections import deque
from typing import Deque, Dict, Optional, Set


class CorrelationIdFilter(logging.Filter):
    """Ensure every log record has a correlation_id to keep formatting safe."""

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - trivial
        if not hasattr(record, "correlation_id"):
            record.correlation_id = "-"
        return True


class JsonLogFormatter(logging.Formatter):
    """Render log records as JSON lines with a consistent schema."""

    default_event = "log"

    def format(self, record: logging.LogRecord) -> str:  # pragma: no cover - formatting logic
        ts = datetime.datetime.utcnow().isoformat(timespec="milliseconds") + "Z"
        message = record.getMessage()
        base: Dict[str, object] = {
            "ts": ts,
            "level": record.levelname.upper(),
            "event": getattr(record, "event", self.default_event),
            "message": message,
            "logger": record.name,
            "correlation_id": getattr(record, "correlation_id", "-"),
        }

        # Capture non-standard attributes to preserve structured context
        standard_attrs = set(logging.LogRecord(None, None, "", 0, "", (), None).__dict__.keys())
        for key, value in record.__dict__.items():
            if key in standard_attrs or key in base:
                continue
            base[key] = value

        if record.exc_info:
            base["error_type"] = record.exc_info[0].__name__ if record.exc_info[0] else "Exception"
            base["error_message"] = str(record.exc_info[1])
            base["stack"] = self.formatException(record.exc_info)

        if record.stack_info:
            base["stack_info"] = record.stack_info

        return json.dumps(base, default=str)


class LogStreamBroadcaster:
    """In-memory log buffer with broadcast support for SSE consumers."""

    def __init__(self, maxlen: int = 200, replay: int = 50) -> None:
        self.buffer: Deque[str] = deque(maxlen=maxlen)
        self.replay = replay
        self.listeners: Set[asyncio.Queue[str]] = set()
        self._lock = threading.Lock()

    async def subscribe(self) -> asyncio.Queue[str]:
        queue: asyncio.Queue[str] = asyncio.Queue()
        with self._lock:
            # Seed with recent history so new listeners see immediate output
            for line in list(self.buffer)[-self.replay :]:
                queue.put_nowait(line)
            self.listeners.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[str]) -> None:
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
    json_formatter = JsonLogFormatter()
    handler.setFormatter(json_formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.addFilter(CorrelationIdFilter())

    # Ensure standard output still receives logs
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(json_formatter)
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


def log_event(
    logger: logging.LoggerAdapter,
    level: int,
    event: str,
    message: str,
    *,
    exc_info=None,
    **fields,
) -> None:
    """Convenience helper to emit structured events consistently."""

    logger.log(level, message, extra={"event": event, **fields}, exc_info=exc_info)
