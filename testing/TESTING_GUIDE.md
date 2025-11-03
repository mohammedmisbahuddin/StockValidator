# StockValidator Testing Guide

Complete testing strategy and tools for the StockValidator application.

## Overview

We use a multi-layered testing approach:

1. **Unit Tests** - Test individual functions and components
2. **Integration Tests** - Test API endpoints and services
3. **E2E Tests** - Test complete user flows
4. **Load Tests** - Test performance under load (JMeter)
5. **Manual Tests** - Quick verification scripts

---

## 1. Unit & Integration Tests (Pytest)

### Auth Service Tests

**Location:** `backend/services/auth/tests/`

**Run Tests:**
```bash
cd backend/services/auth
source ../../venv/bin/activate

# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_auth_utils.py -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

**Test Coverage:**
- ✅ Password hashing (bcrypt)
- ✅ JWT token generation/validation
- ✅ User registration
- ✅ Authentication
- ✅ Token refresh
- ✅ Error handling

**Test Files:**
- `test_auth_utils.py` - Password & JWT utilities (18 tests)
- `test_auth_service.py` - Business logic (service layer)
- `test_auth_endpoints.py` - API endpoints

---

## 2. E2E Integration Tests (Bash Scripts)

### Comprehensive Auth Test

**Location:** `backend/services/auth/test_comprehensive.sh`

**Run:**
```bash
cd backend/services/auth
./test_comprehensive.sh
```

**Coverage:**
- ✅ Health check
- ✅ Admin & user registration
- ✅ Login flows
- ✅ Profile retrieval
- ✅ Token refresh
- ✅ Error scenarios

**Results:** 10/10 tests passing

---

## 3. Load & Performance Tests (JMeter)

### JMeter Test Plan

**Location:** `testing/jmeter/StockValidator_API_Tests.jmx`

**Quick Start:**
```bash
# Install JMeter (macOS)
brew install jmeter

# Run GUI mode (for development/debugging)
jmeter -t testing/jmeter/StockValidator_API_Tests.jmx

# Run CLI mode (for CI/CD)
jmeter -n -t testing/jmeter/StockValidator_API_Tests.jmx \
  -l testing/jmeter/results/results.jtl \
  -e -o testing/jmeter/results/html-report
```

**Current Test Scenarios:**
1. Auth Service - User Registration Flow
2. Auth Service - Regular User Flow  
3. Auth Service - Error Scenarios

**Features:**
- Automatic token extraction & reuse
- Response assertions
- Unique test data generation (`${__time()}`)
- Summary reports & graphs
- HTML dashboard

**Performance Benchmarks:**
- Registration: 200-300ms
- Login: 150-250ms
- Token refresh: 100-150ms
- Get user: 50-100ms

### Load Testing

```bash
# Modify thread group settings in GUI or CLI
jmeter -n -t testing/jmeter/StockValidator_API_Tests.jmx \
  -Jthreads=100 \    # 100 concurrent users
  -Jrampup=10 \      # 10 second ramp-up
  -Jloops=10 \       # 10 iterations per user
  -l testing/jmeter/results/load_test.jtl \
  -e -o testing/jmeter/results/load_report
```

**View Results:**
Open `testing/jmeter/results/html-report/index.html` in browser

---

## 4. Manual API Testing

### Using cURL

```bash
# Start Auth Service
cd backend/services/auth
source ../../venv/bin/activate
python main.py &

# Health Check
curl http://localhost:8001/health

# Register User
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"test","password":"Test123","role":"user"}'

# Login
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"Test123"}'

# Get Current User (replace TOKEN)
curl http://localhost:8001/auth/me \
  -H "Authorization: Bearer TOKEN"
```

### Using FastAPI Swagger UI

Navigate to: `http://localhost:8001/docs`

Interactive API documentation with "Try it out" buttons.

---

## 5. Database Testing

### Connection Test

```bash
cd backend
source venv/bin/activate
python test_connections.py
```

Tests PostgreSQL and Redis connectivity.

### Manual Database Queries

```bash
# Connect to PostgreSQL
docker exec -it stockvalidator-postgres psql -U stockadmin -d stockvalidator

# Check users
\c stockvalidator
\dn
SELECT * FROM auth_schema.users;

# Check Redis
docker exec -it stockvalidator-redis redis-cli
KEYS *
```

---

## Testing Workflow for New Features

When adding new APIs or services, follow this process:

### Step 1: Write Unit Tests First
```bash
# Create test file
touch backend/services/new_service/tests/test_new_feature.py

# Write tests
# - Test individual functions
# - Test edge cases
# - Test error conditions

# Run tests
pytest tests/test_new_feature.py -v
```

