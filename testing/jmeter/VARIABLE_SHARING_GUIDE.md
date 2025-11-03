# JMeter Variable Sharing Guide

**Date:** November 3, 2025  
**Status:** ✅ All Variables Shared Across Thread Groups

---

## 🎯 Overview

This guide explains how variables are extracted in the `setUp` thread group and made available to all other thread groups using **JMeter Properties**.

---

## 📋 Shared Variables (Properties)

All the following variables are extracted during setup and converted to **global properties** accessible by all thread groups:

### Admin User Properties

| Property Name | Source | Description | Usage |
|---------------|--------|-------------|-------|
| `admin_username` | Register Admin User | Admin username (timestamped) | `${__P(admin_username)}` |
| `admin_access_token` | Login Admin User | JWT access token for admin | `${__P(admin_access_token)}` |
| `admin_refresh_token` | Login Admin User | JWT refresh token for admin | `${__P(admin_refresh_token)}` |

### Regular User Properties

| Property Name | Source | Description | Usage |
|---------------|--------|-------------|-------|
| `user_username` | Register Regular User | User username (timestamped) | `${__P(user_username)}` |
| `user_access_token` | Login Regular User | JWT access token for user | `${__P(user_access_token)}` |
| `user_refresh_token` | Login Regular User | JWT refresh token for user | `${__P(user_refresh_token)}` |

---

## 🔧 How It Works

### 1. **Extraction (JSONPostProcessor)**

Variables are first extracted from JSON responses using `JSONPostProcessor`:

```xml
<JSONPostProcessor>
  <stringProp name="JSONPostProcessor.referenceNames">admin_username</stringProp>
  <stringProp name="JSONPostProcessor.jsonPathExprs">$.username</stringProp>
  <stringProp name="JSONPostProcessor.match_numbers">1</stringProp>
</JSONPostProcessor>
```

This creates a **thread-local variable** `admin_username`.

---

### 2. **Conversion to Property (JSR223PostProcessor)**

Immediately after extraction, we convert the thread-local variable to a **global property**:

```groovy
// Save admin username as global property
props.put("admin_username", vars.get("admin_username"))
log.info("Admin username saved: " + vars.get("admin_username"))
```

**Key Difference:**
- **`vars`** = Thread-local variables (only available in the same thread)
- **`props`** = Global properties (available to ALL threads)

---

### 3. **Usage in Other Thread Groups**

To use a shared property in another thread group, use the `${__P(property_name)}` function:

**❌ WRONG (uses thread-local variable):**
```xml
<stringProp name="Header.value">Bearer ${admin_access_token}</stringProp>
```

**✅ CORRECT (uses global property):**
```xml
<stringProp name="Header.value">Bearer ${__P(admin_access_token)}</stringProp>
```

---

## 📖 Complete Flow Example

### setUp Thread Group → Other Thread Groups

```
┌─────────────────────────────────────────────────────────────┐
│ setUp Thread Group (Runs ONCE before all tests)            │
├─────────────────────────────────────────────────────────────┤
│ 1. Register Admin User                                      │
│    └─ Extract: admin_username → Variable                    │
│    └─ Convert: admin_username → Property ✅                 │
│                                                              │
│ 2. Login Admin User                                         │
│    └─ Body: {"username": "${__P(admin_username)}", ...}     │
│    └─ Extract: admin_access_token → Variable                │
│    └─ Extract: admin_refresh_token → Variable               │
│    └─ Convert: admin_access_token → Property ✅             │
│    └─ Convert: admin_refresh_token → Property ✅            │
└─────────────────────────────────────────────────────────────┘
                           ↓
        ┌──────────────────┴────────────────────┐
        ↓                                        ↓
┌──────────────────────┐          ┌──────────────────────────┐
│ Admin Operations     │          │ User Operations          │
│ Thread Group         │          │ Thread Group             │
├──────────────────────┤          ├──────────────────────────┤
│ Get Admin Profile    │          │ Get User Profile         │
│ Authorization:       │          │ Authorization:           │
│ Bearer ${__P(...)}✅ │          │ Bearer ${__P(...)}✅     │
│                      │          │                          │
│ Refresh Admin Token  │          │ Refresh User Token       │
│ Body: {              │          │ Body: {                  │
│   "refresh_token":   │          │   "refresh_token":       │
│   "${__P(...)}"}✅   │          │   "${__P(...)}"}✅       │
└──────────────────────┘          └──────────────────────────┘
```

---

## 🎓 Best Practices

### ✅ DO:

1. **Extract first, convert immediately:**
   ```xml
   <JSONPostProcessor>...</JSONPostProcessor>
   <JSR223PostProcessor>
     props.put("var_name", vars.get("var_name"))
   </JSR223PostProcessor>
   ```

2. **Use `${__P(property_name)}` in other threads:**
   ```xml
   Bearer ${__P(admin_access_token)}
   ```

3. **Add logging for debugging:**
   ```groovy
   log.info("Admin username saved: " + vars.get("admin_username"))
   ```

4. **Use Debug Samplers to verify properties:**
   ```xml
   <DebugSampler>
     <boolProp name="displayJMeterProperties">true</boolProp>
   </DebugSampler>
   ```

