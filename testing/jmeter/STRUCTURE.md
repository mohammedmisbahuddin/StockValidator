# JMeter Test Plan Structure

## 📋 Overview

The JMeter test plan is now properly structured using **setUp Thread Groups** and regular **Thread Groups** for optimal testing.

---

## 🏗️ Current Structure

```
StockValidator API Test Plan
│
├── 🔧 setUp Thread Group: Initialize Test Users & Tokens
│   ├── 1. Health Check
│   ├── 2. Register Admin User
│   ├── 3. Login Admin User (Extract admin tokens)
│   ├── 4. Register Regular User
│   └── 5. Login Regular User (Extract user tokens)
│
├── 🧪 Phase 2 - Auth Service: Admin Operations
│   ├── Get Admin Profile (uses admin_access_token)
│   └── Refresh Admin Access Token
│
├── 🧪 Phase 2 - Auth Service: User Operations
│   ├── Get User Profile (uses user_access_token)
│   └── Refresh User Access Token
│
├── ❌ Phase 2 - Auth Service: Error Scenarios
│   ├── Login with Wrong Password (Expect 401)
│   ├── Access Protected Endpoint without Token (Expect 403)
│   └── Access with Invalid Token (Expect 401)
│
├── 📝 [Phase 3 - Stock Service Tests - To Be Added]
│
└── 📊 Listeners
    ├── View Results Tree
    └── Summary Report
```

---

## ✨ Key Improvements

### 1. **setUp Thread Group** (Runs Once Before All Tests)
- **Purpose:** Initialize test data (users, tokens)
- **Runs:** Only ONCE at the start
- **On Error:** Stops entire test (stoptest)
- **Extracts:**
  - `admin_username`
  - `admin_access_token`
  - `admin_refresh_token`
  - `user_username`
  - `user_id`
  - `user_access_token`
  - `user_refresh_token`

### 2. **Regular Thread Groups** (Can Run Multiple Times)
- **Purpose:** Actual API tests
- **Runs:** Can loop, scale to multiple users
- **On Error:** Continue to next request
- **Uses:** Tokens extracted in setUp

### 3. **Proper Separation**
- ✅ Initialization (setUp) vs Testing (Thread Groups)
- ✅ Happy path vs Error scenarios
- ✅ Admin operations vs User operations

---

## 🎯 How to Use

### Run All Tests
```bash
# GUI Mode
jmeter -t StockValidator_API_Tests.jmx

# CLI Mode
jmeter -n -t StockValidator_API_Tests.jmx \
  -l results/results.jtl \
  -e -o results/html-report
```

### Run Specific Thread Group Only

**In GUI:**
1. Right-click on specific Thread Group (e.g., "Phase 2 - Auth Service: User Operations")
2. Click "Start" (not the global play button)
3. Only that group + setUp will run

**In CLI:**
```bash
jmeter -n -t StockValidator_API_Tests.jmx \
  -Jjmeterengine.threadstop.wait=5000 \
  -l results/results.jtl
```

### Load Testing (Multiple Users)

**Modify Thread Group properties:**
- Number of threads: `10` (10 concurrent users)
- Ramp-up period: `5` (5 seconds to start all)
- Loop count: `10` (each user runs 10 times)

**Result:** setUp runs once, then 10 users each perform 10 test iterations = 100 total test runs

---

## 🔄 Test Flow

### Execution Order:

```
1. setUp Thread Group
   └── Runs ONCE, creates users, extracts tokens
       ↓
2. Phase 2 - Admin Operations
   └── Runs N times (based on threads/loops)
   └── Uses admin_access_token
       ↓
3. Phase 2 - User Operations
   └── Runs N times (based on threads/loops)
   └── Uses user_access_token
       ↓
4. Phase 2 - Error Scenarios
   └── Runs N times (based on threads/loops)
   └── Tests negative cases
```

---

## 📊 Variables Available for All Tests

After setUp completes, these variables are available:

