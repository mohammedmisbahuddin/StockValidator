# StockValidator - Development Phases

**Project:** Stock Trading Application for Admin & Users  
**Architecture:** Microservices (Auth, Stock, Notification, API Gateway)  
**Stack:** FastAPI (Backend) + Next.js (Frontend) + PostgreSQL + Redis

---

## 📋 Complete Phase Overview

### ✅ **Phase 1: Project Setup & Infrastructure** (COMPLETE)
**Duration:** Initial setup  
**Status:** ✅ Done

**Deliverables:**
- ✅ Project structure created
- ✅ Docker Compose for PostgreSQL & Redis
- ✅ Database schemas defined (auth_schema, stock_schema, notification_schema)
- ✅ Shared utilities (config, database, redis_client, auth_utils)
- ✅ Virtual environment setup
- ✅ `.gitignore` and README

**Files:**
- `docker-compose.yml`
- `backend/shared/` (config, database, redis_client, auth_utils)
- `backend/init-db.sql`
- `.env`

---

### ✅ **Phase 2: Authentication Service** (COMPLETE)
**Duration:** Completed with full testing  
**Status:** ✅ Done

**Deliverables:**
- ✅ User model with roles (admin/user)
- ✅ Registration endpoint
- ✅ Login endpoint (JWT tokens)
- ✅ Token refresh endpoint
- ✅ Get current user endpoint
- ✅ Password hashing (bcrypt)
- ✅ JWT authentication middleware
- ✅ Unit tests (pytest)
- ✅ Integration tests (pytest + httpx)
- ✅ End-to-end bash tests
- ✅ JMeter load tests with variable sharing

**API Endpoints:**
```
POST   /auth/register        - Register new user
POST   /auth/login           - Login and get tokens
POST   /auth/refresh         - Refresh access token
GET    /auth/me              - Get current user profile
```

**Files:**
- `backend/services/auth/`
  - `main.py`, `models/`, `schemas/`, `routes/`, `services/`, `middleware/`, `tests/`
- `testing/jmeter/StockValidator_API_Tests.jmx`

**Test Status:**
- ✅ All unit tests passing
- ✅ All integration tests passing
- ✅ JMeter: 14 requests (11 pass, 3 expected errors)

---

### 🔄 **Phase 3: Stock Service** (NEXT - IN PROGRESS)
**Duration:** Estimated 2-3 days  
**Status:** 🔄 Starting Now

**Requirements:**

#### **Stock States:**
1. **Far** - Early stage stocks
2. **Near** - Getting closer
3. **Almost Ready** - Nearly ready
4. **Ready** - Ready to trade
   - Subcategories: `Pullback1`, `Pullback2`

#### **Admin Functionalities:**
- ✅ Add new stock (ticker, category, subcategory)
- ✅ Edit stock (change category/subcategory)
- ✅ Delete stock
- ✅ View all stocks grouped by category
- ✅ Track state change timestamps
- ✅ **Stock ticker validation:**
  - Validate ticker using `yfinance` (primary)
  - Fallback to `Finnhub` API
  - Show company name and current market price before saving

#### **User Functionalities:**
- ✅ Search for stock by ticker
- ✅ View stock details if found in system
- ✅ See company name and market price for ANY valid ticker
- ✅ **Rate limiting:**
  - Each valid search decrements user's limit
  - Invalid tickers don't count
  - Manual reset by admin only (no auto 24h reset)

#### **API Endpoints to Build:**
```
Admin:
  POST   /stocks                 - Add new stock (with validation)
  GET    /stocks                 - List all stocks (grouped by category)
  GET    /stocks/{ticker}        - Get stock details
  PUT    /stocks/{ticker}        - Update stock category/subcategory
  DELETE /stocks/{ticker}        - Delete stock
  POST   /stocks/validate        - Validate ticker (returns company name, price)

User:
  GET    /stocks/search?q={ticker}  - Search stock (with rate limiting)
  POST   /stocks/validate           - Validate ticker (show name, price)

Admin (Rate Limit Management):
  POST   /users/{user_id}/reset-limit    - Reset individual user's limit
  POST   /users/reset-all-limits         - Reset all users' limits
  PUT    /users/{user_id}/limit          - Update user's search limit
  PUT    /users/universal-limit          - Set universal limit for all users
```

