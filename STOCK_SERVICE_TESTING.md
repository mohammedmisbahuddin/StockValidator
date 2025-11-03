# Testing the Stock Service 🧪

Quick guide to test the Stock Service with JMeter and manual API calls.

---

## 🚀 Quick Start

### 1. Start All Services

```bash
# Start infrastructure
docker-compose up -d postgres redis

# Start Auth Service (Terminal 1)
cd backend/services/auth
source ../../venv/bin/activate
python main.py

# Start Stock Service (Terminal 2)
cd backend/services/stock
source ../../venv/bin/activate
python main.py
```

### 2. Verify Services

```bash
# Check Auth Service
curl http://localhost:8001/health
# Expected: {"status":"healthy","service":"auth-service","version":"1.0.0"}

# Check Stock Service
curl http://localhost:8002/health
# Expected: {"status":"healthy","service":"stock-service","version":"1.0.0"}
```

---

## 🎯 Option 1: JMeter Tests (Recommended)

### Run All Tests

```bash
cd testing/jmeter
jmeter -t StockValidator_API_Tests.jmx
```

This will open JMeter GUI with all tests configured.

### How to Run Tests in JMeter GUI

1. **Expand the test plan** on the left sidebar
2. **Find these Stock Service thread groups:**
   - 📦 Stock Service - Admin Operations
   - 🔍 Stock Service - User Search & Rate Limiting
   - ⚙️ Stock Service - Admin Rate Limit Management

3. **Run setUp first** (important!):
   - Right-click on `🏁 setUp Thread Group (Runs First)`
   - Click **Start**
   - Wait for it to complete (registers users, extracts tokens)

4. **Run Stock Service tests:**
   - Right-click on `📦 Stock Service - Admin Operations`
   - Click **Start**
   - Check **View Results Tree** at the bottom to see results

5. **View Results:**
   - Click on **View Results Tree** listener
   - Click on any request to see:
     - Request details
     - Response data
     - Response headers
     - Assertions (pass/fail)

### What Each Thread Group Tests

#### 📦 Stock Service - Admin Operations
✅ **1. Validate Ticker - AAPL**
   - Validates AAPL with yfinance/Finnhub
   - Extracts company name and price

✅ **2. Create Stock - AAPL (Ready/Pullback1)**
   - Creates AAPL stock in "ready" category
   - Sets subcategory to "pullback1"

✅ **3. Create Stock - MSFT (Near)**
   - Creates MSFT stock in "near" category

✅ **4. Get All Stocks (Grouped by Category)**
   - Returns all stocks grouped by far, near, almost_ready, ready

✅ **5. Update Stock - AAPL (Near)**
   - Changes AAPL from "ready" to "near"
   - Tracks state change in state_history

✅ **6. Get Specific Stock - MSFT**
   - Retrieves MSFT stock details

#### 🔍 Stock Service - User Search & Rate Limiting
✅ **1. Search Valid Stock - AAPL (Found in System)**
   - User searches for AAPL
   - Stock found, limit decremented
   - Returns remaining searches

✅ **2. Search Valid Stock - GOOGL (Not in System)**
   - User searches for GOOGL
   - Valid ticker but not in our system
   - Limit still decremented

✅ **3. Search Invalid Stock - INVALID123 (No Limit Decrement)**
   - User searches for invalid ticker
   - Limit NOT decremented (as per requirement)

#### ⚙️ Stock Service - Admin Rate Limit Management
✅ **1. Get User Rate Limit Info**
   - Admin views user's rate limit details

✅ **2. Update User Rate Limit (100 searches)**
   - Admin sets user's limit to 100

✅ **3. Reset User Rate Limit**
   - Admin resets individual user's limit

✅ **4. Reset All User Rate Limits**
   - Admin resets all users' limits at once

✅ **5. Set Universal Rate Limit (50 searches)**
   - Admin sets same limit for all users

---

## 🔧 Option 2: Manual API Testing

### Step 1: Register and Login

```bash
# Register Admin
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "username": "admin",
    "password": "Admin@123",
    "role": "admin"
  }'

# Login Admin
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "Admin@123"
  }'

# Copy the access_token from response
export ADMIN_TOKEN="YOUR_ACCESS_TOKEN_HERE"
```

### Step 2: Validate a Ticker

```bash
curl -X POST http://localhost:8002/stocks/validate \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL"
  }'
```

**Expected Response:**
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

### Step 3: Create a Stock

```bash
curl -X POST http://localhost:8002/stocks \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "category": "ready",
    "subcategory": "pullback1",
    "current_price": 185.50
  }'
```

