# 🚀 Quick Start - Testing All Functionality

## Prerequisites

1. **Start Docker Desktop** (if not already running)
2. **Ensure Python 3.9+ is installed**
3. **Virtual environment activated**

---

## Step 1: Start Infrastructure Services

```bash
cd /Users/mmisbahuddin/Documents/Personal_work/StockValidator

# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Wait for services to be ready (10 seconds)
sleep 10

# Verify services are running
docker ps
```

**Expected Output:**
```
CONTAINER ID   IMAGE                    STATUS
xxx            postgres:15-alpine       Up X seconds
xxx            redis:7-alpine           Up X seconds
```

---

## Step 2: Start Auth Service

```bash
cd backend/services/auth
source ../../venv/bin/activate

# Start Auth Service (Port 8001)
python main.py > /tmp/auth_service.log 2>&1 &

# Wait for startup
sleep 3

# Check if running
curl http://localhost:8001/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "auth",
  "redis": "connected"
}
```

---

## Step 3: Start Stock Service

```bash
cd backend/services/stock
source ../../venv/bin/activate

# Start Stock Service (Port 8002)
python main.py > /tmp/stock_service.log 2>&1 &

# Wait for startup
sleep 3

# Check if running
curl http://localhost:8002/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "stock"
}
```

---

## Step 4: Test All Endpoints

### Option A: Automated Test Script (Recommended)

```bash
cd /Users/mmisbahuddin/Documents/Personal_work/StockValidator

# Run comprehensive test suite
./test_all_endpoints.sh
```

This will test all 16 endpoints and generate a report.

### Option B: Swagger UI (Interactive)

#### Auth Service Swagger:
**URL:** http://localhost:8001/docs

**Endpoints to Test:**
1. `POST /auth/register` - Register admin/user
2. `POST /auth/login` - Login and get tokens
3. `GET /auth/me` - Get current user (use Authorize button)
4. `POST /auth/refresh` - Refresh token

#### Stock Service Swagger:
**URL:** http://localhost:8002/docs

**Endpoints to Test:**

**Admin Endpoints:**
1. `POST /stocks/validate` - Validate ticker (AAPL, RELIANCE.NS, TCS)
2. `POST /stocks` - Create stock
3. `GET /stocks` - Get all stocks
4. `GET /stocks/{ticker}` - Get specific stock
5. `PUT /stocks/{ticker}` - Update stock
6. `DELETE /stocks/{ticker}` - Delete stock

**User Endpoints:**
1. `GET /stocks/search/{ticker}` - Search stock
2. `POST /stocks/validate` - Validate ticker

**Rate Limit Management:**
1. `GET /admin/rate-limits/{user_id}` - Get user limit
2. `PUT /admin/rate-limits/{user_id}` - Update limit
3. `POST /admin/rate-limits/{user_id}/reset` - Reset limit
4. `POST /admin/rate-limits/reset-all` - Reset all

---

## Step 5: Manual Testing (Quick)

### 1. Register and Login

```bash
# Register Admin
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "username": "testadmin",
    "password": "Admin@123",
    "role": "admin"
  }'

# Login Admin
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testadmin",
    "password": "Admin@123"
  }'

# Save the access_token from response
export ADMIN_TOKEN="your_access_token_here"
```

### 2. Test Stock Validation

```bash
# Validate US Stock
curl -X POST http://localhost:8002/stocks/validate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"ticker": "AAPL"}'

# Validate Indian Stock
curl -X POST http://localhost:8002/stocks/validate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"ticker": "RELIANCE.NS"}'

# Auto-detect Indian Stock
curl -X POST http://localhost:8002/stocks/validate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"ticker": "TCS"}'
```

### 3. Create Stock

```bash
curl -X POST http://localhost:8002/stocks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "category": "ready",
    "subcategory": "pullback1",
    "current_price": 175.50
  }'
```

### 4. Get All Stocks

