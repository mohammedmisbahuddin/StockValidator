"""
Unit tests for Notification Service business logic
"""
import pytest
from uuid import uuid4
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from services.notification_service import NotificationService
from schemas.notification import NotificationCreate, NotificationUpdate
from models.notification import Notification, UserNotification


class TestNotificationService:
    """Test notification service business logic"""
    
    @pytest.fixture
    def notification_service(self):
        """Create notification service instance"""
        return NotificationService()
    
    @pytest.mark.asyncio
    async def test_create_notification_success(
        self, notification_service, db_session, sample_admin_user, sample_user, sample_notification_data
    ):
        """Test successful notification creation"""
        notification_data = NotificationCreate(**sample_notification_data)
        
        notification = await notification_service.create_notification(
            db=db_session,
            notification_data=notification_data,
            created_by=sample_admin_user.id
        )
        
        assert notification.title == sample_notification_data["title"]
        assert notification.message == sample_notification_data["message"]
        assert notification.created_by == sample_admin_user.id
        
        # Check that user_notification entries were created for all users
        from sqlalchemy import select
        result = await db_session.execute(
            select(UserNotification).where(UserNotification.notification_id == notification.id)
        )
        user_notifications = result.scalars().all()
        assert len(user_notifications) == 2  # admin + user
        
        # All should be unread
        for un in user_notifications:
            assert un.is_read == False
    
    @pytest.mark.asyncio
    async def test_get_notification_success(
        self, notification_service, db_session, sample_admin_user, sample_notification_data
    ):
        """Test getting notification by ID"""
        notification_data = NotificationCreate(**sample_notification_data)
        notification = await notification_service.create_notification(
            db=db_session,
            notification_data=notification_data,
            created_by=sample_admin_user.id
        )
        
        retrieved = await notification_service.get_notification(db_session, notification.id)
        
        assert retrieved is not None
        assert retrieved.id == notification.id
        assert retrieved.title == notification.title
    
    @pytest.mark.asyncio
    async def test_get_notification_not_found(self, notification_service, db_session):
        """Test getting non-existent notification"""
        fake_id = uuid4()
        notification = await notification_service.get_notification(db_session, fake_id)
        assert notification is None
    
    @pytest.mark.asyncio
    async def test_get_all_notifications(
        self, notification_service, db_session, sample_admin_user, sample_notification_data
    ):
        """Test getting all notifications"""
        # Create multiple notifications
        for i in range(3):
            notification_data = NotificationCreate(
                title=f"{sample_notification_data['title']} {i}",
                message=f"{sample_notification_data['message']} {i}"
            )
            await notification_service.create_notification(
                db=db_session,
                notification_data=notification_data,
                created_by=sample_admin_user.id
            )
        
        notifications = await notification_service.get_all_notifications(db_session)
        
        assert len(notifications) == 3
        # Should be sorted by created_at desc (newest first)
        assert notifications[0].title.endswith("2")
    
    @pytest.mark.asyncio
    async def test_update_notification_success(
        self, notification_service, db_session, sample_admin_user, sample_notification_data
    ):
        """Test updating notification"""
        notification_data = NotificationCreate(**sample_notification_data)
        notification = await notification_service.create_notification(
            db=db_session,
            notification_data=notification_data,
            created_by=sample_admin_user.id
        )
        
        update_data = NotificationUpdate(title="Updated Title", message="Updated message")
        updated = await notification_service.update_notification(
            db=db_session,
            notification_id=notification.id,
            notification_data=update_data
        )
        
        assert updated is not None
        assert updated.title == "Updated Title"
        assert updated.message == "Updated message"
    
    @pytest.mark.asyncio
    async def test_update_notification_partial(
        self, notification_service, db_session, sample_admin_user, sample_notification_data
    ):
        """Test partial update (only title)"""
        notification_data = NotificationCreate(**sample_notification_data)
        notification = await notification_service.create_notification(
            db=db_session,
            notification_data=notification_data,
            created_by=sample_admin_user.id
        )
        
        original_message = notification.message
        update_data = NotificationUpdate(title="Updated Title Only")
        updated = await notification_service.update_notification(
            db=db_session,
            notification_id=notification.id,
            notification_data=update_data
        )
        
        assert updated.title == "Updated Title Only"
        assert updated.message == original_message  # Unchanged
    
    @pytest.mark.asyncio
    async def test_delete_notification_success(
        self, notification_service, db_session, sample_admin_user, sample_notification_data
    ):
        """Test deleting notification"""
        notification_data = NotificationCreate(**sample_notification_data)
        notification = await notification_service.create_notification(
            db=db_session,
            notification_data=notification_data,
            created_by=sample_admin_user.id
        )
        
        deleted = await notification_service.delete_notification(db_session, notification.id)
        
        assert deleted == True
        
        # Verify it's gone
        retrieved = await notification_service.get_notification(db_session, notification.id)
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_delete_notification_not_found(self, notification_service, db_session):
        """Test deleting non-existent notification"""
        fake_id = uuid4()
        deleted = await notification_service.delete_notification(db_session, fake_id)
        assert deleted == False
    
    @pytest.mark.asyncio
    async def test_get_user_notifications(
        self, notification_service, db_session, sample_admin_user, sample_user, sample_notification_data
    ):
        """Test getting user notifications"""
        # Create notification
        notification_data = NotificationCreate(**sample_notification_data)
        await notification_service.create_notification(
            db=db_session,
            notification_data=notification_data,
            created_by=sample_admin_user.id
        )
        
        user_notifications = await notification_service.get_user_notifications(
            db=db_session,
            user_id=sample_user.id
        )
        
        assert len(user_notifications) == 1
        assert user_notifications[0].user_id == sample_user.id
        assert user_notifications[0].is_read == False
    
    @pytest.mark.asyncio
    async def test_get_unread_count(
        self, notification_service, db_session, sample_admin_user, sample_user, sample_notification_data
    ):
        """Test getting unread count"""
        # Create 3 notifications
        for i in range(3):
            notification_data = NotificationCreate(
                title=f"Notification {i}",
                message=f"Message {i}"
            )
            await notification_service.create_notification(
                db=db_session,
                notification_data=notification_data,
                created_by=sample_admin_user.id
            )
        
        unread_count = await notification_service.get_unread_count(
            db=db_session,
            user_id=sample_user.id
        )
        
        assert unread_count == 3
    
    @pytest.mark.asyncio
    async def test_mark_as_read_success(
        self, notification_service, db_session, sample_admin_user, sample_user, sample_notification_data
    ):
        """Test marking notification as read"""
        notification_data = NotificationCreate(**sample_notification_data)
        notification = await notification_service.create_notification(
            db=db_session,
            notification_data=notification_data,
            created_by=sample_admin_user.id
        )
        
        user_notification = await notification_service.mark_as_read(
            db=db_session,
            notification_id=notification.id,
            user_id=sample_user.id
        )
        
        assert user_notification is not None
        assert user_notification.is_read == True
        assert user_notification.read_at is not None
        
        # Verify unread count decreased
        unread_count = await notification_service.get_unread_count(
            db=db_session,
            user_id=sample_user.id
        )
        assert unread_count == 0
    
    @pytest.mark.asyncio
    async def test_mark_as_read_not_found(
        self, notification_service, db_session, sample_user
    ):
        """Test marking non-existent notification as read"""
        fake_id = uuid4()
        result = await notification_service.mark_as_read(
            db=db_session,
            notification_id=fake_id,
            user_id=sample_user.id
        )
        assert result is None

