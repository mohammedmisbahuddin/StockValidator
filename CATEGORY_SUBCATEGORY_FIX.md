# 🐛 Bug Fix: Category & Subcategory Validation

## Issue Identified

### **Bug 1: Empty String Subcategory**
**Problem:** When `category` is NOT "ready" and `subcategory` is sent as empty string `""`, the API throws an error:
```
"Input should be 'pullback1' or 'pullback2'"
```

**Root Cause:** 
- Empty string `""` was being validated as a `StockSubcategory` enum value
- Enum validation happens before checking if subcategory should be None
- Empty strings should be converted to `None` for non-"ready" categories

### **Bug 2: Subcategory with Non-Ready Category**
**Problem:** When `category` is NOT "ready" and `subcategory` is provided (e.g., `"pullback1"`), the API correctly throws an error:
```
"Subcategory can only be set for 'ready' stocks"
```

**Status:** ✅ This was working correctly, but needed to handle empty strings first.

---

## Solution Implemented

### **Fix: Normalize Empty Strings Before Validation**

Added a `normalize_subcategory` validator that runs **before** enum validation to convert empty strings to `None`:

```python
@field_validator('subcategory', mode='before')
@classmethod
def normalize_subcategory(cls, v) -> Optional[StockSubcategory]:
    """Convert empty strings to None before validation"""
    if v == "" or v is None:
        return None
    return v
```

**Applied to:**
- ✅ `StockCreate` schema (for creating stocks)
- ✅ `StockUpdate` schema (for updating stocks)

---

## Test Results

### ✅ **Test 1: Empty String with Non-Ready Category**
```json
{
  "category": "near",
  "subcategory": ""
}
```
**Result:** ✅ **SUCCESS** - Empty string converted to `null`, stock created successfully

### ✅ **Test 2: Valid Subcategory with Non-Ready Category**
```json
{
  "category": "near",
  "subcategory": "pullback1"
}
```
**Result:** ✅ **CORRECT ERROR** - "Subcategory can only be set for 'ready' stocks"

### ✅ **Test 3: Valid Subcategory with Ready Category**
```json
{
  "category": "ready",
  "subcategory": "pullback1"
}
```
**Result:** ✅ **SUCCESS** - Stock created with subcategory

### ✅ **Test 4: Null Subcategory with Non-Ready Category**
```json
{
  "category": "far",
  "subcategory": null
}
```
**Result:** ✅ **SUCCESS** - Stock created successfully

### ✅ **Test 5: Update with Empty String**
```json
PUT /stocks/{ticker}
{
  "category": "almost_ready",
  "subcategory": ""
}
```
**Result:** ✅ **SUCCESS** - Empty string converted to `null`, stock updated

### ✅ **Test 6: Update to Ready with Subcategory**
```json
PUT /stocks/{ticker}
{
  "category": "ready",
  "subcategory": "pullback2"
}
```
**Result:** ✅ **SUCCESS** - Stock updated to ready with subcategory

### ✅ **Test 7: Update to Non-Ready with Subcategory**
```json
PUT /stocks/{ticker}
{
  "category": "near",
  "subcategory": "pullback1"
}
```
**Result:** ✅ **CORRECT ERROR** - "Subcategory can only be set for 'ready' stocks"

---

## Validation Rules (After Fix)

### **Subcategory Rules:**
1. ✅ **Empty string `""`** → Automatically converted to `None`
2. ✅ **`null`** → Accepted (no subcategory)
3. ✅ **Valid enum value** (`pullback1`, `pullback2`) → Only allowed when `category = "ready"`
4. ❌ **Invalid enum value** → Rejected with enum error
5. ❌ **Subcategory with non-ready category** → Rejected with validation error

### **Category Rules:**
- ✅ Valid categories: `far`, `near`, `almost_ready`, `ready`
- ✅ Subcategory required: Only when `category = "ready"`
- ✅ Subcategory optional: When `category != "ready"` (must be `null` or empty string)

