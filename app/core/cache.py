import threading
from typing import Optional, Dict
from app.core.config import settings

class URLCache:
    """
    Thread-safe in-memory Cache-Aside layer.
    Optimizes hot key lookups without hitting disk I/O.
    """
    def __init__(self, capacity: int = settings.CACHE_CAPACITY):
        self.capacity = capacity
        self.cache: Dict[str, str] = {}
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[str]:
        with self.lock:
            return self.cache.get(key)

    def set(self, key: str, original_url: str) -> None:
        with self.lock:
            if len(self.cache) >= self.capacity:
                first_key = next(iter(self.cache))
                del self.cache[first_key]
            self.cache[key] = original_url

    def invalidate(self, key: str) -> None:
        with self.lock:
            self.cache.pop(key, None)

    def count(self) -> int:
        with self.lock:
            return len(self.cache)

cache = URLCache()
