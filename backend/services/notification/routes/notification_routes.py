"""
Notification routes for admin and user operations
"""
import sys
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

# Add paths
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from shared.database import get_db
from shared.models.user import User
from schemas.notification import (
    NotificationCreate,
    NotificationUpdate,
    NotificationResponse,
    NotificationListResponse,
    UserNotificationResponse,
    UserNotificationListResponse,
    UnreadCountResponse,
    MarkAsReadResponse
)
from services.notification_service import NotificationService

# Import auth middleware from shared
from shared.middleware.auth_middleware import get_current_user, require_admin

# Initialize service
notification_service = NotificationService()

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# ===== Admin Endpoints =====

@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification_data: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new notification (Admin only)
    
    When a notification is created, it's automatically sent to all users
    with is_read = False
    """
    notification = await notification_service.create_notification(
        db=db,
        notification_data=notification_data,
        created_by=current_user.id
    )
    return NotificationResponse.model_validate(notification)


@router.get("", response_model=NotificationListResponse)
async def get_all_notifications(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get all notifications (Admin only)
    
    Returns all notifications sorted by creation date (newest first)
    """
    notifications = await notification_service.get_all_notifications(db, skip=skip, limit=limit)
    
    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n) for n in notifications],
        total=len(notifications)
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get a specific notification by ID (Admin only)
    """
    notification = await notification_service.get_notification(db, notification_id)
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with id {notification_id} not found"
        )
    
    return NotificationResponse.model_validate(notification)


@router.put("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    notification_id: UUID,
    notification_data: NotificationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update a notification (Admin only)
    """
    notification = await notification_service.update_notification(
        db=db,
        notification_id=notification_id,
        notification_data=notification_data
    )
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with id {notification_id} not found"
        )
    
    return NotificationResponse.model_validate(notification)


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete a notification (Admin only)
    
    This will also delete all associated user_notification records
    """
    deleted = await notification_service.delete_notification(db, notification_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with id {notification_id} not found"
        )
    
    return None


# ===== User Endpoints =====

@router.get("/user/my-notifications", response_model=UserNotificationListResponse)
async def get_my_notifications(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get my notifications (User)
    
    Returns all notifications for the current user with read/unread status
    """
    user_notifications = await notification_service.get_user_notifications(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    # Get unread count
    unread_count = await notification_service.get_unread_count(db, current_user.id)
    
    # Transform to response format
    notifications = []
    for un in user_notifications:
        notif = un.notification
        notifications.append(UserNotificationResponse(
            id=un.id,
            notification_id=notif.id,
            title=notif.title,
            message=notif.message,
            is_read=un.is_read,
            read_at=un.read_at,
            created_at=notif.created_at
        ))
    
    return UserNotificationListResponse(
        notifications=notifications,
        unread_count=unread_count,
        total=len(notifications)
    )


@router.get("/user/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get count of unread notifications (User)
    """
    unread_count = await notification_service.get_unread_count(db, current_user.id)
    
    return UnreadCountResponse(unread_count=unread_count)


@router.put("/{notification_id}/read", response_model=MarkAsReadResponse)
async def mark_notification_as_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a notification as read (User)
    """
    user_notification = await notification_service.mark_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id
    )
    
    if not user_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with id {notification_id} not found for user"
        )
    
    return MarkAsReadResponse(
        success=True,
        message="Notification marked as read",
        notification_id=notification_id
    )

