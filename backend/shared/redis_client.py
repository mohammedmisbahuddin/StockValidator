"""
Shared Redis connection and utilities
"""
import redis.asyncio as redis
from typing import Optional
import json
from datetime import timedelta

from .config import settings


class RedisClient:
    """Redis client wrapper with common operations"""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Initialize Redis connection"""
        self.client = await redis.from_url(
            settings.redis_url_computed,
            encoding="utf-8",
            decode_responses=True,
        )
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
    
    async def ping(self) -> bool:
        """Check if Redis is connected"""
        try:
            return await self.client.ping()
        except Exception:
            return False
    
    # Rate limiting operations
    async def get_user_search_count(self, user_id: str) -> int:
        """Get current search count for user"""
        key = f"user:{user_id}:search_count"
        count = await self.client.get(key)
        return int(count) if count else 0
    
    async def increment_user_search_count(self, user_id: str) -> int:
        """Increment user search count and return new value"""
        key = f"user:{user_id}:search_count"
        return await self.client.incr(key)
    
    async def get_user_search_limit(self, user_id: str) -> int:
        """Get search limit for user"""
        key = f"user:{user_id}:search_limit"
        limit = await self.client.get(key)
        return int(limit) if limit else 50  # Default limit
    
    async def set_user_search_limit(self, user_id: str, limit: int):
        """Set search limit for user"""
        key = f"user:{user_id}:search_limit"
        await self.client.set(key, limit)
    
    async def reset_user_search_count(self, user_id: str):
        """Reset user search count to 0"""
        key = f"user:{user_id}:search_count"
        await self.client.set(key, 0)
    
    async def check_rate_limit(self, user_id: str) -> tuple[bool, int, int]:
        """
        Check if user has exceeded rate limit.
        Returns: (is_allowed, current_count, limit)
        """
        current_count = await self.get_user_search_count(user_id)
        limit = await self.get_user_search_limit(user_id)
        is_allowed = current_count < limit
        return is_allowed, current_count, limit
    
    # Caching operations
    async def get_cached(self, key: str) -> Optional[dict]:
        """Get cached data"""
        data = await self.client.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def set_cached(self, key: str, value: dict, ttl: int = 3600):
        """
        Set cached data with TTL.
        Default TTL: 1 hour (3600 seconds)
        """
        await self.client.setex(
            key,
            ttl,
            json.dumps(value)
        )
    
    async def delete_cached(self, key: str):
        """Delete cached data"""
        await self.client.delete(key)
    
    # Ticker validation cache
    async def get_ticker_cache(self, ticker: str) -> Optional[dict]:
        """Get cached ticker validation data"""
        key = f"ticker:{ticker.upper()}"
        return await self.get_cached(key)
    
    async def set_ticker_cache(self, ticker: str, data: dict, ttl: int = 3600):
        """Cache ticker validation data (1 hour TTL)"""
        key = f"ticker:{ticker.upper()}"
        await self.set_cached(key, data, ttl)
    
    # Session operations
    async def set_session(self, session_id: str, user_data: dict, ttl: int = 3600):
        """Store session data"""
        key = f"session:{session_id}"
        await self.set_cached(key, user_data, ttl)
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        key = f"session:{session_id}"
        return await self.get_cached(key)
    
    async def delete_session(self, session_id: str):
        """Delete session"""
        key = f"session:{session_id}"
        await self.delete_cached(key)


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """
    Dependency function to get Redis client.
    Usage in FastAPI:
        @app.get("/items")
        async def read_items(redis: RedisClient = Depends(get_redis)):
            ...
    """
    return redis_client