#### **Database Tables:**
```sql
CREATE TABLE stock_schema.stocks (
    ticker VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,  -- far, near, almost_ready, ready
    subcategory VARCHAR(50),         -- pullback1, pullback2 (only for 'ready')
    current_price DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID REFERENCES auth_schema.users(id),
    state_history JSONB DEFAULT '[]'::jsonb  -- Track category changes
);

CREATE INDEX idx_stocks_category ON stock_schema.stocks(category);
CREATE INDEX idx_stocks_created_by ON stock_schema.stocks(created_by);
```

#### **External API Integration:**
1. **yfinance (Primary):**
   ```python
   import yfinance as yf
   ticker = yf.Ticker("AAPL")
   info = ticker.info
   company_name = info.get('longName')
   current_price = info.get('currentPrice')
   ```

2. **Finnhub (Fallback):**
   ```python
   import requests
   url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={API_KEY}"
   ```

#### **Rate Limiting Logic:**
```python
async def check_rate_limit(user_id: str, is_valid_ticker: bool):
    """
    Decrement user's search limit only if ticker is valid
    (either found in DB or valid external ticker)
    """
    if is_valid_ticker:
        # Decrement from Redis
        current = await redis.get(f"user_limit:{user_id}")
        if int(current) <= 0:
            raise RateLimitExceeded()
        await redis.decr(f"user_limit:{user_id}")
```

**Deliverables:**
- [ ] Stock model with state tracking
- [ ] Stock CRUD endpoints (admin only)
- [ ] Stock search endpoint (users)
- [ ] Ticker validation service (yfinance + Finnhub)
- [ ] Rate limiting service (Redis-based)
- [ ] Admin rate limit management endpoints
- [ ] Unit tests
- [ ] Integration tests
- [ ] JMeter test scripts

---

### 📅 **Phase 4: Notification Service** (UPCOMING)
**Duration:** Estimated 1 day  
**Status:** 📅 Planned

**Requirements:**
- Admin bulletin board
- CRUD operations for notifications
- User view notifications endpoint
- Mark as read functionality

**API Endpoints:**
```
Admin:
  POST   /notifications          - Create notification
  GET    /notifications          - List all notifications
  PUT    /notifications/{id}     - Update notification
  DELETE /notifications/{id}     - Delete notification

User:
  GET    /notifications          - Get my notifications
  PUT    /notifications/{id}/read - Mark as read
```

**Database:**
```sql
CREATE TABLE notification_schema.notifications (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    message TEXT,
    created_by UUID REFERENCES auth_schema.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE notification_schema.user_notifications (
    id UUID PRIMARY KEY,
    notification_id UUID REFERENCES notification_schema.notifications(id),
    user_id UUID REFERENCES auth_schema.users(id),
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP
);
```

---

### 📅 **Phase 5: API Gateway** (UPCOMING)
**Duration:** Estimated 1-2 days  
**Status:** 📅 Planned

**Requirements:**
- Route requests to appropriate services
- Unified API endpoint
- Request/response transformation
- Rate limiting at gateway level
- API documentation (Swagger/OpenAPI)

**Technology:**
- FastAPI with reverse proxy
- OR Kong/NGINX as API Gateway

**Endpoints:**
```
/api/auth/*          → Auth Service (port 8001)
/api/stocks/*        → Stock Service (port 8002)
/api/notifications/* → Notification Service (port 8003)
```

---

### 📅 **Phase 6: Frontend - Admin Dashboard** (UPCOMING)
**Duration:** Estimated 3-4 days  
**Status:** 📅 Planned

