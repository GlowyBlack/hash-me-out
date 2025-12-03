# app/utils/cache.py

from threading import RLock
from typing import Any, Dict, Tuple

class Cache:
    """
    Simple thread-safe in-memory cache.
    """
    def __init__(self):
        self._lock = RLock()
        self._store: Dict[Any, Any] = {}

    def get(self, key: Any):
        with self._lock:
            return self._store.get(key)

    def set(self, key: Any, value: Any):
        with self._lock:
            self._store[key] = value

    def invalidate(self, key: Any):
        with self._lock:
            if key in self._store:
                del self._store[key]

    def clear(self):
        with self._lock:
            self._store.clear()


# GLOBAL CACHES
user_vector_cache = Cache()
similarity_cache = Cache()
