# Quick Test Commands Reference

## Stock Service Unit Tests

### Run All Tests
```bash
cd backend/services/stock
source ../../venv/bin/activate
pytest tests/ -v
```

### Run Specific Test Files
```bash
# Ticker Validator Tests
pytest tests/test_ticker_validator.py -v

# Rate Limiter Tests  
pytest tests/test_rate_limiter.py -v

# Stock Service Tests
pytest tests/test_stock_service.py -v

# Endpoint Tests
pytest tests/test_stock_endpoints.py -v
```

### Run with Coverage Report
```bash
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html  # View coverage report
```

---

## JMeter Integration Tests

### GUI Mode (Recommended)
```bash
cd testing/jmeter
jmeter -t StockValidator_API_Tests.jmx
```

Then in JMeter GUI:
1. Right-click "🏁 setUp Thread Group" → Start
2. Right-click "📦 Stock Service - Admin Operations" → Start  
3. Right-click "🔍 User Search & Rate Limiting" → Start
4. Right-click "⚙️ Admin Rate Limit Management" → Start
5. Click "View Results Tree" to see results

### CLI Mode (For CI/CD - has emoji parsing issues currently)
```bash
cd testing/jmeter
jmeter -n -t StockValidator_API_Tests.jmx \
  -l results/test_results.jtl \
  -e -o results/html_report
```

---

## Auth Service Unit Tests

```bash
cd backend/services/auth
source ../../venv/bin/activate
pytest tests/ -v
```

---

## Run All Project Tests

```bash
# From project root
cd backend
source venv/bin/activate

# Auth tests
cd services/auth && pytest tests/ -v && cd ../..

# Stock tests  
cd services/stock && pytest tests/ -v && cd ../..
```

---

## Test Status

- **Auth Service**: 22/22 tests passing ✅
- **Stock Service**: 18/37 tests passing (49% - mocking refinement needed)
- **JMeter Tests**: 24+ scenarios ✅
- **API Coverage**: 16/16 endpoints (100%) ✅

---

## Documentation

- `TESTING_STATUS.md` - Comprehensive testing summary
- `STOCK_SERVICE_TESTING.md` - Manual testing guide
- `testing/jmeter/README.md` - JMeter documentation

