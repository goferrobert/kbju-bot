from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
from threading import Lock

class Cache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, ttl: int = 3600, max_size: int = 1000):
        """
        Initialize cache.
        
        Args:
            ttl: Time to live in seconds
            max_size: Maximum number of items
        """
        self.ttl = ttl
        self.max_size = max_size
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if not found or expired
        """
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                    return value
                else:
                    del self.cache[key]
            return None
    
    def set(self, key: str, value: Any):
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with self.lock:
            # Check cache size
            if len(self.cache) >= self.max_size:
                # Remove oldest item
                oldest_key = min(
                    self.cache.keys(),
                    key=lambda k: self.cache[k][1]
                )
                del self.cache[oldest_key]
            
            # Add new item
            self.cache[key] = (value, datetime.now())
    
    def delete(self, key: str):
        """
        Delete value from cache.
        
        Args:
            key: Cache key
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
    
    def clear(self):
        """Clear all cached values."""
        with self.lock:
            self.cache.clear()
    
    def get_many(self, keys: list) -> Dict[str, Any]:
        """
        Get multiple values from cache.
        
        Args:
            keys: List of cache keys
        
        Returns:
            Dictionary with cached values
        """
        result = {}
        with self.lock:
            for key in keys:
                if key in self.cache:
                    value, timestamp = self.cache[key]
                    if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                        result[key] = value
                    else:
                        del self.cache[key]
        return result
    
    def set_many(self, items: Dict[str, Any]):
        """
        Set multiple values in cache.
        
        Args:
            items: Dictionary with key-value pairs
        """
        with self.lock:
            for key, value in items.items():
                # Check cache size
                if len(self.cache) >= self.max_size:
                    # Remove oldest item
                    oldest_key = min(
                        self.cache.keys(),
                        key=lambda k: self.cache[k][1]
                    )
                    del self.cache[oldest_key]
                
                # Add new item
                self.cache[key] = (value, datetime.now())
    
    def delete_many(self, keys: list):
        """
        Delete multiple values from cache.
        
        Args:
            keys: List of cache keys
        """
        with self.lock:
            for key in keys:
                if key in self.cache:
                    del self.cache[key]
    
    def get_ttl(self, key: str) -> Optional[int]:
        """
        Get remaining TTL for key.
        
        Args:
            key: Cache key
        
        Returns:
            Remaining TTL in seconds or None if not found
        """
        with self.lock:
            if key in self.cache:
                _, timestamp = self.cache[key]
                ttl = self.ttl - (datetime.now() - timestamp).total_seconds()
                return max(0, int(ttl))
            return None
    
    def touch(self, key: str):
        """
        Update timestamp for key.
        
        Args:
            key: Cache key
        """
        with self.lock:
            if key in self.cache:
                value, _ = self.cache[key]
                self.cache[key] = (value, datetime.now())
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'ttl': self.ttl
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert cache to dictionary.
        
        Returns:
            Dictionary with cache contents
        """
        with self.lock:
            return {
                key: value for key, (value, _) in self.cache.items()
            }
    
    def from_dict(self, data: Dict[str, Any]):
        """
        Load cache from dictionary.
        
        Args:
            data: Dictionary with cache contents
        """
        with self.lock:
            self.clear()
            for key, value in data.items():
                self.set(key, value)

# Create default cache instance
cache = Cache() 