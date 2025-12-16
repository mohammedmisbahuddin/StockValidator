"""
Notification service business logic
"""
import sys
from pathlib import Path
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
import logging

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from models.notification import Notification, UserNotification
from schemas.notification import NotificationCreate, NotificationUpdate

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for notification management operations"""
    
    async def create_notification(
        self,
        db: AsyncSession,
        notification_data: NotificationCreate,
        created_by: UUID
    ) -> Notification:
        """
        Create a new notification
        
        When a notification is created, entries are automatically created
        in user_notifications for ALL users (is_read = False)
        
        Args:
            db: Database session
            notification_data: Notification creation data
            created_by: UUID of user creating the notification
        
        Returns:
            Created notification
        """
        # Create notification
        notification = Notification(
            title=notification_data.title,
            message=notification_data.message,
            created_by=created_by
        )
        
        db.add(notification)
        await db.flush()  # Flush to get the notification ID
        
        # Get all users to create user_notification entries
        from shared.models.user import User
        users_result = await db.execute(select(User.id))
        user_ids = [row[0] for row in users_result.fetchall()]
        
        # Create user_notification entries for all users
        user_notifications = [
            UserNotification(
                notification_id=notification.id,
                user_id=user_id,
                is_read=False
            )
            for user_id in user_ids
        ]
        
        db.add_all(user_notifications)
        await db.commit()
        await db.refresh(notification)
        
        logger.info(f"Created notification {notification.id} by user {created_by} for {len(user_ids)} users")
        return notification
    
    async def get_notification(
        self,
        db: AsyncSession,
        notification_id: UUID
    ) -> Optional[Notification]:
        """
        Get a notification by ID
        
        Args:
            db: Database session
            notification_id: Notification UUID
        
        Returns:
            Notification if found, None otherwise
        """
        result = await db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_notifications(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Notification]:
        """
        Get all notifications (admin view)
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of notifications
        """
        result = await db.execute(
            select(Notification)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def update_notification(
        self,
        db: AsyncSession,
        notification_id: UUID,
        notification_data: NotificationUpdate
    ) -> Optional[Notification]:
        """
        Update a notification
        
        Args:
            db: Database session
            notification_id: Notification UUID
            notification_data: Update data
        
        Returns:
            Updated notification if found, None otherwise
        """
        notification = await self.get_notification(db, notification_id)
        if not notification:
            return None
        
        # Update fields
        if notification_data.title is not None:
            notification.title = notification_data.title
        if notification_data.message is not None:
            notification.message = notification_data.message
        
        await db.commit()
        await db.refresh(notification)
        
        logger.info(f"Updated notification {notification_id}")
        return notification
    
    async def delete_notification(
        self,
        db: AsyncSession,
        notification_id: UUID
    ) -> bool:
        """
        Delete a notification
        
        Args:
            db: Database session
            notification_id: Notification UUID
        
        Returns:
            True if deleted, False if not found
        """
        notification = await self.get_notification(db, notification_id)
        if not notification:
            return False
        
        await db.delete(notification)
        await db.commit()
        
        logger.info(f"Deleted notification {notification_id}")
        return True
    
    async def get_user_notifications(
        self,
        db: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserNotification]:
        """
        Get all notifications for a specific user with read status
        
        Args:
            db: Database session
            user_id: User UUID
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of user notifications
        """
        result = await db.execute(
            select(UserNotification)
            .where(UserNotification.user_id == user_id)
            .options(selectinload(UserNotification.notification))
            .order_by(UserNotification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_unread_count(
        self,
        db: AsyncSession,
        user_id: UUID
    ) -> int:
        """
        Get count of unread notifications for a user
        
        Args:
            db: Database session
            user_id: User UUID
        
        Returns:
            Number of unread notifications
        """
        result = await db.execute(
            select(func.count(UserNotification.id))
            .where(
                and_(
                    UserNotification.user_id == user_id,
                    UserNotification.is_read == False
                )
            )
        )
        return result.scalar() or 0
    
    async def mark_as_read(
        self,
        db: AsyncSession,
        notification_id: UUID,
        user_id: UUID
    ) -> Optional[UserNotification]:
        """
        Mark a notification as read for a user
        
        Args:
            db: Database session
            notification_id: Notification UUID
            user_id: User UUID
        
        Returns:
            UserNotification if found and updated, None otherwise
        """
        result = await db.execute(
            select(UserNotification).where(
                and_(
                    UserNotification.notification_id == notification_id,
                    UserNotification.user_id == user_id
                )
            )
        )
        user_notification = result.scalar_one_or_none()
        
        if not user_notification:
            return None
        
        user_notification.mark_as_read()
        await db.commit()
        await db.refresh(user_notification)
        
        logger.info(f"Marked notification {notification_id} as read for user {user_id}")
        return user_notification