### Step 4: Get All Stocks

```bash
curl -X GET http://localhost:8002/stocks \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Expected Response:**
```json
{
  "far": [],
  "near": [],
  "almost_ready": [],
  "ready": [
    {
      "ticker": "AAPL",
      "company_name": "Apple Inc.",
      "category": "ready",
      "subcategory": "pullback1",
      "current_price": 185.50,
      "created_at": "2025-11-03T...",
      "updated_at": "2025-11-03T...",
      "state_history": []
    }
  ],
  "total": 1
}
```

### Step 5: Update Stock Category

```bash
curl -X PUT http://localhost:8002/stocks/AAPL \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "near",
    "subcategory": null
  }'
```

### Step 6: User Search (with Rate Limiting)

First, register a regular user:

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
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "User@123"
  }'

# Copy the access_token
export USER_TOKEN="USER_ACCESS_TOKEN_HERE"

# Search for a stock
curl -X GET http://localhost:8002/stocks/search/AAPL \
  -H "Authorization: Bearer $USER_TOKEN"
```

**Expected Response:**
```json
{
  "found": true,
  "ticker": "AAPL",
  "stock": {
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    ...
  },
  "company_name": "Apple Inc.",
  "current_price": 185.50,
  "is_valid_ticker": true,
  "remaining_searches": 49,
  "message": "Stock found in our system"
}
```

### Step 7: Admin Rate Limit Management

```bash
# Get User's Rate Limit Info
curl -X GET http://localhost:8002/admin/rate-limits/USER_ID_HERE \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Update User's Limit
curl -X PUT http://localhost:8002/admin/rate-limits/USER_ID_HERE \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "search_limit": 100
  }'

# Reset User's Limit
curl -X POST http://localhost:8002/admin/rate-limits/USER_ID_HERE/reset \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Reset All Users' Limits
curl -X POST http://localhost:8002/admin/rate-limits/reset-all \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Set Universal Limit
curl -X PUT http://localhost:8002/admin/rate-limits/universal-limit \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "search_limit": 50
  }'
```

---

## 📊 Expected Results

### ✅ Success Indicators
- All HTTP status codes match expected (200, 201, 204)
- Ticker validation returns company name and price
- Stock CRUD operations work correctly
- Rate limiting decrements only for valid tickers
- Invalid tickers don't decrement limit
- State history tracks category changes

### ❌ Common Issues

**Issue: 401 Unauthorized**
- **Cause:** Missing or invalid JWT token
- **Fix:** Make sure you've logged in and exported the token

**Issue: 404 Not Found**
- **Cause:** Stock Service not running
- **Fix:** Start Stock Service on port 8002

**Issue: Ticker Validation Slow**
- **Cause:** External API (yfinance/Finnhub) slow
- **Expected:** Ticker validation can take 500-1500ms

**Issue: Rate limit not working**
- **Cause:** Redis not running
- **Fix:** `docker-compose up -d redis`

---

## 🎯 Testing Checklist

### Admin Operations
- [ ] Validate ticker returns company name and price
- [ ] Create stock with all categories (far, near, almost_ready, ready)
- [ ] Create stock with subcategories (pullback1, pullback2) for "ready"
- [ ] Get all stocks returns grouped by category
- [ ] Update stock changes category successfully
- [ ] State history tracks category changes
- [ ] Delete stock removes it from database

### User Search
- [ ] Search for stock in system returns stock details
- [ ] Search for valid ticker not in system returns "not in our system"
- [ ] Search for invalid ticker returns "invalid ticker"
- [ ] Valid searches decrement rate limit
- [ ] Invalid searches DON'T decrement rate limit
- [ ] Remaining searches displayed correctly

### Admin Rate Limit Management
- [ ] View user's rate limit info
- [ ] Update individual user's limit
- [ ] Reset individual user's limit
- [ ] Reset all users' limits
- [ ] Set universal limit for all users

---

## 🚀 API Documentation

Full API documentation available at:
- **Stock Service:** http://localhost:8002/docs
- **Auth Service:** http://localhost:8001/docs

---

## 📈 Next Steps

After testing Stock Service:
1. ✅ Review test results in JMeter
2. ✅ Check logs for any errors
3. ✅ Verify rate limiting in Redis
4. ✅ Test edge cases (duplicate tickers, invalid data)
5. 🎯 Ready for Phase 4: Notification Service

---

**Last Updated:** November 3, 2025  
**Phase:** 3 Complete  
**Services Tested:** Auth + Stock  
**Total Endpoints:** 20+

