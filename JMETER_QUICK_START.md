# JMeter Quick Start Guide

Fast guide to get you testing with JMeter in 5 minutes.

## 1. Install JMeter

### macOS
```bash
brew install jmeter
```

### Windows
Download from: https://jmeter.apache.org/download_jmeter.cgi  
Extract and add `bin` folder to PATH

### Linux
```bash
sudo apt install jmeter
```

## 2. Start Your Services

```bash
# Start infrastructure
cd backend
docker-compose up -d

# Start Auth Service
cd backend/services/auth
source ../../venv/bin/activate
python main.py &
```

**Verify:** Visit `http://localhost:8001/health`

## 3. Run JMeter Tests

### Option A: GUI Mode (Recommended for First Time)

```bash
cd testing/jmeter
jmeter -t StockValidator_API_Tests.jmx
```

**In JMeter GUI:**
1. Click the green "Play" button (Start)
2. Watch tests run in real-time
3. Click "View Results Tree" to see requests/responses
4. Click "Summary Report" to see statistics

### Option B: Command Line (For Automation)

```bash
cd testing/jmeter

# Run all tests
jmeter -n -t StockValidator_API_Tests.jmx \
  -l results/results.jtl \
  -e -o results/html-report

# View report
open results/html-report/index.html  # macOS
# OR
xdg-open results/html-report/index.html  # Linux
# OR
start results/html-report/index.html  # Windows
```

## 4. Understanding Results

### What to Look For

✅ **Good:**
- All tests green (passed)
- Error % = 0
- Response times < 500ms

❌ **Bad:**
- Red tests (failed)
- Error % > 0
- Response times > 2000ms

### Key Metrics

| Metric | Description | Good Target |
|--------|-------------|-------------|
| Samples | # of requests executed | Depends on test |
| Average | Average response time | < 500ms |
| Min | Fastest response | < 100ms |
| Max | Slowest response | < 1000ms |
| Error % | Failed requests | 0% |
| Throughput | Requests/sec | Higher is better |

## 5. Common Tasks

### Test Specific Flow Only

In GUI:
- Right-click on thread group
- Click "Start" (starts only that group)

### Change Load (Concurrent Users)

In GUI:
1. Click on Thread Group
2. Change "Number of Threads (users)"
3. Change "Ramp-Up Period (seconds)"
4. Run test

Example:
- Threads: 100 (100 concurrent users)
- Ramp-Up: 10 (start all 100 within 10 seconds)
- Loop: 5 (each user runs 5 times)

### Test Different Environment

Change variables at top of test plan:
- `AUTH_HOST` → Your server
- `AUTH_PORT` → Your port
- `PROTOCOL` → http or https

## 6. Load Testing Quick Recipe

```bash
# Start JMeter
jmeter -t StockValidator_API_Tests.jmx

# In GUI:
# 1. Select "Auth Service - User Registration Flow"
# 2. Change settings:
#    - Threads: 50
#    - Ramp-Up: 5
#    - Loop: 10
# 3. Click Play
# 4. Watch Summary Report
```

**Interpret:**
- If error % stays at 0% → System handles 50 concurrent users ✅
- If error % increases → System is overloaded ❌

## 7. Troubleshooting

### "Connection refused"
```bash
# Check service is running
curl http://localhost:8001/health

# If not, start it
cd backend/services/auth
python main.py &
```

### "Assertion failed"
- Check service is correct version
- Check test expectations match API responses
- View "Response data" in View Results Tree

### Tests passing but you want to verify manually
```bash
# Use cURL to test same endpoints
curl http://localhost:8001/health
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"Test123","role":"user"}'
```

## 8. Adding New APIs (Phase 3+)

When you build new services:

1. **Open JMeter GUI:**
   ```bash
   jmeter -t StockValidator_API_Tests.jmx
   ```

2. **Find the section marker:**
   ```
   <!-- PHASE 3: STOCK SERVICE TESTS (TO BE ADDED) -->
   ```

3. **Add new Thread Group:**
   - Right-click "Test Plan"
   - Add → Threads → Thread Group
   - Name it: "Stock Service - Stock Management Flow"

4. **Add HTTP Requests:**
   - Right-click Thread Group
   - Add → Sampler → HTTP Request
   - Fill in:
     - Server: `${AUTH_HOST}`
     - Port: `${STOCK_PORT}` (add variable first)
     - Method: POST/GET/PUT/DELETE
     - Path: /stocks/add
     - Body: JSON payload

5. **Add Assertions:**
   - Right-click HTTP Request
   - Add → Assertions → Response Assertion
   - Check status code (200, 201, etc.)

6. **Extract Variables (if needed):**
   - Right-click HTTP Request
   - Add → Post Processors → JSON Extractor
   - Extract IDs, tokens, etc.

7. **Save & Test:**
   - File → Save
   - Run your new thread group
   - Verify in View Results Tree

## 9. CI/CD Integration (Future)

Save this for later:

```bash
# Run in CI pipeline
jmeter -n -t StockValidator_API_Tests.jmx \
  -JAUTH_HOST=staging.myapp.com \
  -JAUTH_PORT=443 \
  -JPROTOCOL=https \
  -l results.jtl \
  -e -o report

# Check for failures
if grep -q "false" results.jtl; then
  echo "Tests failed!"
  exit 1
fi
```

## 10. Useful JMeter Functions

Use in your tests:

```
${__time()}           → Unix timestamp (unique IDs)
${__Random(1,100)}    → Random number
${__UUID()}           → UUID
${__base64Encode()}   → Base64 encode
${variable_name}      → Use extracted variable
```

Example:
```json
{
  "email": "user_${__time()}@test.com",
  "username": "user_${__time()}",
  "password": "Pass${__Random(1000,9999)}"
}
```

---

## Next Steps

1. ✅ Run the Auth Service tests
2. ✅ View the HTML report
3. ✅ Try increasing thread count
4. ⏳ Add Stock Service tests after Phase 3
5. ⏳ Set up automated runs

---

**Need Help?**
- Full guide: `testing/jmeter/README.md`
- Testing guide: `testing/TESTING_GUIDE.md`
- JMeter docs: https://jmeter.apache.org/usermanual/

**Ready to test! 🚀**

