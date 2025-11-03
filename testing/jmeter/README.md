# JMeter Testing for StockValidator

This directory contains JMeter test plans for load testing and API verification.

## Overview

The JMeter test plan (`StockValidator_API_Tests.jmx`) contains comprehensive test scenarios for all microservices. We continuously append new APIs and user flows as they are developed.

## Current Coverage

### Phase 2: Authentication Service ✅
- Health check
- Admin user registration & login
- Regular user registration & login
- Get current user profile
- Token refresh
- Error scenarios (wrong password, missing token)

### Phase 3: Stock Service ✅
**Admin Operations:**
- Validate ticker (AAPL) with yfinance/Finnhub
- Create stock (AAPL - Ready/Pullback1)
- Create stock (MSFT - Near)
- Get all stocks grouped by category
- Update stock category (AAPL: Ready → Near)
- Get specific stock (MSFT)

**User Search & Rate Limiting:**
- Search valid stock in system (AAPL) - limit decremented
- Search valid stock not in system (GOOGL) - limit decremented
- Search invalid stock (INVALID123) - no limit decrement
- View remaining searches after each search

**Admin Rate Limit Management:**
- Get user rate limit info
- Update user rate limit (100 searches)
- Reset individual user limit
- Reset all user limits
- Set universal rate limit (50 searches)

## Prerequisites

### Install JMeter

**macOS:**
```bash
brew install jmeter
```

**Windows:**
1. Download from https://jmeter.apache.org/download_jmeter.cgi
2. Extract and add to PATH

**Linux:**
```bash
wget https://downloads.apache.org//jmeter/binaries/apache-jmeter-5.6.3.tgz
tar -xzf apache-jmeter-5.6.3.tgz
export PATH=$PATH:/path/to/apache-jmeter-5.6.3/bin
```

### Start Services

Before running tests, ensure all services are running:

```bash
# Start infrastructure
docker-compose up -d postgres redis

# Start Auth Service (Port 8001)
cd backend/services/auth
source ../../venv/bin/activate
python main.py &

# Start Stock Service (Port 8002)
cd backend/services/stock
source ../../venv/bin/activate
python main.py &

# Verify services are running
curl http://localhost:8001/health
curl http://localhost:8002/health
```

## Running Tests

### Option 1: GUI Mode (Recommended for Development)

```bash
jmeter -t testing/jmeter/StockValidator_API_Tests.jmx
```

This opens the JMeter GUI where you can:
- View test structure
- Run individual test groups
- See real-time results
- Debug failures

### Option 2: Command Line Mode (CI/CD)

```bash
# Run all tests
jmeter -n -t testing/jmeter/StockValidator_API_Tests.jmx \
  -l testing/jmeter/results/results.jtl \
  -e -o testing/jmeter/results/html-report

# Run specific thread group
jmeter -n -t testing/jmeter/StockValidator_API_Tests.jmx \
  -l testing/jmeter/results/results.jtl \
  -Jthread_group="Auth Service - User Registration Flow"
```

### Option 3: Load Testing

Modify thread group properties for load testing:

```bash
# Edit the .jmx file or use GUI to set:
# - Number of threads: 100 (concurrent users)
# - Ramp-up period: 10 (seconds)
# - Loop count: 10 (iterations per user)

jmeter -n -t testing/jmeter/StockValidator_API_Tests.jmx \
  -Jthreads=100 -Jrampup=10 -Jloops=10 \
  -l testing/jmeter/results/load_test.jtl \
  -e -o testing/jmeter/results/load_report
```

## Test Structure

### Thread Groups
Each thread group represents a user flow:

**Authentication (Phase 2):**
1. **🏁 setUp Thread Group (Runs First)**
   - Register admin & user
   - Extract tokens and user IDs
   - Share globally across all tests

2. **👤 Admin Operations**
   - Get current user
   - Refresh token

3. **👥 User Operations**
   - Get user profile

4. **❌ Error Scenarios**
   - Wrong password
   - Missing authentication token

**Stock Service (Phase 3):**
5. **📦 Stock Service - Admin Operations**
   - Validate ticker
   - Create stocks (AAPL, MSFT)
   - Get all stocks (grouped)
   - Update stock category
   - Get specific stock

6. **🔍 Stock Service - User Search & Rate Limiting**
   - Search stock in system
   - Search valid ticker not in system
   - Search invalid ticker (no limit decrement)

7. **⚙️ Stock Service - Admin Rate Limit Management**
   - Get user rate limit info
   - Update user limit
   - Reset individual user
   - Reset all users
   - Set universal limit

### Variables
Configurable test parameters:

**Service Endpoints:**
```
AUTH_HOST=localhost
AUTH_PORT=8001
STOCK_HOST=localhost (port 8002 hardcoded in requests)
PROTOCOL=http
```

