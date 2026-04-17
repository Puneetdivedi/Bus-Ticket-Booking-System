"""Caching strategies and utilities."""
from typing import Any, Callable, Optional, Dict
import time
from functools import wraps


class CacheStrategy:
    """Base cache strategy."""
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        raise NotImplementedError
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        raise NotImplementedError
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        raise NotImplementedError
    
    def clear(self) -> None:
        """Clear all cache."""
        raise NotImplementedError


class InMemoryCache(CacheStrategy):
    """In-memory cache implementation."""
    
    def __init__(self):
        self._cache: Dict[str, tuple[Any, float]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with TTL check."""
        if key not in self._cache:
            return None
        
        value, expiry = self._cache[key]
        if expiry and time.time() > expiry:
            del self._cache[key]
            return None
        
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional TTL."""
        expiry = None
        if ttl:
            expiry = time.time() + ttl
        
        self._cache[key] = (value, expiry)
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """Clear all cache."""
        self._cache.clear()
    
    def size(self) -> int:
        """Get cache size."""
        return len(self._cache)


class CacheManager:
    """Centralized cache manager."""
    
    def __init__(self):
        self._caches: Dict[str, CacheStrategy] = {
            "default": InMemoryCache(),
            "bookings": InMemoryCache(),
            "seats": InMemoryCache(),
        }
    
    def get_cache(self, namespace: str = "default") -> CacheStrategy:
        """Get cache by namespace."""
        if namespace not in self._caches:
            self._caches[namespace] = InMemoryCache()
        return self._caches[namespace]
    
    def invalidate(self, namespace: str, pattern: Optional[str] = None) -> None:
        """Invalidate cache by namespace or pattern."""
        cache = self.get_cache(namespace)
        if isinstance(cache, InMemoryCache) and pattern is None:
            cache.clear()


# Global cache manager
cache_manager = CacheManager()


class cached(object):
    """Decorator for caching function results."""
    
    def __init__(self, ttl: int = 300, namespace: str = "default"):
        """Initialize cache decorator.
        
        Args:
            ttl: Time to live in seconds
            namespace: Cache namespace
        """
        self.ttl = ttl
        self.namespace = namespace
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key from function name and arguments
            cache_key = self._generate_key(func.__name__, args, kwargs)
            
            # Try to get from cache
            cache = cache_manager.get_cache(self.namespace)
            cached_value = cache.get(cache_key)
            
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, self.ttl)
            
            return result
        
        return wrapper
    
    @staticmethod
    def _generate_key(func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key from function and arguments."""
        # Simple key generation - can be improved
        key_parts = [func_name]
        
        # Add args (skip self)
        for arg in args:
            if not isinstance(arg, (object, type)):
                key_parts.append(str(arg))
        
        # Add kwargs
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        
        return ":".join(key_parts)


class CachePatterns:
    """Common caching patterns."""
    
    @staticmethod
    def cache_aside(
        key: str,
        load_func: Callable,
        ttl: int = 300,
        namespace: str = "default",
    ) -> Any:
        """Cache-aside (lazy loading) pattern."""
        cache = cache_manager.get_cache(namespace)
        
        # Try to get from cache
        value = cache.get(key)
        if value is not None:
            return value
        
        # Load from source
        value = load_func()
        
        # Store in cache
        cache.set(key, value, ttl)
        
        return value
    
    @staticmethod
    def write_through(
        key: str,
        value: Any,
        persist_func: Callable,
        ttl: int = 300,
        namespace: str = "default",
    ) -> None:
        """Write-through pattern - write to source first, then cache."""
        # Write to source
        persist_func(value)
        
        # Update cache
        cache = cache_manager.get_cache(namespace)
        cache.set(key, value, ttl)
    
    @staticmethod
    def write_behind(
        key: str,
        value: Any,
        persist_func: Callable,
        ttl: int = 300,
        namespace: str = "default",
    ) -> None:
        """Write-behind pattern - write to cache first, then source."""
        # Update cache immediately
        cache = cache_manager.get_cache(namespace)
        cache.set(key, value, ttl)
        
        # Queue write to source (should be async in production)
        # For now, just write synchronously
        persist_func(value)


# Predefined cache TTLs
CACHE_TTLS = {
    "seat_map": 300,        # 5 minutes
    "boarding_sequence": 300,  # 5 minutes
    "booking_list": 60,     # 1 minute
    "user_session": 3600,   # 1 hour
}
