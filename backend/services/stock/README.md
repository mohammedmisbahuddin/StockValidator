# Stock Service

Stock management microservice for the StockValidator application.

## 🎯 Overview

The Stock Service handles:
- **Stock CRUD operations** (admin only)
- **Ticker validation** using yfinance + Finnhub
- **Stock search with rate limiting** (users)
- **Rate limit management** (admin)

## 📋 Features

### Admin Features
- ✅ Create, read, update, delete stocks
- ✅ Validate stock tickers before adding
- ✅ Track state history (category changes)
- ✅ View all stocks grouped by category
- ✅ Manage user search rate limits
- ✅ Reset individual or all user limits
- ✅ Set universal search limits

### User Features
- ✅ Search for stocks by ticker
- ✅ Validate tickers without using search limit
- ✅ See remaining search limit
- ✅ Only valid searches count against limit

## 🗂️ Stock Categories

Stocks are organized into 4 categories:

1. **far** - Early stage stocks
2. **near** - Getting closer
3. **almost_ready** - Nearly ready
4. **ready** - Ready to trade
   - Subcategories: `pullback1`, `pullback2`

State changes are tracked in the `state_history` field (JSONB).

## 🚀 API Endpoints

### Stock Management (Admin Only)

```
POST   /stocks                   - Create new stock
GET    /stocks                   - Get all stocks (grouped by category)
GET    /stocks/{ticker}          - Get specific stock
PUT    /stocks/{ticker}          - Update stock
DELETE /stocks/{ticker}          - Delete stock
POST   /stocks/validate          - Validate ticker (get name & price)
```

### Stock Search (Users)

```
GET    /stocks/search/{ticker}   - Search with rate limiting
POST   /stocks/validate          - Validate ticker (no limit impact)
```

### Rate Limit Management (Admin Only)

```
GET    /admin/rate-limits/{user_id}        - Get user's rate limit info
PUT    /admin/rate-limits/{user_id}        - Update user's search limit
POST   /admin/rate-limits/{user_id}/reset  - Reset user's limit
POST   /admin/rate-limits/reset-all        - Reset all users' limits
PUT    /admin/rate-limits/universal-limit  - Set universal limit
```

## 📊 Database Schema

### Stocks Table (`stock_schema.stocks`)

```sql
CREATE TABLE stock_schema.stocks (
    ticker VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    category stock_category NOT NULL,
    subcategory stock_subcategory,
    current_price NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP DEFAULT NOW() NOT NULL,
    created_by UUID REFERENCES auth_schema.users(id) NOT NULL,
    state_history JSONB DEFAULT '[]'::jsonb NOT NULL
);
```

### State History Format

```json
[
  {
    "from": "far",
    "to": "near",
    "changed_at": "2024-01-01T00:00:00",
    "changed_by": "uuid-here"
  }
]
```

## 🔌 External APIs

### 1. yfinance (Primary)
- **Free** - No API key required
- Fetches stock information directly
- Returns company name and current price

### 2. Finnhub (Fallback)
- Requires API key (optional)
- Used if yfinance fails
- Configure via `FINNHUB_API_KEY` environment variable

## 🔒 Rate Limiting

### How It Works
1. Each user has a configurable search limit
2. Searches are tracked in Redis: `user_limit:{user_id}`
3. **Only valid ticker searches** decrement the limit
4. Invalid tickers don't count
5. **No automatic reset** - admin must manually reset

### Redis Keys
```
user_limit:{user_id}      → Remaining searches
user_limit_max:{user_id}  → Maximum search limit
```

### Admin Controls
- Reset individual user's limit
- Reset all users' limits at once
- Set universal limit for all users
- Update individual user's limit

## 🛠️ Setup

### 1. Install Dependencies

```bash
cd backend/services/stock
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file or use shared config:

```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=stockvalidator
POSTGRES_USER=stockadmin
POSTGRES_PASSWORD=stockpass123

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Optional: Finnhub API Key
FINNHUB_API_KEY=your_api_key_here
```

### 3. Run Database Migration

```bash
# Make sure Docker Compose is running
docker-compose up -d postgres redis