**Technology:** Next.js + TailwindCSS + shadcn/ui  
**Theme:** White, Black, Gold (Premium)

**Pages:**
1. **Login** (`/login`)
2. **Admin Dashboard** (`/admin/dashboard`)
   - 4 Widgets: Far, Near, Almost Ready, Ready
   - Each widget shows stock count
   - Click to expand and see stock list
3. **Stock Management** (`/admin/stocks`)
   - Add new stock (with validation)
   - Edit stock (drag-and-drop between categories?)
   - Delete stock
   - View state change history
4. **User Management** (`/admin/users`)
   - Create user
   - Edit user (name, email, phone, limit)
   - View users list
   - Individual limit reset
   - Universal limit setting
5. **Notifications** (`/admin/notifications`)
   - Create bulletin
   - Edit/delete bulletins
   - View all bulletins

**UI Components:**
- Stock cards with company name, ticker, price
- Drag-and-drop between categories (optional)
- Search bar for stock ticker validation
- Modal for add/edit forms
- Toast notifications
- Loading states

---

### 📅 **Phase 7: Frontend - User Dashboard** (UPCOMING)
**Duration:** Estimated 2 days  
**Status:** 📅 Planned

**Pages:**
1. **Login** (`/login`)
2. **User Dashboard** (`/user/dashboard`)
   - Search box for stock ticker
   - Display search results (stock details)
   - Show remaining search limit
   - Bulletin board (notifications from admin)
3. **Change Password** (`/user/settings`)

**Features:**
- Real-time search limit display
- Stock details card with price
- Notification badges
- Responsive design

---

### 📅 **Phase 8: Testing & Quality Assurance** (UPCOMING)
**Duration:** Ongoing + 2 days dedicated  
**Status:** 📅 Planned

**Activities:**
- End-to-end testing
- Performance testing (JMeter)
- Security testing
- User acceptance testing
- Bug fixes
- Code review
- Documentation review

---

### 📅 **Phase 9: Deployment** (UPCOMING)
**Duration:** 1-2 days  
**Status:** 📅 Planned

**Options:**
1. **AWS:** ECS/EKS + RDS + ElastiCache
2. **DigitalOcean:** App Platform + Managed Database
3. **Heroku:** Simple deployment
4. **Vercel (Frontend)** + AWS/DO (Backend)

**Tasks:**
- Docker images for each service
- CI/CD pipeline (GitHub Actions)
- Environment configuration
- Database migration scripts
- Monitoring & logging setup
- Backup strategy

---

### 📅 **Phase 10: Mobile App** (FUTURE)
**Duration:** 2-3 weeks  
**Status:** 📅 Future Enhancement

**Technology:** Capacitor (wrap Next.js app)  
**Platforms:** iOS, Android

---

## 📊 Current Status Summary

| Phase | Status | Progress |
|-------|--------|----------|
| 1. Infrastructure | ✅ Complete | 100% |
| 2. Auth Service | ✅ Complete | 100% |
| 3. Stock Service | 🔄 In Progress | 0% → Starting Now! |
| 4. Notification Service | 📅 Planned | 0% |
| 5. API Gateway | 📅 Planned | 0% |
| 6. Admin Frontend | 📅 Planned | 0% |
| 7. User Frontend | 📅 Planned | 0% |
| 8. Testing & QA | 📅 Planned | 0% |
| 9. Deployment | 📅 Planned | 0% |
| 10. Mobile App | 📅 Future | 0% |

---

## 🎯 Next Steps: Phase 3 - Stock Service

**Let's start with:**
1. ✅ Define Stock model
2. ✅ Set up stock service structure
3. ✅ Implement ticker validation (yfinance + Finnhub)
4. ✅ Build CRUD endpoints
5. ✅ Implement rate limiting
6. ✅ Write tests
7. ✅ Add to JMeter

**Estimated Time:** 2-3 days

Ready to start Phase 3? 🚀