**Global Properties (Shared Across Thread Groups):**
```
admin_username, admin_access_token, admin_refresh_token, admin_id
user_username, user_access_token, user_refresh_token, user_id
```

To change variables, edit them in the Test Plan or pass via command line:

```bash
jmeter -n -t StockValidator_API_Tests.jmx \
  -JAUTH_HOST=staging.example.com \
  -JAUTH_PORT=443 \
  -JPROTOCOL=https
```

## Interpreting Results

### GUI Mode
- **View Results Tree**: See individual request/response details
- **Summary Report**: View aggregate statistics
- **Graph Results**: Visualize response times

### Command Line Reports
After running in CLI mode, open `results/html-report/index.html` in a browser.

Key metrics to monitor:
- **Response Time (ms)**: Should be < 500ms for most APIs
- **Throughput**: Requests per second
- **Error %**: Should be 0% for functional tests
- **90th Percentile**: 90% of requests faster than this

### Success Criteria
✅ All assertions pass (HTTP status codes match expected)
✅ Error rate = 0%
✅ Average response time < 500ms (Auth APIs)
✅ 95th percentile < 1000ms

## Adding New APIs (Phase 3 and Beyond)

When developing new services, add tests following this pattern:

### 1. Add Thread Group

```xml
<ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Stock Service - Stock Management Flow" enabled="true">
  <!-- Thread configuration -->
</ThreadGroup>
```

### 2. Add HTTP Samplers

```xml
<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="Add New Stock" enabled="true">
  <!-- Request configuration -->
</HTTPSamplerProxy>
```

### 3. Add Assertions

```xml
<ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Response Assertion" enabled="true">
  <!-- Expected status code -->
</ResponseAssertion>
```

### 4. Extract Variables (if needed)

```xml
<JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="Extract Stock ID" enabled="true">
  <stringProp name="JSONPostProcessor.referenceNames">stock_id</stringProp>
  <stringProp name="JSONPostProcessor.jsonPathExprs">$.id</stringProp>
</JSONPostProcessor>
```

## Troubleshooting

### Issue: Connection Refused
**Solution:** Ensure services are running on correct ports
```bash
lsof -i :8001  # Check Auth service
```

### Issue: Authentication Failures
**Solution:** Check token extraction and usage
- View Results Tree → Show request headers
- Verify `Authorization: Bearer ${token}` is present

### Issue: Timeouts
**Solution:** Increase timeout in HTTP Sampler
```xml
<stringProp name="HTTPSampler.connect_timeout">5000</stringProp>
<stringProp name="HTTPSampler.response_timeout">10000</stringProp>
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: API Load Tests

on: [push, pull_request]

jobs:
  jmeter-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Start Services
        run: |
          docker-compose up -d
          # Wait for services to be ready
          sleep 10
      
      - name: Install JMeter
        run: |
          wget https://downloads.apache.org//jmeter/binaries/apache-jmeter-5.6.3.tgz
          tar -xzf apache-jmeter-5.6.3.tgz
      
      - name: Run Tests
        run: |
          apache-jmeter-5.6.3/bin/jmeter -n \
            -t testing/jmeter/StockValidator_API_Tests.jmx \
            -l results.jtl \
            -e -o report
      
      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: jmeter-report
          path: report/
```

## Best Practices

1. **Unique Test Data**: Use `${__time()}` for unique usernames/emails
2. **Variable Extraction**: Extract IDs and tokens for dependent requests
3. **Assertions**: Always add response code and content assertions
4. **Error Handling**: Test both success and failure paths
5. **Cleanup**: Consider adding teardown thread group to clean test data
6. **Comments**: Document complex test scenarios
7. **Modular Design**: Group related requests in thread groups
8. **Realistic Load**: Base thread counts on expected production traffic

## Performance Benchmarks

### Auth Service (Baseline)
- Registration: ~200-300ms
- Login: ~150-250ms
- Token refresh: ~100-150ms
- Get user: ~50-100ms

### Stock Service (Phase 3)
- Ticker validation: ~500-1500ms (depends on yfinance/Finnhub API)
- Create stock: ~100-200ms
- Get all stocks: ~50-150ms
- Update stock: ~100-200ms
- User search: ~100-300ms
- Rate limit operations: ~50-100ms

**Note:** Ticker validation times vary based on external API response times.

## Version History

- **v1.0** (2025-10-31): Initial Auth Service tests
- **v2.0** (2025-11-03): ✅ Added Stock Service tests (Admin ops, User search, Rate limiting)
- **v3.0** (TBD): Add Notification Service tests

---

**Last Updated:** November 3, 2025  
**Services Covered:** Authentication (Phase 2) + Stock Service (Phase 3)  
**Total Test Scenarios:** 24+  
**Thread Groups:** 7  
**Endpoints Tested:** 20+

