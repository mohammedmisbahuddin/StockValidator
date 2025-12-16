# 🎯 Next Phase: Notification Service (Phase 4)

## 📊 Current Status

| Phase | Status | Progress |
|-------|--------|----------|
| ✅ Phase 1: Infrastructure | Complete | 100% |
| ✅ Phase 2: Auth Service | Complete | 100% |
| ✅ Phase 3: Stock Service | Complete | 100% |
| 🎯 **Phase 4: Notification Service** | **NEXT** | **0%** |
| 📅 Phase 5: API Gateway | Planned | 0% |
| 📅 Phase 6: Admin Frontend | Planned | 0% |
| 📅 Phase 7: User Frontend | Planned | 0% |

---

## 🎯 Phase 4: Notification Service

**Duration:** Estimated 1 day  
**Status:** Ready to Start  
**Port:** 8003

---

## 📋 Requirements

### **Purpose:**
Admin bulletin board system where admins can post notifications/announcements that users can view and mark as read.

### **Features:**

#### **Admin Features:**
- ✅ Create notifications (title, message)
- ✅ View all notifications
- ✅ Update notifications
- ✅ Delete notifications
- ✅ See who created each notification

#### **User Features:**
- ✅ View all notifications (bulletin board)
- ✅ Mark notifications as read
- ✅ See unread notification count
- ✅ View notification history

---

## 🔌 API Endpoints to Build

### **Admin Endpoints (5):**

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/notifications` | Create new notification | Admin |
| GET | `/notifications` | List all notifications | Admin |
| GET | `/notifications/{id}` | Get specific notification | Admin |
| PUT | `/notifications/{id}` | Update notification | Admin |
| DELETE | `/notifications/{id}` | Delete notification | Admin |

### **User Endpoints (3):**

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/notifications` | Get my notifications | User |
| GET | `/notifications/unread-count` | Get unread count | User |
| PUT | `/notifications/{id}/read` | Mark as read | User |

---

## 🗄️ Database Schema

### **Table 1: `notifications`**
```sql
CREATE TABLE notification_schema.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    created_by UUID REFERENCES auth_schema.users(id) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_notifications_created_by ON notification_schema.notifications(created_by);
CREATE INDEX idx_notifications_created_at ON notification_schema.notifications(created_at DESC);
```

### **Table 2: `user_notifications`**
```sql
CREATE TABLE notification_schema.user_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    notification_id UUID REFERENCES notification_schema.notifications(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES auth_schema.users(id) ON DELETE CASCADE NOT NULL,
    is_read BOOLEAN DEFAULT FALSE NOT NULL,
    read_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    UNIQUE(notification_id, user_id)
);

CREATE INDEX idx_user_notifications_user_id ON notification_schema.user_notifications(user_id);
CREATE INDEX idx_user_notifications_notification_id ON notification_schema.user_notifications(notification_id);
CREATE INDEX idx_user_notifications_is_read ON notification_schema.user_notifications(is_read);
```

---

## 📁 Project Structure

```
backend/services/notification/
├── __init__.py
├── main.py                    # FastAPI app (port 8003)
├── requirements.txt
│
├── models/
│   ├── __init__.py
│   └── notification.py        # SQLAlchemy models
│
├── schemas/
│   ├── __init__.py
│   └── notification.py        # Pydantic schemas
│
├── routes/
│   ├── __init__.py
│   └── notification_routes.py # API routes
│
├── services/
│   ├── __init__.py
│   └── notification_service.py # Business logic
│
└── tests/
    ├── __init__.py
    └── test_notifications.py   # Unit tests
```

---

## 🔧 Implementation Steps

### **Step 1: Database Setup**
- [ ] Add notification tables to `init-db.sql`
- [ ] Run migration/create tables
- [ ] Verify schema

### **Step 2: Models & Schemas**
- [ ] Create `Notification` model (SQLAlchemy)
- [ ] Create `UserNotification` model (SQLAlchemy)
- [ ] Create Pydantic schemas:
  - `NotificationCreate`
  - `NotificationUpdate`
  - `NotificationResponse`
  - `NotificationListResponse`
  - `UserNotificationResponse`
  - `UnreadCountResponse`

### **Step 3: Service Layer**
- [ ] Create `NotificationService` class
- [ ] Implement CRUD operations
- [ ] Implement user notification tracking
- [ ] Implement mark as read functionality
- [ ] Implement unread count

### **Step 4: Routes**
- [ ] Admin routes (CRUD)
- [ ] User routes (view, mark as read)
- [ ] Add authentication middleware
- [ ] Add error handling

### **Step 5: Testing**
- [ ] Unit tests
- [ ] Integration tests
- [ ] Test admin operations
- [ ] Test user operations
- [ ] Test read/unread functionality

### **Step 6: Documentation**
- [ ] Update Swagger docs
- [ ] Add to JMeter tests
- [ ] Update API documentation

---

## 📝 API Request/Response Examples

### **Create Notification (Admin)**
```http
POST /notifications
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "title": "Market Update",
  "message": "Important market trends for this week..."
}
```

**Response:**
```json
{
  "id": "uuid",
  "title": "Market Update",
  "message": "Important market trends for this week...",
  "created_by": "admin-uuid",
  "created_at": "2025-12-16T10:00:00Z",
  "updated_at": "2025-12-16T10:00:00Z"
}
```

### **Get My Notifications (User)**
```http
GET /notifications
Authorization: Bearer {user_token}
```

**Response:**
```json
{
  "notifications": [
    {
      "id": "uuid",
      "title": "Market Update",
      "message": "Important market trends...",
      "is_read": false,
      "read_at": null,
      "created_at": "2025-12-16T10:00:00Z"
    }
  ],
  "unread_count": 3,
  "total": 5
}
```

### **Mark as Read (User)**
```http
PUT /notifications/{id}/read
Authorization: Bearer {user_token}
```

**Response:**
```json
{
  "success": true,
  "message": "Notification marked as read",
  "notification_id": "uuid"
}
```

---

## 🎨 Business Logic

### **Notification Creation:**
1. Admin creates notification
2. System creates entry in `notifications` table
3. System creates entries in `user_notifications` for ALL users (is_read = false)
4. Users can now see the notification

### **User Views Notifications:**
1. User requests notifications
2. System fetches all notifications with user's read status
3. Returns notifications sorted by created_at (newest first)
4. Includes unread count

### **Mark as Read:**
1. User marks notification as read
2. System updates `user_notifications` record:
   - Set `is_read = true`
   - Set `read_at = CURRENT_TIMESTAMP`
3. Returns success response

---

## 🔐 Security & Permissions

- **Admin Endpoints:** Require `admin` role
- **User Endpoints:** Require `user` or `admin` role
- **Authorization:** Use shared `auth_middleware`
- **Data Isolation:** Users only see their own read status

---

## 📊 Estimated Timeline

| Task | Time |
|------|------|
| Database setup | 30 min |
| Models & Schemas | 1 hour |
| Service layer | 2 hours |
| Routes & API | 2 hours |
| Testing | 1.5 hours |
| Documentation | 30 min |
| **Total** | **~7-8 hours** |

---

## ✅ Success Criteria

- [ ] All admin CRUD endpoints working
- [ ] Users can view notifications
- [ ] Users can mark notifications as read
- [ ] Unread count works correctly
- [ ] All tests passing
- [ ] Swagger documentation complete
- [ ] JMeter tests added

---

## 🚀 Ready to Start?

**Next Steps:**
1. Set up database tables
2. Create service structure
3. Implement models and schemas
4. Build API endpoints
5. Add tests

**Let's begin Phase 4!** 🎯