# Database schema is auto-created via init-db.sql
```

### 4. Start Service

```bash
# Development mode with auto-reload
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --port 8002
```

Service will be available at: **http://localhost:8002**

API Documentation: **http://localhost:8002/docs**

## 📝 Example Usage

### 1. Validate a Ticker (Admin or User)

```bash
curl -X POST http://localhost:8002/stocks/validate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'
```

Response:
```json
{
  "ticker": "AAPL",
  "is_valid": true,
  "company_name": "Apple Inc.",
  "current_price": 185.50,
  "source": "yfinance",
  "error": null
}
```

### 2. Create a Stock (Admin)

```bash
curl -X POST http://localhost:8002/stocks \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "category": "ready",
    "subcategory": "pullback1",
    "current_price": 185.50
  }'
```

### 3. Search for a Stock (User)

```bash
curl -X GET http://localhost:8002/stocks/search/AAPL \
  -H "Authorization: Bearer USER_TOKEN"
```

Response:
```json
{
  "found": true,
  "ticker": "AAPL",
  "stock": { /* stock details */ },
  "company_name": "Apple Inc.",
  "current_price": 185.50,
  "is_valid_ticker": true,
  "remaining_searches": 49,
  "message": "Stock found in our system"
}
```

### 4. Reset All Limits (Admin)

```bash
curl -X POST http://localhost:8002/admin/rate-limits/reset-all \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/ -v
```

### Run Integration Tests

```bash
pytest tests/test_integration.py -v
```

### Test Coverage

```bash
pytest --cov=. --cov-report=html
```

## 📦 Project Structure

```
stock/
├── models/
│   ├── __init__.py
│   └── stock.py              # Stock SQLAlchemy model
├── schemas/
│   ├── __init__.py
│   └── stock.py              # Pydantic schemas
├── routes/
│   ├── __init__.py
│   ├── stock_routes.py       # Stock CRUD + search endpoints
│   └── rate_limit_routes.py # Admin rate limit management
├── services/
│   ├── __init__.py
│   ├── stock_service.py      # Stock business logic
│   ├── ticker_validator.py  # yfinance + Finnhub integration
│   └── rate_limiter.py       # Redis-based rate limiting
├── tests/
│   ├── __init__.py
│   ├── test_stock_service.py
│   └── test_rate_limiter.py
├── main.py                   # FastAPI application
├── requirements.txt          # Dependencies
└── README.md                 # This file
```

## 🔗 Dependencies

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM for PostgreSQL
- **Redis** - Rate limiting and caching
- **yfinance** - Stock data (primary)
- **requests** - HTTP client for Finnhub

## 🚀 Deployment

### Run with Docker

```bash
# Build image
docker build -t stock-service .

# Run container
docker run -p 8002:8002 \
  -e POSTGRES_HOST=postgres \
  -e REDIS_HOST=redis \
  stock-service
```

### Health Check

```bash
curl http://localhost:8002/health
```

Response:
```json
{
  "status": "healthy",
  "service": "stock-service",
  "version": "1.0.0"
}
```

## 📈 Performance Considerations

- **Redis** is used for high-speed rate limit checks
- **Indexes** on `category` and `created_by` for fast queries
- **JSONB** for flexible state history storage
- **Connection pooling** via SQLAlchemy

## 🔐 Security

- All endpoints require JWT authentication
- Admin endpoints require `role=admin`
- User searches are rate-limited
- SQL injection protected by SQLAlchemy ORM

## 📚 Related Services

- **Auth Service** (port 8001) - User authentication
- **Notification Service** (port 8003) - User notifications
- **API Gateway** (port 8000) - Unified entry point

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update this README for API changes
4. Use type hints and docstrings

## 📄 License

Part of the StockValidator application.

---

**Service:** Stock Service  
**Port:** 8002  
**Version:** 1.0.0  
**Status:** ✅ Complete (Phase 3)

