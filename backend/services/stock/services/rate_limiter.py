"""
Rate limiting service using Redis
"""
import sys
from pathlib import Path
from typing import Optional
from uuid import UUID
import logging

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from shared.redis_client import redis_client

logger = logging.getLogger(__name__)


class RateLimitService:
    """
    Service to manage user search rate limits using Redis
    
    Redis keys:
    - user_limit:{user_id} = remaining searches
    - user_limit_max:{user_id} = maximum search limit
    """
    
    def __init__(self):
        self.redis = redis_client
    
    async def initialize_user_limit(self, user_id: UUID, limit: int) -> None:
        """
        Initialize a user's search limit
        
        Args:
            user_id: User UUID
            limit: Maximum search limit
        """
        user_id_str = str(user_id)
        await self.redis.client.set(f"user_limit:{user_id_str}", limit)
        await self.redis.client.set(f"user_limit_max:{user_id_str}", limit)
        logger.info(f"Initialized rate limit for user {user_id}: {limit}")
    
    async def get_remaining_searches(self, user_id: UUID) -> int:
        """
        Get user's remaining searches
        
        Args:
            user_id: User UUID
        
        Returns:
            Number of remaining searches (0 if limit reached or not initialized)
        """
        user_id_str = str(user_id)
        remaining = await self.redis.client.get(f"user_limit:{user_id_str}")
        
        if remaining is None:
            return 0
        
        return int(remaining)
    
    async def get_max_limit(self, user_id: UUID) -> int:
        """
        Get user's maximum search limit
        
        Args:
            user_id: User UUID
        
        Returns:
            Maximum search limit (0 if not initialized)
        """
        user_id_str = str(user_id)
        max_limit = await self.redis.client.get(f"user_limit_max:{user_id_str}")
        
        if max_limit is None:
            return 0
        
        return int(max_limit)
    
    async def decrement_search(self, user_id: UUID) -> tuple[bool, int]:
        """
        Decrement user's search count
        
        Args:
            user_id: User UUID
        
        Returns:
            Tuple of (success, remaining_searches)
            - success: False if limit reached or not initialized
            - remaining_searches: Number of remaining searches after decrement
        """
        user_id_str = str(user_id)
        remaining = await self.get_remaining_searches(user_id)
        
        if remaining <= 0:
            logger.warning(f"Rate limit exceeded for user {user_id}")
            return False, 0
        
        # Decrement
        new_remaining = await self.redis.client.decr(f"user_limit:{user_id_str}")
        logger.info(f"Decremented search for user {user_id}: {new_remaining} remaining")
        
        return True, max(0, new_remaining)
    
    async def reset_user_limit(self, user_id: UUID) -> bool:
        """
        Reset user's search limit to maximum
        
        Args:
            user_id: User UUID
        
        Returns:
            True if successful, False if user not found
        """
        user_id_str = str(user_id)
        max_limit = await self.get_max_limit(user_id)
        
        if max_limit == 0:
            logger.warning(f"Cannot reset limit for user {user_id}: not initialized")
            return False
        
        await self.redis.client.set(f"user_limit:{user_id_str}", max_limit)
        logger.info(f"Reset rate limit for user {user_id} to {max_limit}")
        
        return True
    
    async def update_user_limit(self, user_id: UUID, new_limit: int) -> None:
        """
        Update user's maximum search limit
        
        Args:
            user_id: User UUID
            new_limit: New maximum search limit
        """
        user_id_str = str(user_id)
        await self.redis.client.set(f"user_limit:{user_id_str}", new_limit)
        await self.redis.client.set(f"user_limit_max:{user_id_str}", new_limit)
        logger.info(f"Updated rate limit for user {user_id} to {new_limit}")
    
    async def reset_all_limits(self, user_ids: list[UUID]) -> int:
        """
        Reset all users' search limits to their maximum
        
        Args:
            user_ids: List of user UUIDs
        
        Returns:
            Number of users reset successfully
        """
        count = 0
        for user_id in user_ids:
            if await self.reset_user_limit(user_id):
                count += 1
        
        logger.info(f"Reset rate limits for {count} users")
        return count
    
    async def set_universal_limit(self, user_ids: list[UUID], limit: int) -> int:
        """
        Set universal search limit for all users
        
        Args:
            user_ids: List of user UUIDs
            limit: New universal limit
        
        Returns:
            Number of users updated successfully
        """
        count = 0
        for user_id in user_ids:
            await self.update_user_limit(user_id, limit)
            count += 1
        
        logger.info(f"Set universal rate limit of {limit} for {count} users")
        return count