### ❌ DON'T:

1. **Don't use thread-local variables across thread groups:**
   ```xml
   <!-- ❌ This won't work in other threads -->
   Bearer ${admin_access_token}
   ```

2. **Don't forget to convert extracted variables to properties:**
   ```xml
   <!-- ❌ Extraction alone isn't enough -->
   <JSONPostProcessor>...</JSONPostProcessor>
   <!-- Missing JSR223PostProcessor to convert to property -->
   ```

3. **Don't use complex property names with spaces:**
   ```groovy
   // ❌ Bad
   props.put("admin access token", token)
   
   // ✅ Good
   props.put("admin_access_token", token)
   ```

---

## 🔍 Debugging Variable Sharing

### Check if Property is Set

**Option 1: Debug Sampler**
- Add a Debug Sampler in your thread group
- Enable "Display JMeter Properties"
- Run tests and check the "Response data" tab

**Option 2: JSR223 Sampler**
```groovy
log.info("Admin Token: " + props.get("admin_access_token"))
log.info("User Token: " + props.get("user_access_token"))
```

**Option 3: Check jmeter.log**
```bash
grep "saved" jmeter.log
```

Expected output:
```
Admin username saved: admin_1762167873477
Admin tokens saved as properties
User username saved: user_1762167874229
User tokens saved as properties
```

---

## 📊 Current Test Results

**All Variables Successfully Shared!**

```
✅ 1. Health Check → 200
✅ 2. Register Admin User → 201
   └─ Extracted & Shared: admin_username ✅
✅ 3. Login Admin User (Extract Tokens) → 200
   └─ Uses: admin_username from property ✅
   └─ Extracted & Shared: admin_access_token ✅
   └─ Extracted & Shared: admin_refresh_token ✅
✅ 4. Register Regular User → 201
   └─ Extracted & Shared: user_username ✅
✅ 5. Login Regular User (Extract Tokens) → 200
   └─ Uses: user_username from property ✅
   └─ Extracted & Shared: user_access_token ✅
   └─ Extracted & Shared: user_refresh_token ✅
✅ 🔍 Debug Sampler (Verify Properties)
✅ 🔍 Debug Sampler (Other Thread Group Check)
✅ Get Admin Profile → 200
   └─ Uses: admin_access_token from property ✅
✅ Get User Profile → 200
   └─ Uses: user_access_token from property ✅
✅ Refresh Admin Access Token → 200
   └─ Uses: admin_refresh_token from property ✅
✅ Refresh User Access Token → 200
   └─ Uses: user_refresh_token from property ✅
```

**Total: 14 requests, 11 passed, 3 expected errors (security validation)**

---

## 🚀 Adding New Shared Variables

When you need to share a new variable across thread groups:

### Step 1: Extract the variable
```xml
<JSONPostProcessor>
  <stringProp name="JSONPostProcessor.referenceNames">new_variable</stringProp>
  <stringProp name="JSONPostProcessor.jsonPathExprs">$.field_name</stringProp>
  <stringProp name="JSONPostProcessor.match_numbers">1</stringProp>
</JSONPostProcessor>
```

### Step 2: Convert to property
```xml
<JSR223PostProcessor>
  <stringProp name="scriptLanguage">groovy</stringProp>
  <stringProp name="script">
    props.put("new_variable", vars.get("new_variable"))
    log.info("New variable saved: " + vars.get("new_variable"))
  </stringProp>
</JSR223PostProcessor>
```

### Step 3: Use in other threads
```xml
${__P(new_variable)}
```

---

## 📚 Reference: JMeter Functions

### Variable vs Property Functions

| Function | Scope | Usage | Example |
|----------|-------|-------|---------|
| `${variable}` | Thread-local | Same thread only | `${admin_username}` |
| `${__P(property)}` | Global | All threads | `${__P(admin_username)}` |
| `${__V(variable)}` | Variable eval | Dynamic variable names | `${__V(user_${id})}` |
| `${__setProperty(name,value)}` | Set property | Set during test | `${__setProperty(token,abc)}` |

### Groovy Access

| Object | Description | Example |
|--------|-------------|---------|
| `vars` | Thread-local variables | `vars.get("var")`, `vars.put("var", "val")` |
| `props` | Global properties | `props.get("prop")`, `props.put("prop", "val")` |
| `log` | Logger | `log.info("message")` |

---

## ✅ Summary

**6 Variables Shared Across All Thread Groups:**

1. ✅ `admin_username` - Admin's username
2. ✅ `admin_access_token` - Admin's JWT access token
3. ✅ `admin_refresh_token` - Admin's JWT refresh token
4. ✅ `user_username` - User's username
5. ✅ `user_access_token` - User's JWT access token
6. ✅ `user_refresh_token` - User's JWT refresh token

**All variables are:**
- ✅ Extracted in setUp thread group
- ✅ Converted to global properties
- ✅ Available to all other thread groups
- ✅ Used with `${__P(property_name)}` syntax
- ✅ Verified working in all tests

---

**Status:** 🎉 All Variables Successfully Shared!

