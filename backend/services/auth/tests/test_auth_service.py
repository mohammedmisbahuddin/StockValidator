"""
Unit tests for AuthService
"""
import pytest
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

from shared.auth_utils import hash_password, verify_password
from services.auth_service import AuthService
from schemas.user import UserCreate, UserLogin
from models.user import User, UserRole


class TestAuthService:
    """Test suite for AuthService"""
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, db_session, sample_user_data):
        """Test successful user registration"""
        user_create = UserCreate(**sample_user_data)
        user = await AuthService.register_user(db_session, user_create)
        
        assert user.id is not None
        assert user.email == sample_user_data["email"]
        assert user.username == sample_user_data["username"]
        assert user.password_hash != sample_user_data["password"]
        assert verify_password(sample_user_data["password"], user.password_hash)
        assert user.role == UserRole.USER
        assert user.search_limit == 50
        assert user.searches_used == 0
    
    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, db_session, sample_user_data):
        """Test registering with duplicate username"""
        user_create = UserCreate(**sample_user_data)
        await AuthService.register_user(db_session, user_create)
        
        # Try to register again with same username
        with pytest.raises(ValueError, match="Username already exists"):
            await AuthService.register_user(db_session, user_create)
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, db_session, sample_user_data):
        """Test registering with duplicate email"""
        user_create = UserCreate(**sample_user_data)
        await AuthService.register_user(db_session, user_create)
        
        # Try to register with different username but same email
        duplicate_data = sample_user_data.copy()
        duplicate_data["username"] = "different_user"
        user_create2 = UserCreate(**duplicate_data)
        
        with pytest.raises(ValueError, match="Email already exists"):
            await AuthService.register_user(db_session, user_create2)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, db_session, sample_user_data):
        """Test successful authentication"""
        # Register user first
        user_create = UserCreate(**sample_user_data)
        await AuthService.register_user(db_session, user_create)
        
        # Authenticate
        credentials = UserLogin(
            username=sample_user_data["username"],
            password=sample_user_data["password"]
        )
        user = await AuthService.authenticate_user(db_session, credentials)
        
        assert user is not None
        assert user.username == sample_user_data["username"]
        assert user.email == sample_user_data["email"]
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, db_session, sample_user_data):
        """Test authentication with wrong password"""
        # Register user first
        user_create = UserCreate(**sample_user_data)
        await AuthService.register_user(db_session, user_create)
        
        # Try to authenticate with wrong password
        credentials = UserLogin(
            username=sample_user_data["username"],
            password="WrongPassword123"
        )
        user = await AuthService.authenticate_user(db_session, credentials)
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_authenticate_nonexistent_user(self, db_session):
        """Test authentication with non-existent username"""
        credentials = UserLogin(
            username="nonexistent",
            password="SomePassword123"
        )
        user = await AuthService.authenticate_user(db_session, credentials)
        
        assert user is None
    
    @pytest.mark.asyncio
    async def test_create_tokens(self, db_session, sample_user_data):
        """Test token creation"""
        # Register and authenticate user
        user_create = UserCreate(**sample_user_data)
        user = await AuthService.register_user(db_session, user_create)
        
        # Create tokens
        token_response = await AuthService.create_tokens(db_session, user)
        
        assert token_response.access_token is not None
        assert token_response.refresh_token is not None
        assert token_response.token_type == "bearer"
        assert token_response.expires_in == 1800  # 30 minutes
    
    @pytest.mark.asyncio
    async def test_refresh_access_token_success(self, db_session, sample_user_data):
        """Test successful token refresh"""
        # Register user and create tokens
        user_create = UserCreate(**sample_user_data)
        user = await AuthService.register_user(db_session, user_create)
        token_response = await AuthService.create_tokens(db_session, user)
        
        # Refresh token
        new_access_token, refreshed_user = await AuthService.refresh_access_token(
            db_session,
            token_response.refresh_token
        )
        
        assert new_access_token is not None
        assert refreshed_user.id == user.id
        assert refreshed_user.username == user.username
    
    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token(self, db_session):
        """Test refresh with invalid token"""
        new_access_token, user = await AuthService.refresh_access_token(
            db_session,
            "invalid_refresh_token"
        )
        
        assert new_access_token is None
        assert user is None
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, db_session, sample_user_data):
        """Test getting user by ID"""
        # Register user
        user_create = UserCreate(**sample_user_data)
        user = await AuthService.register_user(db_session, user_create)
        
        # Get user by ID
        found_user = await AuthService.get_user_by_id(db_session, str(user.id))
        
        assert found_user is not None
        assert found_user.id == user.id
        assert found_user.username == user.username
    
    @pytest.mark.asyncio
    async def test_get_user_by_invalid_id(self, db_session):
        """Test getting user with invalid ID"""
        import uuid
        
        user = await AuthService.get_user_by_id(
            db_session,
            str(uuid.uuid4())  # Random UUID
        )
        
        assert user is None

