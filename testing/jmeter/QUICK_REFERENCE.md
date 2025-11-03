# JMeter Variable Sharing - Quick Reference Card

## 🎯 6 Shared Variables Available to All Thread Groups

```
┌──────────────────────────────────────────────────────────────┐
│  ADMIN VARIABLES                                             │
├──────────────────────────────────────────────────────────────┤
│  ${__P(admin_username)}        → Admin username              │
│  ${__P(admin_access_token)}    → Admin JWT access token      │
│  ${__P(admin_refresh_token)}   → Admin JWT refresh token     │
├──────────────────────────────────────────────────────────────┤
│  USER VARIABLES                                              │
├──────────────────────────────────────────────────────────────┤
│  ${__P(user_username)}         → User username               │
│  ${__P(user_access_token)}     → User JWT access token       │
│  ${__P(user_refresh_token)}    → User JWT refresh token      │
└──────────────────────────────────────────────────────────────┘
```

---

## 📋 Usage Examples

### Authorization Header
```xml
<HeaderManager>
  <collectionProp name="HeaderManager.headers">
    <elementProp name="" elementType="Header">
      <stringProp name="Header.name">Authorization</stringProp>
      <stringProp name="Header.value">Bearer ${__P(admin_access_token)}</stringProp>
    </elementProp>
  </collectionProp>
</HeaderManager>
```

### Request Body
```xml
<elementProp name="" elementType="HTTPArgument">
  <stringProp name="Argument.value">{
  "refresh_token": "${__P(admin_refresh_token)}"
}</stringProp>
</elementProp>
```

### URL Parameter
```xml
<stringProp name="HTTPSampler.path">/users/${__P(admin_username)}</stringProp>
```

---

## ⚠️ Common Mistakes

### ❌ WRONG - Using Variables (Thread-Local)
```xml
Bearer ${admin_access_token}
```
**Problem:** Only works in the same thread where it was extracted

### ✅ CORRECT - Using Properties (Global)
```xml
Bearer ${__P(admin_access_token)}
```
**Solution:** Works in ALL threads

---

## 🔍 Debug Commands

### Check Properties in JMeter Log
```bash
grep "saved" testing/jmeter/jmeter.log
```

### View Test Results
```bash
cat testing/jmeter/results/results.jtl | grep -v "^timeStamp" | awk -F',' '{print $3, "→", $4}'
```

### Open HTML Report
```bash
open testing/jmeter/results/html-report/index.html
```

---

## 🚀 Quick Test Commands

### Run Tests (CLI)
```bash
cd testing/jmeter
jmeter -n -t StockValidator_API_Tests.jmx -l results/results.jtl -e -o results/html-report
```

### Run Tests (GUI)
```bash
cd testing/jmeter
jmeter -t StockValidator_API_Tests.jmx
# Click Play button ▶️
```

---

## 📊 Expected Test Results

```
✅ setUp Thread Group (6 requests)
   - Health Check
   - Register Admin + Extract username
   - Login Admin + Extract tokens
   - Register User + Extract username
   - Login User + Extract tokens
   - Debug Sampler

✅ Admin Operations (2 requests)
   - Get Admin Profile (uses admin_access_token)
   - Refresh Admin Token (uses admin_refresh_token)

✅ User Operations (2 requests)
   - Get User Profile (uses user_access_token)
   - Refresh User Token (uses user_refresh_token)

✅ Error Scenarios (3 expected errors)
   - Wrong Password → 401 ✅
   - No Token → 403 ✅
   - Invalid Token → 401 ✅
```

**Total: 14 requests (11 pass, 3 expected errors)**

---

## 💡 Key Concepts

| Concept | Description | Syntax |
|---------|-------------|--------|
| **Variable** | Thread-local | `${variable_name}` |
| **Property** | Global (all threads) | `${__P(property_name)}` |
| **Extract** | JSONPostProcessor | Extracts from JSON response |
| **Convert** | JSR223PostProcessor | `props.put("name", vars.get("name"))` |

---

## 🎯 How Properties Work

```
setUp Thread Group (Thread 1)
    ↓
Extract variable: admin_username = "admin_123"
    ↓
Convert to property: props.put("admin_username", "admin_123")
    ↓
┌─────────────────────────────────────────────────────┐
│  JMeter Properties (Global Storage)                 │
│  ├─ admin_username = "admin_123"                    │
│  ├─ admin_access_token = "eyJ..."                   │
│  └─ admin_refresh_token = "eyJ..."                  │
└─────────────────────────────────────────────────────┘
    ↓                    ↓                    ↓
Thread 2          Thread 3          Thread 4
Admin Ops         User Ops      Error Scenarios
Can access!       Can access!       Can access!
```

---

## 📚 Full Documentation

- **Comprehensive Guide:** `VARIABLE_SHARING_GUIDE.md`
- **Test Structure:** `STRUCTURE.md`
- **Run Instructions:** `RUN_TESTS.md`
- **Fixes Applied:** `JMETER_TESTS_FIXED.md`

---

**Quick Help:** Need to share a new variable? See `VARIABLE_SHARING_GUIDE.md` → "Adding New Shared Variables"

