"""
Unit tests for Rate Limiter Service
"""
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from services.rate_limiter import RateLimitService


class TestRateLimiterService:
    """Test Redis-based rate limiting"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Create rate limiter instance"""
        return RateLimitService()
    
    @pytest.fixture
    def user_id(self):
        """Generate test user ID"""
        return uuid4()
    
    @pytest.mark.asyncio
    async def test_initialize_user_limit(self, rate_limiter, user_id):
        """Test initializing a user's search limit"""
        with patch.object(rate_limiter.redis, 'set', new_callable=AsyncMock) as mock_set:
            await rate_limiter.initialize_user_limit(user_id, 50)
            
            # Should set both current and max limit
            assert mock_set.call_count == 2
            mock_set.assert_any_call(f"user_limit:{user_id}", 50)
            mock_set.assert_any_call(f"user_limit_max:{user_id}", 50)
    
    @pytest.mark.asyncio
    async def test_get_remaining_searches(self, rate_limiter, user_id):
        """Test getting remaining searches"""
        with patch.object(rate_limiter.redis, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = "25"
            
            remaining = await rate_limiter.get_remaining_searches(user_id)
            
            assert remaining == 25
            mock_get.assert_called_once_with(f"user_limit:{user_id}")
    
    @pytest.mark.asyncio
    async def test_get_remaining_searches_not_initialized(self, rate_limiter, user_id):
        """Test getting remaining searches when not initialized"""
        with patch.object(rate_limiter.redis, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            
            remaining = await rate_limiter.get_remaining_searches(user_id)
            
            assert remaining == 0
    
    @pytest.mark.asyncio
    async def test_decrement_search_success(self, rate_limiter, user_id):
        """Test successful search decrement"""
        with patch.object(rate_limiter, 'get_remaining_searches', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = 10
            
            with patch.object(rate_limiter.redis, 'decr', new_callable=AsyncMock) as mock_decr:
                mock_decr.return_value = 9
                
                success, remaining = await rate_limiter.decrement_search(user_id)
                
                assert success is True
                assert remaining == 9
                mock_decr.assert_called_once_with(f"user_limit:{user_id}")
    
    @pytest.mark.asyncio
    async def test_decrement_search_limit_exceeded(self, rate_limiter, user_id):
        """Test decrement when limit is exceeded"""
        with patch.object(rate_limiter, 'get_remaining_searches', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = 0
            
            success, remaining = await rate_limiter.decrement_search(user_id)
            
            assert success is False
            assert remaining == 0
    
    @pytest.mark.asyncio
    async def test_reset_user_limit(self, rate_limiter, user_id):
        """Test resetting a user's limit"""
        with patch.object(rate_limiter, 'get_max_limit', new_callable=AsyncMock) as mock_max:
            mock_max.return_value = 50
            
            with patch.object(rate_limiter.redis, 'set', new_callable=AsyncMock) as mock_set:
                success = await rate_limiter.reset_user_limit(user_id)
                
                assert success is True
                mock_set.assert_called_once_with(f"user_limit:{user_id}", 50)
    
    @pytest.mark.asyncio
    async def test_reset_user_limit_not_initialized(self, rate_limiter, user_id):
        """Test reset when user not initialized"""
        with patch.object(rate_limiter, 'get_max_limit', new_callable=AsyncMock) as mock_max:
            mock_max.return_value = 0
            
            success = await rate_limiter.reset_user_limit(user_id)
            
            assert success is False
    
    @pytest.mark.asyncio
    async def test_update_user_limit(self, rate_limiter, user_id):
        """Test updating a user's limit"""
        with patch.object(rate_limiter.redis, 'set', new_callable=AsyncMock) as mock_set:
            await rate_limiter.update_user_limit(user_id, 100)
            
            assert mock_set.call_count == 2
            mock_set.assert_any_call(f"user_limit:{user_id}", 100)
            mock_set.assert_any_call(f"user_limit_max:{user_id}", 100)
    
    @pytest.mark.asyncio
    async def test_reset_all_limits(self, rate_limiter):
        """Test resetting all users' limits"""
        user_ids = [uuid4() for _ in range(3)]
        
        with patch.object(rate_limiter, 'reset_user_limit', new_callable=AsyncMock) as mock_reset:
            mock_reset.return_value = True
            
            count = await rate_limiter.reset_all_limits(user_ids)
            
            assert count == 3
            assert mock_reset.call_count == 3
    
    @pytest.mark.asyncio
    async def test_set_universal_limit(self, rate_limiter):
        """Test setting universal limit for all users"""
        user_ids = [uuid4() for _ in range(3)]
        
        with patch.object(rate_limiter, 'update_user_limit', new_callable=AsyncMock):
            count = await rate_limiter.set_universal_limit(user_ids, 75)
            
            assert count == 3