### Step 2: Write Integration Tests
```bash
# Add to test_endpoints.py
# - Test API endpoints
# - Test request/response
# - Test authentication
# - Test validation

pytest tests/test_endpoints.py -v
```

### Step 3: Add to E2E Script
```bash
# Update comprehensive test script
# - Add new user flow
# - Test end-to-end scenarios

./test_comprehensive.sh
```

### Step 4: Add to JMeter
```bash
# Open JMeter GUI
jmeter -t testing/jmeter/StockValidator_API_Tests.jmx

# Add new Thread Group for new service
# Add HTTP Samplers for each endpoint
# Add assertions
# Extract variables as needed

# Test in GUI mode
# Save and commit
```

### Step 5: Document
```bash
# Update TEST_SUMMARY.md
# Update service README.md
# Update this guide if needed
```

---

## Test Data Management

### Database Cleanup

After testing, you may want to clean up test data:

```bash
# Drop and recreate database
docker exec stockvalidator-postgres psql -U stockadmin -d postgres -c "DROP DATABASE stockvalidator;"
docker exec stockvalidator-postgres psql -U stockadmin -d postgres -c "CREATE DATABASE stockvalidator;"

# Restart services to recreate tables
cd backend/services/auth
python main.py
```

### Redis Cleanup

```bash
docker exec stockvalidator-redis redis-cli FLUSHALL
```

---

## Continuous Integration

### GitHub Actions (Future)

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  pytest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Pytest
        run: |
          cd backend/services/auth
          pip install -r requirements.txt -r requirements-test.txt
          pytest tests/ -v --cov
  
  jmeter:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start Services
        run: docker-compose up -d
      - name: Run JMeter
        run: |
          # Install JMeter
          # Run tests
          # Upload reports
```

---

## Troubleshooting Tests

### Pytest Failures

**Issue:** Import errors
```bash
# Solution: Check PYTHONPATH
cd backend/services/auth
export PYTHONPATH="${PYTHONPATH}:../..:."
pytest tests/ -v
```

**Issue:** Database connection fails
```bash
# Solution: Check Docker
docker ps
docker logs stockvalidator-postgres
```

### JMeter Failures

**Issue:** Connection refused
```bash
# Solution: Check service is running
lsof -i :8001
curl http://localhost:8001/health
```

**Issue:** Token extraction fails
```bash
# Solution: Check JSON path expression
# View Results Tree → Response data
# Verify $.access_token exists
```

### E2E Script Failures

**Issue:** Service not starting
```bash
# Solution: Check for port conflicts
pkill -9 -f "python.*main.py"
lsof -ti:8001 | xargs kill -9
```

---

## Test Metrics & Reports

### Current Status (Phase 2 Complete)

**Unit Tests:** ✅ 18/18 passed
**Integration Tests:** ✅ 10/10 passed  
**E2E Tests:** ✅ All scenarios passing
**Load Tests:** ✅ Available via JMeter

**Coverage:**
- Auth Service: 100%
- Stock Service: TBD (Phase 3)
- Notification Service: TBD (Phase 4)

### Performance Metrics

**Response Times (p95):**
- Health check: <50ms
- Registration: <300ms
- Login: <250ms
- Token refresh: <150ms
- Get user: <100ms

**Throughput:**
- TBD after load testing

---

## Best Practices

1. **Test Early, Test Often**
   - Write tests alongside code
   - Run tests before committing

2. **Test Coverage**
   - Aim for >80% code coverage
   - Focus on critical paths

3. **Realistic Test Data**
   - Use realistic usernames, emails
   - Test with various input sizes

4. **Isolation**
   - Each test should be independent
   - Clean up test data

5. **Documentation**
   - Document test purpose
   - Keep test names descriptive

6. **Version Control**
   - Commit test code
   - Exclude test results from git

---

## Quick Reference

### Start Everything for Testing

```bash
# Terminal 1: Infrastructure
cd backend
docker-compose up -d postgres redis

# Terminal 2: Auth Service
cd backend/services/auth
source ../../venv/bin/activate
python main.py

# Terminal 3: Run Tests
cd backend/services/auth
source ../../venv/bin/activate

# Choose one:
pytest tests/ -v                    # Pytest
./test_comprehensive.sh             # E2E
jmeter -t ../../testing/jmeter/StockValidator_API_Tests.jmx  # JMeter GUI
```

### Stop Everything

```bash
pkill -f "python.*main.py"
docker-compose down
```

---

**Maintained by:** Development Team  
**Last Updated:** October 31, 2025  
**Next Review:** After Phase 3 completion

