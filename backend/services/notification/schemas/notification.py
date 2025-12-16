"""
Pydantic schemas for Notification service
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


# ===== Request Schemas =====

class NotificationCreate(BaseModel):
    """Schema for creating a notification"""
    title: str = Field(..., min_length=1, max_length=255, description="Notification title")
    message: str = Field(..., min_length=1, description="Notification message/content")


class NotificationUpdate(BaseModel):
    """Schema for updating a notification"""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Notification title")
    message: Optional[str] = Field(None, min_length=1, description="Notification message/content")


# ===== Response Schemas =====

class NotificationResponse(BaseModel):
    """Schema for notification response (admin view)"""
    id: UUID
    title: str
    message: str
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """Schema for list of notifications"""
    notifications: List[NotificationResponse] = Field(default_factory=list)
    total: int = Field(..., description="Total number of notifications")


class UserNotificationResponse(BaseModel):
    """Schema for user notification response (includes read status)"""
    id: UUID
    title: str
    message: str
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    notification_id: UUID
    
    model_config = {"from_attributes": True}


class UserNotificationListResponse(BaseModel):
    """Schema for user's notification list"""
    notifications: List[UserNotificationResponse] = Field(default_factory=list)
    unread_count: int = Field(..., description="Number of unread notifications")
    total: int = Field(..., description="Total number of notifications")


class UnreadCountResponse(BaseModel):
    """Schema for unread count response"""
    unread_count: int = Field(..., description="Number of unread notifications")


class MarkAsReadResponse(BaseModel):
    """Schema for mark as read response"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    notification_id: UUID = Field(..., description="ID of the notification that was marked as read")

