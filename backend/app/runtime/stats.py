from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Deque, Optional


def _percentile(latencies: Deque[float], percentile: float) -> Optional[float]:
    if not latencies:
        return None
    ordered = sorted(latencies)
    k = (len(ordered) - 1) * percentile
    f = int(k)
    c = min(f + 1, len(ordered) - 1)
    if f == c:
        return ordered[int(k)]
    d0 = ordered[f] * (c - k)
    d1 = ordered[c] * (k - f)
    return d0 + d1


@dataclass
class StatsSnapshot:
    backend_ready: bool
    stt_ready: bool
    started_at: datetime
    total_requests: int
    total_failures: int
    last_request_at: Optional[datetime]
    last_latency_ms: Optional[float]
    latencies: Deque[float] = field(default_factory=deque)
    last_error: Optional[str] = None


class StatsTracker:
    def __init__(self, window: int = 50) -> None:
        self.started_at = datetime.now(timezone.utc)
        self.total_requests = 0
        self.total_failures = 0
        self.last_request_at: Optional[datetime] = None
        self.last_latency_ms: Optional[float] = None
        self.last_error: Optional[str] = None
        self.latencies: Deque[float] = deque(maxlen=window)

    def record(self, latency_ms: float, error: Optional[Exception] = None) -> None:
        self.total_requests += 1
        self.last_request_at = datetime.now(timezone.utc)
        self.last_latency_ms = round(latency_ms, 2)
        self.latencies.append(self.last_latency_ms)
        if error:
            self.total_failures += 1
            self.last_error = str(error)[:160]

    def snapshot(self) -> StatsSnapshot:
        return StatsSnapshot(
            backend_ready=True,
            stt_ready=True,
            started_at=self.started_at,
            total_requests=self.total_requests,
            total_failures=self.total_failures,
            last_request_at=self.last_request_at,
            last_latency_ms=self.last_latency_ms,
            latencies=self.latencies,
            last_error=self.last_error,
        )

    def percentiles(self) -> tuple[Optional[float], Optional[float]]:
        p50 = _percentile(self.latencies, 0.5)
        p95 = _percentile(self.latencies, 0.95)
        return (p50, p95)