---

## Code Changes

### **File: `backend/services/stock/schemas/stock.py`**

**Added to `StockBase` class:**
```python
@field_validator('subcategory', mode='before')
@classmethod
def normalize_subcategory(cls, v) -> Optional[StockSubcategory]:
    """Convert empty strings to None before validation"""
    if v == "" or v is None:
        return None
    return v
```

**Added to `StockUpdate` class:**
```python
@field_validator('subcategory', mode='before')
@classmethod
def normalize_subcategory(cls, v) -> Optional[StockSubcategory]:
    """Convert empty strings to None before validation"""
    if v == "" or v is None:
        return None
    return v
```

---

## API Behavior Examples

### **Create Stock - Valid Scenarios:**

#### ✅ **Non-Ready Category with Empty String**
```bash
POST /stocks
{
  "ticker": "AAPL",
  "company_name": "Apple Inc.",
  "category": "near",
  "subcategory": "",  # ✅ Converted to null
  "current_price": 175.50
}
```
**Response:** ✅ Stock created with `subcategory: null`

#### ✅ **Non-Ready Category with Null**
```bash
POST /stocks
{
  "ticker": "MSFT",
  "company_name": "Microsoft Corporation",
  "category": "far",
  "subcategory": null,  # ✅ Accepted
  "current_price": 380.00
}
```
**Response:** ✅ Stock created successfully

#### ✅ **Ready Category with Valid Subcategory**
```bash
POST /stocks
{
  "ticker": "GOOGL",
  "company_name": "Alphabet Inc.",
  "category": "ready",
  "subcategory": "pullback1",  # ✅ Valid
  "current_price": 140.25
}
```
**Response:** ✅ Stock created with subcategory

### **Create Stock - Invalid Scenarios:**

#### ❌ **Non-Ready Category with Subcategory**
```bash
POST /stocks
{
  "category": "near",
  "subcategory": "pullback1"  # ❌ Not allowed
}
```
**Response:** ❌ Error: "Subcategory can only be set for 'ready' stocks"

#### ❌ **Ready Category without Subcategory**
```bash
POST /stocks
{
  "category": "ready",
  "subcategory": null  # ⚠️ Allowed but might want to require it
}
```
**Response:** ✅ Currently allowed (subcategory is optional even for ready)

---

## Update Stock - Valid Scenarios:

#### ✅ **Update to Non-Ready with Empty String**
```bash
PUT /stocks/AAPL
{
  "category": "almost_ready",
  "subcategory": ""  # ✅ Converted to null
}
```
**Response:** ✅ Stock updated, subcategory set to `null`

#### ✅ **Update to Ready with Subcategory**
```bash
PUT /stocks/AAPL
{
  "category": "ready",
  "subcategory": "pullback2"  # ✅ Valid
}
```
**Response:** ✅ Stock updated to ready with subcategory

---

## Summary

### **Before Fix:**
- ❌ Empty string `""` caused enum validation error
- ✅ Valid subcategory with non-ready category correctly rejected
- ✅ Valid subcategory with ready category worked

### **After Fix:**
- ✅ Empty string `""` automatically converted to `None`
- ✅ Valid subcategory with non-ready category correctly rejected
- ✅ Valid subcategory with ready category works
- ✅ All edge cases handled correctly

---

## Files Modified

1. **`backend/services/stock/schemas/stock.py`**
   - Added `normalize_subcategory` validator to `StockBase`
   - Added `normalize_subcategory` validator to `StockUpdate`
   - Both validators run in `mode='before'` to normalize before enum validation

---

## Testing

All test scenarios pass:
- ✅ Empty string handling
- ✅ Null handling
- ✅ Valid subcategory with ready category
- ✅ Invalid subcategory with non-ready category
- ✅ Create endpoint
- ✅ Update endpoint

---

**Status:** ✅ **FIXED**  
**Date:** December 16, 2025  
**Impact:** Both Create and Update endpoints now handle empty strings correctly

