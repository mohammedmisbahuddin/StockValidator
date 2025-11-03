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

### Phase 3: Stock Service (To be added)
- Will be appended after Phase 3 development

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
cd backend
docker-compose up -d postgres redis

# Start Auth Service
cd backend/services/auth
source ../../venv/bin/activate
python main.py &
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

1. **Auth Service - User Registration Flow**
   - Health check
   - Register admin
   - Login admin
   - Get current admin user
   - Refresh token

2. **Auth Service - Regular User Flow**
   - Register regular user
   - Login regular user
   - Get user profile

3. **Auth Service - Error Scenarios**
   - Wrong password
   - Missing authentication token

### Variables
Configurable test parameters:

```
AUTH_HOST=localhost
AUTH_PORT=8001
PROTOCOL=http
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

These will be updated as we add more services and optimize.

## Version History

- **v1.0** (2025-10-31): Initial Auth Service tests
- **v2.0** (TBD): Add Stock Service tests
- **v3.0** (TBD): Add Notification Service tests

---

**Last Updated:** October 31, 2025
**Services Covered:** Authentication (Phase 2)
**Total Test Scenarios:** 10+

