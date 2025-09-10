#!/usr/bin/env python3
"""
Cache Manager for ROI Calculator
Implements in-memory caching with Redis support (when available)
"""

import json
import hashlib
import time
from typing import Any, Optional, Dict, Callable
from functools import wraps
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.info("Redis not available, using in-memory cache only")

class CacheManager:
    """Manages application caching with fallback to in-memory if Redis unavailable"""
    
    def __init__(self, redis_url: Optional[str] = None, default_ttl: int = 3600):
        """
        Initialize cache manager
        
        Args:
            redis_url: Redis connection URL (e.g., redis://localhost:6379/0)
            default_ttl: Default time-to-live in seconds
        """
        self.default_ttl = default_ttl
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.redis_client = None
        
        # Try to connect to Redis if available
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.Redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Connected to Redis cache")
            except (redis.ConnectionError, redis.TimeoutError) as e:
                logger.warning(f"Failed to connect to Redis: {e}. Using in-memory cache.")
                self.redis_client = None
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix and arguments"""
        # Create a unique key from arguments
        key_data = {
            'prefix': prefix,
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        # Try Redis first
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except (redis.ConnectionError, redis.TimeoutError, json.JSONDecodeError):
                pass
        
        # Fallback to memory cache
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if entry['expires'] > time.time():
                return entry['value']
            else:
                # Clean up expired entry
                del self.memory_cache[key]
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        ttl = ttl or self.default_ttl
        
        # Try Redis first
        if self.redis_client:
            try:
                serialized = json.dumps(value, default=str)
                self.redis_client.setex(key, ttl, serialized)
                return True
            except (redis.ConnectionError, redis.TimeoutError, TypeError):
                pass
        
        # Fallback to memory cache
        self.memory_cache[key] = {
            'value': value,
            'expires': time.time() + ttl
        }
        return True
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        deleted = False
        
        # Try Redis first
        if self.redis_client:
            try:
                deleted = bool(self.redis_client.delete(key))
            except (redis.ConnectionError, redis.TimeoutError):
                pass
        
        # Also delete from memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
            deleted = True
        
        return deleted
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        count = 0
        
        # Clear from Redis
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    count += self.redis_client.delete(*keys)
            except (redis.ConnectionError, redis.TimeoutError):
                pass
        
        # Clear from memory cache
        keys_to_delete = [k for k in self.memory_cache if pattern.replace('*', '') in k]
        for key in keys_to_delete:
            del self.memory_cache[key]
            count += 1
        
        return count
    
    def cleanup_expired(self):
        """Remove expired entries from memory cache"""
        current_time = time.time()
        expired_keys = [
            k for k, v in self.memory_cache.items()
            if v['expires'] <= current_time
        ]
        for key in expired_keys:
            del self.memory_cache[key]
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        stats = {
            'redis_connected': self.redis_client is not None,
            'memory_entries': len(self.memory_cache),
            'memory_size_bytes': sum(
                len(json.dumps(v, default=str).encode())
                for v in self.memory_cache.values()
            )
        }
        
        if self.redis_client:
            try:
                info = self.redis_client.info('memory')
                stats['redis_memory_used'] = info.get('used_memory_human', 'N/A')
                stats['redis_keys'] = self.redis_client.dbsize()
            except (redis.ConnectionError, redis.TimeoutError):
                stats['redis_connected'] = False
        
        return stats


def cached(ttl: int = 3600, key_prefix: Optional[str] = None):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Optional prefix for cache key (defaults to function name)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get or create cache manager
            if not hasattr(wrapper, '_cache_manager'):
                wrapper._cache_manager = CacheManager()
            
            # Generate cache key
            prefix = key_prefix or f"func:{func.__name__}"
            cache_key = wrapper._cache_manager._make_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            result = wrapper._cache_manager.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return result
            
            # Execute function and cache result
            logger.debug(f"Cache miss for {cache_key}")
            result = func(*args, **kwargs)
            wrapper._cache_manager.set(cache_key, result, ttl)
            
            return result
        
        # Attach cache management methods
        wrapper.clear_cache = lambda: wrapper._cache_manager.clear_pattern(
            f"{key_prefix or f'func:{func.__name__}'}:*"
        )
        
        return wrapper
    return decorator


# Global cache instance for application-wide use
_global_cache = None

def get_cache() -> CacheManager:
    """Get global cache instance"""
    global _global_cache
    if _global_cache is None:
        # Try to connect to Redis if available
        redis_url = None
        if REDIS_AVAILABLE:
            import os
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        
        _global_cache = CacheManager(redis_url=redis_url)
    
    return _global_cache


# Cache keys for different components
class CacheKeys:
    """Standard cache key prefixes"""
    ROI_CALCULATION = "roi:calc"
    COST_OPTIMIZATION = "cost:opt"
    TAX_CALCULATION = "tax:calc"
    CURRENCY_RATES = "currency:rates"
    METRICS_DASHBOARD = "metrics:dashboard"
    ML_PREDICTIONS = "ml:predict"
    USER_SESSION = "session"
    
    @staticmethod
    def roi_result(company: str, investment: float) -> str:
        """Generate key for ROI calculation result"""
        return f"{CacheKeys.ROI_CALCULATION}:{company}:{investment}"
    
    @staticmethod
    def cost_analysis(company: str) -> str:
        """Generate key for cost analysis"""
        return f"{CacheKeys.COST_OPTIMIZATION}:{company}"
    
    @staticmethod
    def exchange_rate(from_currency: str, to_currency: str) -> str:
        """Generate key for exchange rate"""
        return f"{CacheKeys.CURRENCY_RATES}:{from_currency}:{to_currency}"