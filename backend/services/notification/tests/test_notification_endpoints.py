"""
Unit tests for Notification Service API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from main import app
from shared.auth_utils import create_access_token
from shared.models.user import UserRole


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
async def admin_token(sample_admin_user):
    """Create admin JWT token"""
    admin = await sample_admin_user
    return create_access_token(
        user_id=str(admin.id),
        username=admin.username,
        role=admin.role
    )


@pytest.fixture
async def user_token(sample_user):
    """Create user JWT token"""
    user = await sample_user
    return create_access_token(
        user_id=str(user.id),
        username=user.username,
        role=user.role
    )


class TestNotificationEndpoints:
    """Test notification API endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_notification_success(self, client, admin_token, sample_notification_data):
        admin_token_val = await admin_token
        """Test creating notification as admin"""
        response = client.post(
            "/notifications",
            json=sample_notification_data,
            headers={"Authorization": f"Bearer {admin_token_val}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_notification_data["title"]
        assert data["message"] == sample_notification_data["message"]
        assert "id" in data
    
    @pytest.mark.asyncio
    async def test_create_notification_unauthorized(self, client, sample_notification_data):
        """Test creating notification without auth"""
        response = client.post(
            "/notifications",
            json=sample_notification_data
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_create_notification_user_forbidden(self, client, user_token, sample_notification_data):
        """Test user cannot create notification"""
        user_token_val = await user_token
        response = client.post(
            "/notifications",
            json=sample_notification_data,
            headers={"Authorization": f"Bearer {user_token_val}"}
        )
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_get_all_notifications_admin(self, client, admin_token, db_session, sample_admin_user, sample_notification_data):
        """Test admin getting all notifications"""
        # Create a notification first
        from services.notification_service import NotificationService
        from schemas.notification import NotificationCreate
        
        service = NotificationService()
        notification_data = NotificationCreate(**sample_notification_data)
        await service.create_notification(db_session, notification_data, sample_admin_user.id)
        
        admin_token_val = await admin_token
        response = client.get(
            "/notifications",
            headers={"Authorization": f"Bearer {admin_token_val}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert "total" in data
        assert len(data["notifications"]) >= 1
    
    @pytest.mark.asyncio
    async def test_get_notification_by_id(self, client, admin_token, db_session, sample_admin_user, sample_notification_data):
        """Test getting notification by ID"""
        from services.notification_service import NotificationService
        from schemas.notification import NotificationCreate
        
        service = NotificationService()
        notification_data = NotificationCreate(**sample_notification_data)
        notification = await service.create_notification(db_session, notification_data, sample_admin_user.id)
        
        admin_token_val = await admin_token
        response = client.get(
            f"/notifications/{notification.id}",
            headers={"Authorization": f"Bearer {admin_token_val}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(notification.id)
        assert data["title"] == notification.title
    
    @pytest.mark.asyncio
    async def test_get_notification_not_found(self, client, admin_token):
        """Test getting non-existent notification"""
        admin_token_val = await admin_token
        fake_id = uuid4()
        response = client.get(
            f"/notifications/{fake_id}",
            headers={"Authorization": f"Bearer {admin_token_val}"}
        )
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_update_notification_success(self, client, admin_token, db_session, sample_admin_user, sample_notification_data):
        """Test updating notification"""
        from services.notification_service import NotificationService
        from schemas.notification import NotificationCreate
        
        service = NotificationService()
        notification_data = NotificationCreate(**sample_notification_data)
        notification = await service.create_notification(db_session, notification_data, sample_admin_user.id)
        
        update_data = {"title": "Updated Title", "message": "Updated message"}
        admin_token_val = await admin_token
        response = client.put(
            f"/notifications/{notification.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token_val}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["message"] == "Updated message"
    
    @pytest.mark.asyncio
    async def test_delete_notification_success(self, client, admin_token, db_session, sample_admin_user, sample_notification_data):
        """Test deleting notification"""
        from services.notification_service import NotificationService
        from schemas.notification import NotificationCreate
        
        service = NotificationService()
        notification_data = NotificationCreate(**sample_notification_data)
        notification = await service.create_notification(db_session, notification_data, sample_admin_user.id)
        
        admin_token_val = await admin_token
        response = client.delete(
            f"/notifications/{notification.id}",
            headers={"Authorization": f"Bearer {admin_token_val}"}
        )
        
        assert response.status_code == 204
    
    @pytest.mark.asyncio
    async def test_get_my_notifications_user(self, client, user_token, db_session, sample_admin_user, sample_user, sample_notification_data):
        """Test user getting their notifications"""
        from services.notification_service import NotificationService
        from schemas.notification import NotificationCreate
        
        service = NotificationService()
        notification_data = NotificationCreate(**sample_notification_data)
        await service.create_notification(db_session, notification_data, sample_admin_user.id)
        
        user_token_val = await user_token
        response = client.get(
            "/notifications/user/my-notifications",
            headers={"Authorization": f"Bearer {user_token_val}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "notifications" in data
        assert "unread_count" in data
        assert "total" in data
        assert len(data["notifications"]) >= 1
    
    @pytest.mark.asyncio
    async def test_get_unread_count(self, client, user_token, db_session, sample_admin_user, sample_user, sample_notification_data):
        """Test getting unread count"""
        from services.notification_service import NotificationService
        from schemas.notification import NotificationCreate
        
        service = NotificationService()
        notification_data = NotificationCreate(**sample_notification_data)
        await service.create_notification(db_session, notification_data, sample_admin_user.id)
        
        user_token_val = await user_token
        response = client.get(
            "/notifications/user/unread-count",
            headers={"Authorization": f"Bearer {user_token_val}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "unread_count" in data
        assert data["unread_count"] >= 1
    
    @pytest.mark.asyncio
    async def test_mark_as_read_success(self, client, user_token, db_session, sample_admin_user, sample_user, sample_notification_data):
        """Test marking notification as read"""
        from services.notification_service import NotificationService
        from schemas.notification import NotificationCreate
        
        service = NotificationService()
        notification_data = NotificationCreate(**sample_notification_data)
        notification = await service.create_notification(db_session, notification_data, sample_admin_user.id)
        
        user_token_val = await user_token
        response = client.put(
            f"/notifications/{notification.id}/read",
            headers={"Authorization": f"Bearer {user_token_val}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["notification_id"] == str(notification.id)
        
        # Verify unread count decreased
        unread_response = client.get(
            "/notifications/user/unread-count",
            headers={"Authorization": f"Bearer {user_token_val}"}
        )
        assert unread_response.json()["unread_count"] == 0
    
    @pytest.mark.asyncio
    async def test_mark_as_read_not_found(self, client, user_token):
        """Test marking non-existent notification as read"""
        user_token_val = await user_token
        fake_id = uuid4()
        response = client.put(
            f"/notifications/{fake_id}/read",
            headers={"Authorization": f"Bearer {user_token_val}"}
        )
        assert response.status_code == 404