| Variable | Description | Usage |
|----------|-------------|-------|
| `${admin_username}` | Admin username | Login, references |
| `${admin_access_token}` | Admin JWT token | Authorization header |
| `${admin_refresh_token}` | Admin refresh token | Token refresh |
| `${user_username}` | User username | Login, references |
| `${user_id}` | User ID (UUID) | User operations |
| `${user_access_token}` | User JWT token | Authorization header |
| `${user_refresh_token}` | User refresh token | Token refresh |

**Usage Example:**
```
Authorization: Bearer ${admin_access_token}
```

---

## 🆕 Adding Phase 3 Tests

When implementing Stock Service, add new Thread Groups:

### Example: Stock Service Tests

```xml
<ThreadGroup testname="Phase 3 - Stock Service: Admin Stock Management">
  <!-- Admin adds/edits/deletes stocks -->
  <HTTPSamplerProxy testname="Add Stock">
    <!-- Uses ${admin_access_token} -->
  </HTTPSamplerProxy>
</ThreadGroup>

<ThreadGroup testname="Phase 3 - Stock Service: User Stock Search">
  <!-- User searches for stocks -->
  <HTTPSamplerProxy testname="Search Valid Stock">
    <!-- Uses ${user_access_token} -->
  </HTTPSamplerProxy>
</ThreadGroup>
```

Add these **AFTER** Phase 2 thread groups, **BEFORE** listeners.

---

## 🎨 Color-Coded in JMeter GUI

When you open in JMeter GUI:

- **Green triangle** (setUp) - Runs first, initialization
- **Blue circle** (Thread Group) - Regular tests
- **Purple icon** (Listeners) - Results viewers

---

## 📈 Performance Testing

### Example: Test with 100 Concurrent Users

1. Open `Phase 2 - Auth Service: User Operations`
2. Set properties:
   ```
   Number of Threads: 100
   Ramp-Up Period: 10
   Loop Count: 5
   ```
3. Run test
4. View Summary Report:
   - Throughput: Requests/sec
   - Average response time
   - Error %

---

## ✅ Best Practices Implemented

1. **setUp for Initialization** ✅
   - Users created once
   - Tokens extracted once
   - Reused across all tests

2. **Thread Groups for Tests** ✅
   - Can scale independently
   - Each group represents a test suite
   - Can enable/disable individually

3. **Error Handling** ✅
   - setUp stops on error (critical)
   - Tests continue on error (informative)

4. **Assertions** ✅
   - Response code assertions
   - JSON path assertions for roles
   - Clear error messages

5. **Token Management** ✅
   - Extracted once in setUp
   - Available to all thread groups
   - Used in Authorization headers

6. **Naming Convention** ✅
   - Prefixed with phase number
   - Clear descriptions
   - Grouped by service

7. **Comments & Documentation** ✅
   - Section markers
   - Clear purpose statements
   - Instructions for Phase 3

---

## 🐛 Troubleshooting

### Issue: Tokens not found in tests
**Cause:** setUp didn't run  
**Solution:** Always run entire test plan, not individual samplers

### Issue: Tests fail with 401 Unauthorized
**Cause:** Tokens may have expired  
**Solution:** Re-run entire test plan to regenerate tokens

### Issue: Duplicate username error
**Cause:** Re-running setUp with same timestamp  
**Solution:** Wait 1 second between runs, or clean database

---

## 📚 Next Steps

After completing Phase 3 (Stock Service):

1. Add setUp steps (if needed) for stock initialization
2. Create new Thread Groups:
   - "Phase 3 - Stock Service: Admin Stock Management"
   - "Phase 3 - Stock Service: User Stock Search"
   - "Phase 3 - Stock Service: Rate Limiting Tests"
3. Extract stock IDs as variables (like tokens)
4. Update this documentation

---

**Last Updated:** November 3, 2025  
**Current Phase:** 2 (Auth Service) - Complete  
**Next Phase:** 3 (Stock Service) - Ready to append

