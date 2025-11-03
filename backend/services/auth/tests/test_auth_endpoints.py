"""
Integration tests for Auth API endpoints
"""
import pytest
from httpx import AsyncClient
from fastapi import status
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

from main import app


class TestAuthEndpoints:
    """Test suite for Auth API endpoints"""
    
    @pytest.mark.asyncio
    async def test_register_user_success(self):
        """Test successful user registration via API"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/auth/register",
                json={
                    "email": "newuser@test.com",
                    "username": "newuser",
                    "password": "NewPass123",
                    "role": "user"
                }
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["email"] == "newuser@test.com"
            assert data["username"] == "newuser"
            assert "password" not in data
            assert data["role"] == "user"
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self):
        """Test registration with invalid email"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/auth/register",
                json={
                    "email": "invalid-email",
                    "username": "testuser",
                    "password": "TestPass123",
                    "role": "user"
                }
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_register_short_password(self):
        """Test registration with too short password"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/auth/register",
                json={
                    "email": "user@test.com",
                    "username": "testuser",
                    "password": "short",  # Less than 8 characters
                    "role": "user"
                }
            )
            
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_login_success(self):
        """Test successful login"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Register user first
            await client.post(
                "/auth/register",
                json={
                    "email": "logintest@test.com",
                    "username": "logintest",
                    "password": "LoginPass123",
                    "role": "user"
                }
            )
            
            # Login
            response = await client.post(
                "/auth/login",
                json={
                    "username": "logintest",
                    "password": "LoginPass123"
                }
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"
            assert data["expires_in"] == 1800
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self):
        """Test login with wrong password"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Register user first
            await client.post(
                "/auth/register",
                json={
                    "email": "wrongpass@test.com",
                    "username": "wrongpass",
                    "password": "CorrectPass123",
                    "role": "user"
                }
            )
            
            # Try to login with wrong password
            response = await client.post(
                "/auth/login",
                json={
                    "username": "wrongpass",
                    "password": "WrongPassword"
                }
            )
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Incorrect username or password" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_get_current_user(self):
        """Test getting current user with valid token"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Register and login
            await client.post(
                "/auth/register",
                json={
                    "email": "currentuser@test.com",
                    "username": "currentuser",
                    "password": "CurrentPass123",
                    "role": "user"
                }
            )
            
            login_response = await client.post(
                "/auth/login",
                json={
                    "username": "currentuser",
                    "password": "CurrentPass123"
                }
            )
            token = login_response.json()["access_token"]
            
            # Get current user
            response = await client.get(
                "/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["username"] == "currentuser"
            assert data["email"] == "currentuser@test.com"
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/auth/me",
                headers={"Authorization": "Bearer invalid_token"}
            )
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self):
        """Test getting current user without token"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/auth/me")
            
            assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self):
        """Test successful token refresh"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Register and login
            await client.post(
                "/auth/register",
                json={
                    "email": "refresh@test.com",
                    "username": "refresh",
                    "password": "RefreshPass123",
                    "role": "user"
                }
            )
            
            login_response = await client.post(
                "/auth/login",
                json={
                    "username": "refresh",
                    "password": "RefreshPass123"
                }
            )
            refresh_token = login_response.json()["refresh_token"]
            
            # Refresh token
            response = await client.post(
                "/auth/refresh",
                json={"refresh_token": refresh_token}
            )
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self):
        """Test token refresh with invalid token"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/auth/refresh",
                json={"refresh_token": "invalid_token"}
            )
            
            assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestHealthCheck:
    """Test health check endpoint"""
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "healthy"
            assert data["service"] == "auth"

