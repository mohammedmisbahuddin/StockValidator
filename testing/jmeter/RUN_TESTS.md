# Quick Guide: Running JMeter Tests

## ✅ Issue Fixed!

**Problem:** JSONAssertion elements required a plugin  
**Solution:** Removed JSONAssertion, using ResponseAssertion only

---

## 🚀 How to Run Tests

### Step 1: Start Services

```bash
# Terminal 1: Start Docker (PostgreSQL + Redis)
cd /Users/mmisbahuddin/Documents/Personal_work/StockValidator/backend
docker-compose up -d postgres redis

# Wait for services to be ready
sleep 5

# Terminal 2: Start Auth Service
cd /Users/mmisbahuddin/Documents/Personal_work/StockValidator/backend/services/auth
source ../../venv/bin/activate
python main.py
```

**Verify Auth Service:**
```bash
curl http://localhost:8001/health
# Should return: {"status":"healthy","service":"auth","redis":"connected"}
```

---

### Step 2: Run JMeter Tests

#### Option A: GUI Mode (Recommended First Time)

```bash
cd /Users/mmisbahuddin/Documents/Personal_work/StockValidator/testing/jmeter
jmeter -t StockValidator_API_Tests.jmx
```

Then in JMeter GUI:
1. Click the green "Play" button (▶️) at the top
2. Watch tests execute in real-time
3. Click "View Results Tree" to see requests/responses
4. Click "Summary Report" to see statistics

#### Option B: Command Line (Headless)

```bash
cd /Users/mmisbahuddin/Documents/Personal_work/StockValidator/testing/jmeter

# Run tests
jmeter -n -t StockValidator_API_Tests.jmx \
  -l results/results.jtl \
  -e -o results/html-report

# View HTML report
open results/html-report/index.html
```

---

## 📊 Expected Results

### What Should Happen:

1. **setUp Thread Group** (runs once):
   - ✅ Health Check (200 OK)
   - ✅ Register Admin User (201 Created)
   - ✅ Login Admin User (200 OK, extracts tokens)
   - ✅ Register Regular User (201 Created)
   - ✅ Login Regular User (200 OK, extracts tokens)

2. **Admin Operations Thread Group**:
   - ✅ Get Admin Profile (200 OK)
   - ✅ Refresh Admin Token (200 OK)

3. **User Operations Thread Group**:
   - ✅ Get User Profile (200 OK)
   - ✅ Refresh User Token (200 OK)

4. **Error Scenarios Thread Group**:
   - ✅ Wrong Password (401 Unauthorized)
   - ✅ No Token (403 Forbidden)
   - ✅ Invalid Token (401 Unauthorized)

**Total: 13 requests, all should pass ✅**

---

## 🐛 Troubleshooting

### Error: "Connection refused"

**Cause:** Auth service not running  
**Fix:**
```bash
# Check if service is running
lsof -i :8001

# If not, start it
cd backend/services/auth
source ../../venv/bin/activate
python main.py
```

### Error: "Database connection failed"

**Cause:** Docker not running  
**Fix:**
```bash
# Start Docker services
cd backend
docker-compose up -d postgres redis

# Check they're running
docker ps | grep stockvalidator
```

### Error: "Port 8001 already in use"

**Fix:**
```bash
# Kill process on port 8001
lsof -ti:8001 | xargs kill -9

# Or kill all Python main.py processes
pkill -f "python main.py"
```

### Tests Fail: "401 Unauthorized"

**Cause:** Tokens expired or setUp didn't run  
**Fix:** Re-run entire test plan (not individual tests)

---

## 🎯 Quick Test Commands

### 1. Start Everything
```bash
# One-liner to start all services
cd /Users/mmisbahuddin/Documents/Personal_work/StockValidator/backend && \
docker-compose up -d && sleep 5 && \
cd services/auth && source ../../venv/bin/activate && \
python main.py &

# Wait for service to start
sleep 3
```

### 2. Run JMeter (GUI)
```bash
cd /Users/mmisbahuddin/Documents/Personal_work/StockValidator/testing/jmeter
jmeter -t StockValidator_API_Tests.jmx
```

### 3. Stop Everything
```bash
# Stop Auth service
pkill -f "python main.py"

# Stop Docker
cd /Users/mmisbahuddin/Documents/Personal_work/StockValidator/backend
docker-compose down
```

---

## 📈 Load Testing

To test with multiple users:

1. Open in JMeter GUI
2. Select "Phase 2 - Auth Service: User Operations"
3. Set properties:
   - **Number of threads:** 10 (10 concurrent users)
   - **Ramp-up period:** 5 (start all 10 in 5 seconds)
   - **Loop count:** 5 (each user runs 5 times)
4. Run

**Result:** 10 users × 5 loops = 50 total test executions

---

## ✅ Verification Checklist

Before running JMeter, verify:

- [ ] Docker is running (`docker ps`)
- [ ] PostgreSQL is accessible (port 5433)
- [ ] Redis is accessible (port 6379)
- [ ] Auth service is running (port 8001)
- [ ] Health check works (`curl http://localhost:8001/health`)

---

## 📝 Notes

- **setUp runs once** - Creates users and extracts tokens
- **Thread Groups run N times** - Based on your settings
- **Tokens are reused** - No need to login for each test
- **Error scenarios are expected to fail** - They test negative cases (401, 403)

---

**Ready to test! 🚀**

Last Updated: November 3, 2025

