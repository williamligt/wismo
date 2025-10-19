from datetime import datetime, timedelta
import threading
from typing import Any, Optional, Dict, Tuple

class TTLCache:
    """
    A thread-safe cache with time-to-live (TTL) functionality.
    Items automatically expire after the specified time period.
    """
    
    def __init__(self, ttl_hours: float = 1.0):
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.ttl = timedelta(hours=ttl_hours)
        self.lock = threading.Lock()
        
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if datetime.now() - timestamp < self.ttl:
                    return value
                else:
                    del self.cache[key]
            return None
    
    def set(self, key: str, value: Any) -> None:
        with self.lock:
            self.cache[key] = (value, datetime.now())
    
    def clear(self) -> None:
        with self.lock:
            self.cache.clear()
    
    def cleanup_expired(self) -> int:
        with self.lock:
            current_time = datetime.now()
            expired_keys = [
                key for key, (value, timestamp) in self.cache.items()
                if current_time - timestamp >= self.ttl
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            return len(expired_keys)
    
    def stats(self) -> Dict[str, Any]:
        with self.lock:
            current_time = datetime.now()
            valid_entries = sum(
                1 for _, (_, timestamp) in self.cache.items()
                if current_time - timestamp < self.ttl
            )
            
            return {
                "total_entries": len(self.cache),
                "valid_entries": valid_entries,
                "expired_entries": len(self.cache) - valid_entries,
                "ttl_hours": self.ttl.total_seconds() / 3600,
                "cache_keys": list(self.cache.keys())
            }