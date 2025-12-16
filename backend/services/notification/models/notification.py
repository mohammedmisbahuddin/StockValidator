"""
Notification models for tracking admin bulletins and user read status
"""
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
import sys
from pathlib import Path

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from shared.database import Base


class Notification(Base):
    """
    Notification model for admin-created bulletins
    
    When an admin creates a notification, entries are automatically
    created in UserNotification for all users (is_read = False)
    """
    __tablename__ = "notifications"
    __table_args__ = (
        Index('idx_notifications_created_by', 'created_by'),
        Index('idx_notifications_created_at', 'created_at'),
        {"schema": "notification_schema"}
    )

    # Primary Key
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Notification Content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Audit Fields
    created_by = Column(PGUUID(as_uuid=True), ForeignKey('auth_schema.users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user_notifications = relationship("UserNotification", back_populates="notification", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, title={self.title[:30]}...)>"


class UserNotification(Base):
    """
    User notification tracking model
    
    Tracks which users have read which notifications
    """
    __tablename__ = "user_notifications"
    __table_args__ = (
        UniqueConstraint('notification_id', 'user_id', name='uq_user_notification'),
        Index('idx_user_notifications_user_id', 'user_id'),
        Index('idx_user_notifications_notification_id', 'notification_id'),
        Index('idx_user_notifications_is_read', 'is_read'),
        {"schema": "notification_schema"}
    )

    # Primary Key
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Foreign Keys
    notification_id = Column(PGUUID(as_uuid=True), ForeignKey('notification_schema.notifications.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(PGUUID(as_uuid=True), ForeignKey('auth_schema.users.id', ondelete='CASCADE'), nullable=False)
    
    # Read Status
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    notification = relationship("Notification", back_populates="user_notifications")
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<UserNotification(user_id={self.user_id}, notification_id={self.notification_id}, is_read={self.is_read})>"