```bash
curl -X GET http://localhost:8002/stocks \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### 5. Search Stock (User)

```bash
# Register User
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@test.com",
    "username": "testuser",
    "password": "User@123",
    "role": "user"
  }'

# Login User
USER_RESPONSE=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "User@123"}')

export USER_TOKEN=$(echo $USER_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Search Stock
curl -X GET "http://localhost:8002/stocks/search/AAPL" \
  -H "Authorization: Bearer $USER_TOKEN"
```

---

## Step 6: JMeter Testing

```bash
cd testing/jmeter

# Open JMeter GUI
jmeter -t StockValidator_API_Tests.jmx

# Or run headless
jmeter -n -t StockValidator_API_Tests.jmx -l results.jtl -e -o report/
```

---

## Troubleshooting

### Services Not Starting?

1. **Check Docker:**
   ```bash
   docker ps
   docker-compose ps
   ```

2. **Check Logs:**
   ```bash
   # Auth Service
   tail -f /tmp/auth_service.log
   
   # Stock Service
   tail -f /tmp/stock_service.log
   
   # PostgreSQL
   docker logs stockvalidator-postgres
   
   # Redis
   docker logs stockvalidator-redis
   ```

3. **Check Ports:**
   ```bash
   lsof -i :8001  # Auth Service
   lsof -i :8002  # Stock Service
   lsof -i :5433  # PostgreSQL
   lsof -i :6379  # Redis
   ```

### Database Connection Issues?

```bash
# Test PostgreSQL connection
docker exec -it stockvalidator-postgres psql -U stockadmin -d stockvalidator -c "SELECT 1;"

# Check tables
docker exec -it stockvalidator-postgres psql -U stockadmin -d stockvalidator -c "\dt auth_schema.*"
docker exec -it stockvalidator-postgres psql -U stockadmin -d stockvalidator -c "\dt stock_schema.*"
```

### Redis Connection Issues?

```bash
# Test Redis connection
docker exec -it stockvalidator-redis redis-cli ping

# Should return: PONG
```

---

## Expected Test Results

### ✅ All Tests Should Pass:

**Auth Service (4 endpoints):**
- ✅ Register Admin
- ✅ Register User
- ✅ Login Admin
- ✅ Login User
- ✅ Get Current User

**Stock Service - Admin (7 endpoints):**
- ✅ Validate Ticker (US)
- ✅ Validate Ticker (Indian)
- ✅ Validate Ticker (Auto-detect)
- ✅ Create Stock
- ✅ Get All Stocks
- ✅ Get Specific Stock
- ✅ Update Stock
- ✅ Delete Stock

**Stock Service - User (2 endpoints):**
- ✅ Search Stock (Found)
- ✅ Search Stock (Not Found but Valid)
- ✅ Validate Ticker (No Limit)

**Rate Limit Management (4 endpoints):**
- ✅ Get User Rate Limit
- ✅ Update User Limit
- ✅ Reset User Limit
- ✅ Reset All Limits

**Total: 16+ endpoints, all working!** ✅

---

## Quick Status Check

```bash
# Check all services
echo "=== Service Status ==="
echo "Auth Service:"
curl -s http://localhost:8001/health | python3 -m json.tool || echo "❌ Not running"

echo ""
echo "Stock Service:"
curl -s http://localhost:8002/health | python3 -m json.tool || echo "❌ Not running"

echo ""
echo "PostgreSQL:"
docker ps --filter "name=postgres" --format "{{.Status}}" || echo "❌ Not running"

echo ""
echo "Redis:"
docker ps --filter "name=redis" --format "{{.Status}}" || echo "❌ Not running"
```

---

## Next Steps

Once all tests pass:
1. ✅ Review `ACHIEVEMENT_REPORT.md` for complete status
2. ✅ Check Swagger docs for API details
3. ✅ Review test results
4. 🚀 Proceed to Phase 4 (Notification Service)

---

**Happy Testing!** 🎉

