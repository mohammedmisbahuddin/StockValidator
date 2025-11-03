"""
Authentication service - Business logic for user authentication
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional, Tuple
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

from shared.auth_utils import hash_password, verify_password, create_access_token, create_refresh_token
from shared.config import settings
from shared.models.user import User, RefreshToken, UserRole
from schemas.user import UserCreate, UserLogin, TokenResponse


class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserCreate) -> User:
        """
        Register a new user
        
        Args:
            db: Database session
            user_data: User registration data
            
        Returns:
            Created user
            
        Raises:
            ValueError: If username or email already exists
        """
        # Check if username exists
        result = await db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise ValueError("Username already exists")
        
        # Check if email exists
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        if result.scalar_one_or_none():
            raise ValueError("Email already exists")
        
        # Create new user
        user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=hash_password(user_data.password),
            role=user_data.role,
            search_limit=50,  # Default limit
            searches_used=0
        )
        
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        return user
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, credentials: UserLogin) -> Optional[User]:
        """
        Authenticate user with username and password
        
        Args:
            db: Database session
            credentials: Login credentials
            
        Returns:
            User if authentication successful, None otherwise
        """
        result = await db.execute(
            select(User).where(User.username == credentials.username)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not verify_password(credentials.password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    async def create_tokens(db: AsyncSession, user: User) -> TokenResponse:
        """
        Create access and refresh tokens for user
        
        Args:
            db: Database session
            user: User to create tokens for
            
        Returns:
            Token response with access and refresh tokens
        """
        # Create access token
        access_token = create_access_token({
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value
        })
        
        # Create refresh token
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        # Store refresh token in database
        refresh_token_obj = RefreshToken(
            token=refresh_token,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(refresh_token_obj)
        await db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    @staticmethod
    async def refresh_access_token(db: AsyncSession, refresh_token: str) -> Tuple[Optional[str], Optional[User]]:
        """
        Refresh access token using refresh token
        
        Args:
            db: Database session
            refresh_token: Refresh token
            
        Returns:
            Tuple of (new_access_token, user) or (None, None) if invalid
        """
        # Find refresh token in database
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token == refresh_token)
        )
        token_obj = result.scalar_one_or_none()
        
        if not token_obj:
            return None, None
        
        # Check if token is expired
        if token_obj.expires_at < datetime.utcnow():
            # Delete expired token
            await db.delete(token_obj)
            await db.commit()
            return None, None
        
        # Get user
        result = await db.execute(
            select(User).where(User.id == token_obj.user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None, None
        
        # Create new access token
        access_token = create_access_token({
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value
        })
        
        return access_token, user
    
    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """
        Get user by ID
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User or None
        """
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

