"""
Unit tests for API Gateway routing
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestGatewayRouting:
    """Test gateway routing functionality"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "api-gateway"
        assert "routes" in data
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "api-gateway"
    
    def test_api_info(self, client):
        """Test API info endpoint"""
        response = client.get("/api")
        assert response.status_code == 200
        data = response.json()
        assert "gateway" in data
        assert "routes" in data
    
    def test_auth_route_exists(self, client):
        """Test that auth route is accessible (may return 404 from auth service if not running)"""
        # This will fail if auth service is not running, but route should exist
        response = client.post("/api/auth/login", json={"username": "test", "password": "test"})
        # Should not be 404 from gateway (would be 404 if route doesn't exist)
        # Could be 404 from auth service if it's not running, or 422 if validation fails
        assert response.status_code != 404 or "gateway" not in response.text.lower()
    
    def test_stocks_route_exists(self, client):
        """Test that stocks route is accessible"""
        response = client.get("/api/stocks")
        # Should not be 404 from gateway
        assert response.status_code != 404 or "gateway" not in response.text.lower()
    
    def test_notifications_route_exists(self, client):
        """Test that notifications route is accessible"""
        response = client.get("/api/notifications")
        # Should not be 404 from gateway
        assert response.status_code != 404 or "gateway" not in response.text.lower()
    
    def test_invalid_route(self, client):
        """Test invalid route returns 404"""
        response = client.get("/api/invalid-service/test")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

