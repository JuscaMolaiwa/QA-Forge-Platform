import threading
from collections import deque
from typing import Optional

from utils.logger import get_logger

logger = get_logger(__name__)


class QueueManager:
    """Thread-safe FIFO queue for pending test session IDs."""

    def __init__(self, max_size: int = 50):
        self._queue: deque[str] = deque()
        self._lock = threading.Lock()
        self.max_size = max_size

    def enqueue(self, session_id: str) -> bool:
        with self._lock:
            if len(self._queue) >= self.max_size:
                logger.warning("Queue full — rejected session %s", session_id)
                return False
            self._queue.append(session_id)
            logger.info("Enqueued session %s (queue depth: %d)", session_id, len(self._queue))
            return True

    def dequeue(self) -> Optional[str]:
        with self._lock:
            if self._queue:
                session_id = self._queue.popleft()
                logger.info("Dequeued session %s", session_id)
                return session_id
            return None

    def remove(self, session_id: str) -> bool:
        with self._lock:
            try:
                self._queue.remove(session_id)
                logger.info("Removed session %s from queue", session_id)
                return True
            except ValueError:
                return False

    def depth(self) -> int:
        with self._lock:
            return len(self._queue)

    def snapshot(self) -> list:
        with self._lock:
            return list(self._queue)

    def clear(self) -> None:
        with self._lock:
            self._queue.clear()
