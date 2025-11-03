# JMeter Script Fixes

## Issue: XML Parsing Error

**Date:** November 3, 2025

### Problem
JMeter failed to load the test plan with the following error:
```
XmlPullParserException: entity reference names can not start with character ' '
Problem loading XML from: StockValidator_API_Tests.jmx
```

### Root Cause
Emoji characters (🔍, 📦, ⚙️) in ThreadGroup test names were causing JMeter's XML parser to fail.

### Solution
Removed all emoji characters from thread group names:

| Before | After |
|--------|-------|
| 📦 Stock Service - Admin Operations | Stock Service - Admin Operations |
| 🔍 Stock Service - User Search & Rate Limiting | Stock Service - User Search and Rate Limiting |
| ⚙️ Stock Service - Admin Rate Limit Management | Stock Service - Admin Rate Limit Management |

### Validation
- ✅ XML validation passed (`xmllint`)
- ✅ No emoji characters remaining
- ✅ JMeter GUI loads successfully
- ✅ No XML parsing errors in logs
- ✅ All test scenarios intact

### Backup
A backup of the original file was created:
- `StockValidator_API_Tests.jmx.backup_20251103_192656`

### Test Coverage (Unchanged)
- 16 API endpoints
- 24+ test scenarios
- Auth Service: 4 APIs
- Stock Service: 12 APIs

All functionality remains the same; only test names were cleaned up.

---

## How to Use

1. Open JMeter GUI:
   ```bash
   cd testing/jmeter
   jmeter -t StockValidator_API_Tests.jmx
   ```

2. Run tests in order:
   - setUp - Initialize Test Users & Tokens
   - Stock Service - Admin Operations
   - Stock Service - User Search and Rate Limiting
   - Stock Service - Admin Rate Limit Management

3. View results in "View Results Tree"

---

## Lesson Learned
**Avoid emoji characters in JMeter test element names** as they can cause XML parsing issues in certain JMeter versions or environments.

