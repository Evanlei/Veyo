"""Small in-process abuse bound for the single-instance public inference service."""
from collections import defaultdict, deque
import hashlib
import threading
import time
from fastapi import HTTPException, Request


class WriteLimiter:
    def __init__(self, limit=90, interval=3600, clock=time.monotonic):
        self.limit, self.interval, self.clock = limit, interval, clock
        self.events = defaultdict(deque)
        self.lock = threading.Lock()

    def check(self, identity: str):
        current = self.clock()
        with self.lock:
            for client in list(self.events):
                queue = self.events[client]
                while queue and current-queue[0] >= self.interval:
                    queue.popleft()
                if not queue:
                    del self.events[client]
            queue = self.events[identity]
            if len(queue) >= self.limit or len(self.events) > 10000:
                raise HTTPException(429, "This connection has made many changes. Please try again later.",
                                    headers={"Retry-After": "60"})
            queue.append(current)


def limit_writes(request: Request):
    if request.method in {"POST", "PUT", "PATCH"}:
        remote = request.client.host if request.client else "unknown"
        request.app.state.write_limiter.check(hashlib.sha256(remote.encode()).hexdigest())
