"""
Integration tests for Stock Service endpoints
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, Mock
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from main import app


class TestStockEndpoints:
    """Integration tests for stock endpoints"""
    
    @pytest.fixture
    def admin_token(self):
        """Mock admin JWT token"""
        return "mock_admin_token"
    
    @pytest.fixture
    def user_token(self):
        """Mock user JWT token"""
        return "mock_user_token"
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "stock-service"
    
    @pytest.mark.asyncio
    async def test_validate_ticker_requires_auth(self):
        """Test validate ticker requires authentication"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/stocks/validate",
                json={"ticker": "AAPL"}
            )
            
            assert response.status_code == 403  # No auth header
    
    @pytest.mark.asyncio
    async def test_create_stock_requires_admin(self):
        """Test create stock requires admin role"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/stocks",
                json={
                    "ticker": "AAPL",
                    "company_name": "Apple Inc.",
                    "category": "ready",
                    "subcategory": "pullback1"
                }
            )
            
            assert response.status_code == 403  # No auth header
    
    @pytest.mark.asyncio
    async def test_get_all_stocks_requires_admin(self):
        """Test get all stocks requires admin role"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/stocks")
            
            assert response.status_code == 403  # No auth header
    
    @pytest.mark.asyncio
    async def test_update_stock_requires_admin(self):
        """Test update stock requires admin role"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.put(
                "/stocks/AAPL",
                json={"category": "near"}
            )
            
            assert response.status_code == 403  # No auth header
    
    @pytest.mark.asyncio
    async def test_delete_stock_requires_admin(self):
        """Test delete stock requires admin role"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.delete("/stocks/AAPL")
            
            assert response.status_code == 403  # No auth header
    
    @pytest.mark.asyncio
    async def test_search_stock_requires_auth(self):
        """Test search stock requires authentication"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/stocks/search/AAPL")
            
            assert response.status_code == 403  # No auth header
    
    @pytest.mark.asyncio
    async def test_get_rate_limit_requires_admin(self):
        """Test get rate limit requires admin role"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/admin/rate-limits/user-id-123")
            
            assert response.status_code == 403  # No auth header
    
    @pytest.mark.asyncio
    async def test_update_rate_limit_requires_admin(self):
        """Test update rate limit requires admin role"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.put(
                "/admin/rate-limits/user-id-123",
                json={"search_limit": 100}
            )
            
            assert response.status_code == 403  # No auth header
    
    @pytest.mark.asyncio
    async def test_reset_rate_limit_requires_admin(self):
        """Test reset rate limit requires admin role"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/admin/rate-limits/user-id-123/reset")
            
            assert response.status_code == 403  # No auth header
    
    @pytest.mark.asyncio
    async def test_reset_all_limits_requires_admin(self):
        """Test reset all limits requires admin role"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/admin/rate-limits/reset-all")
            
            assert response.status_code == 403  # No auth header
    
    @pytest.mark.asyncio
    async def test_set_universal_limit_requires_admin(self):
        """Test set universal limit requires admin role"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.put(
                "/admin/rate-limits/universal-limit",
                json={"search_limit": 50}
            )
            
            assert response.status_code == 403  # No auth header


class TestStockEndpointsWithAuth:
    """Integration tests with mocked authentication"""
    
    # Note: These would require more complex mocking of the auth middleware
    # For now, we're testing that auth is required
    # Full integration tests would be done in the comprehensive test script
    
    pass

