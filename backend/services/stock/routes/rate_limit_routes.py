"""
Admin routes for rate limit management
"""
import sys
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

# Add paths
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from shared.database import get_db
from shared.models.user import User
from schemas.stock import (
    RateLimitInfo,
    RateLimitUpdate,
    UniversalRateLimitUpdate,
    RateLimitResetResponse,
)
from services.rate_limiter import RateLimitService

# Import auth middleware from shared
from shared.middleware.auth_middleware import require_admin

# Initialize service
rate_limiter = RateLimitService()

router = APIRouter(prefix="/admin/rate-limits", tags=["Admin - Rate Limits"])


@router.get("/{user_id}", response_model=RateLimitInfo)
async def get_user_rate_limit(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get a user's rate limit information (Admin only)
    """
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Get rate limit info from Redis
    max_limit = await rate_limiter.get_max_limit(user.id)
    remaining = await rate_limiter.get_remaining_searches(user.id)
    
    return RateLimitInfo(
        user_id=user.id,
        username=user.username,
        search_limit=max_limit,
        searches_used=max_limit - remaining,
        remaining_searches=remaining,
        last_reset_at=user.last_reset_at
    )


@router.put("/{user_id}", response_model=RateLimitInfo)
async def update_user_rate_limit(
    user_id: str,
    limit_data: RateLimitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update a user's search limit (Admin only)
    
    This will:
    - Set the user's maximum search limit
    - Reset their current searches to the new limit
    """
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Update limit in Redis
    await rate_limiter.update_user_limit(user.id, limit_data.search_limit)
    
    # Update user's search_limit in database
    user.search_limit = limit_data.search_limit
    user.searches_used = 0
    await db.commit()
    await db.refresh(user)
    
    # Get updated info
    max_limit = await rate_limiter.get_max_limit(user.id)
    remaining = await rate_limiter.get_remaining_searches(user.id)
    
    return RateLimitInfo(
        user_id=user.id,
        username=user.username,
        search_limit=max_limit,
        searches_used=0,
        remaining_searches=remaining,
        last_reset_at=user.last_reset_at
    )


@router.post("/{user_id}/reset", response_model=RateLimitResetResponse)
async def reset_user_rate_limit(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Reset a specific user's search limit to their maximum (Admin only)
    """
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Reset limit in Redis
    success = await rate_limiter.reset_user_limit(user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset rate limit"
        )
    
    # Update user's searches_used in database
    user.searches_used = 0
    await db.commit()
    
    return RateLimitResetResponse(
        success=True,
        message=f"Rate limit reset successfully for user {user.username}",
        affected_users=1
    )


@router.post("/reset-all", response_model=RateLimitResetResponse)
async def reset_all_rate_limits(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Reset all users' search limits to their maximum (Admin only)
    """
    # Get all users
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    user_ids = [user.id for user in users]
    
    # Reset all limits in Redis
    count = await rate_limiter.reset_all_limits(user_ids)
    
    # Update all users' searches_used in database
    for user in users:
        user.searches_used = 0
    
    await db.commit()
    
    return RateLimitResetResponse(
        success=True,
        message=f"Successfully reset rate limits for {count} users",
        affected_users=count
    )


@router.put("/universal-limit", response_model=RateLimitResetResponse)
async def set_universal_rate_limit(
    limit_data: UniversalRateLimitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Set universal search limit for all users (Admin only)
    
    This will:
    - Update all users' maximum search limits
    - Reset all users' current searches to the new limit
    """
    # Get all users
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    user_ids = [user.id for user in users]
    
    # Set universal limit in Redis
    count = await rate_limiter.set_universal_limit(user_ids, limit_data.search_limit)
    
    # Update all users in database
    for user in users:
        user.search_limit = limit_data.search_limit
        user.searches_used = 0
    
    await db.commit()
    
    return RateLimitResetResponse(
        success=True,
        message=f"Successfully set universal limit of {limit_data.search_limit} for {count} users",
        affected_users=count
    )

