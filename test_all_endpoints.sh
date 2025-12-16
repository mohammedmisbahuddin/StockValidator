#!/bin/bash

# Comprehensive API Testing Script for StockValidator
# Tests all endpoints and generates a report

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Base URLs
AUTH_URL="http://localhost:8001"
STOCK_URL="http://localhost:8002"

# Test results file
RESULTS_FILE="/tmp/stockvalidator_test_results.json"
echo "[]" > "$RESULTS_FILE"

# Function to log test result
log_test() {
    local test_name="$1"
    local status="$2"
    local details="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ "$status" == "PASS" ]; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        echo -e "   ${RED}Details: $details${NC}"
    fi
    
    # Add to JSON results
    python3 << EOF
import json
import sys

with open("$RESULTS_FILE", "r") as f:
    results = json.load(f)

results.append({
    "test": "$test_name",
    "status": "$status",
    "details": "$details"
})

with open("$RESULTS_FILE", "w") as f:
    json.dump(results, f, indent=2)
EOF
}

# Function to make API call and check response
test_endpoint() {
    local method="$1"
    local url="$2"
    local headers="$3"
    local data="$4"
    local expected_status="$5"
    local test_name="$6"
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" $headers 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" $headers -d "$data" 2>&1)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" == "$expected_status" ]; then
        log_test "$test_name" "PASS" "HTTP $http_code"
        echo "$body" | python3 -m json.tool 2>/dev/null | head -20 || echo "$body" | head -5
        return 0
    else
        log_test "$test_name" "FAIL" "Expected HTTP $expected_status, got $http_code. Response: $(echo "$body" | head -100)"
        return 1
    fi
}

echo ""
echo "=========================================="
echo "🧪 StockValidator - Comprehensive API Test"
echo "=========================================="
echo ""

# Check if services are running
echo "🔍 Checking services..."
if ! curl -s "$AUTH_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Auth Service is not running on $AUTH_URL${NC}"
    echo "Please start the Auth Service first"
    exit 1
fi

if ! curl -s "$STOCK_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Stock Service is not running on $STOCK_URL${NC}"
    echo "Please start the Stock Service first"
    exit 1
fi

echo -e "${GREEN}✅ Services are running${NC}"
echo ""

# ============================================
# PHASE 1: AUTH SERVICE TESTS
# ============================================
echo "=========================================="
echo "🔐 PHASE 1: Auth Service Tests"
echo "=========================================="
echo ""

# 1. Health Check
test_endpoint "GET" "$AUTH_URL/health" "" "" "200" "Auth Service - Health Check"

# 2. Register Admin User
ADMIN_REGISTER='{"email":"testadmin@test.com","username":"testadmin","password":"Admin@123","role":"admin"}'
test_endpoint "POST" "$AUTH_URL/auth/register" "-H 'Content-Type: application/json'" "$ADMIN_REGISTER" "201" "Auth Service - Register Admin"

# 3. Register Regular User
USER_REGISTER='{"email":"testuser@test.com","username":"testuser","password":"User@123","role":"user"}'
test_endpoint "POST" "$AUTH_URL/auth/register" "-H 'Content-Type: application/json'" "$USER_REGISTER" "201" "Auth Service - Register User"

# 4. Login Admin
ADMIN_LOGIN='{"username":"testadmin","password":"Admin@123"}'
ADMIN_RESPONSE=$(curl -s -X POST "$AUTH_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d "$ADMIN_LOGIN")
ADMIN_TOKEN=$(echo "$ADMIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -n "$ADMIN_TOKEN" ] && [ "$ADMIN_TOKEN" != "None" ]; then
    log_test "Auth Service - Login Admin" "PASS" "Token received"
else
    log_test "Auth Service - Login Admin" "FAIL" "No token received"
    exit 1
fi

# 5. Login User
USER_LOGIN='{"username":"testuser","password":"User@123"}'
USER_RESPONSE=$(curl -s -X POST "$AUTH_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d "$USER_LOGIN")
USER_TOKEN=$(echo "$USER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -n "$USER_TOKEN" ] && [ "$USER_TOKEN" != "None" ]; then
    log_test "Auth Service - Login User" "PASS" "Token received"
else
    log_test "Auth Service - Login User" "FAIL" "No token received"
    exit 1
fi

# 6. Get Current User (Admin)
test_endpoint "GET" "$AUTH_URL/auth/me" "-H 'Authorization: Bearer $ADMIN_TOKEN'" "" "200" "Auth Service - Get Current User (Admin)"

# 7. Get Current User (User)
test_endpoint "GET" "$AUTH_URL/auth/me" "-H 'Authorization: Bearer $USER_TOKEN'" "" "200" "Auth Service - Get Current User (User)"

echo ""

# ============================================
# PHASE 2: STOCK SERVICE - ADMIN OPERATIONS
# ============================================
echo "=========================================="
echo "📦 PHASE 2: Stock Service - Admin Operations"
echo "=========================================="
echo ""

# 1. Health Check
test_endpoint "GET" "$STOCK_URL/health" "" "" "200" "Stock Service - Health Check"

# 2. Validate Ticker (US Stock)
VALIDATE_US='{"ticker":"AAPL"}'
test_endpoint "POST" "$STOCK_URL/stocks/validate" \
    "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "$VALIDATE_US" "200" "Stock Service - Validate US Ticker (AAPL)"

# 3. Validate Ticker (Indian Stock)
VALIDATE_INDIAN='{"ticker":"RELIANCE.NS"}'
test_endpoint "POST" "$STOCK_URL/stocks/validate" \
    "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "$VALIDATE_INDIAN" "200" "Stock Service - Validate Indian Ticker (RELIANCE.NS)"

# 4. Validate Ticker (Auto-detect Indian)
VALIDATE_AUTO='{"ticker":"TCS"}'
test_endpoint "POST" "$STOCK_URL/stocks/validate" \
    "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "$VALIDATE_AUTO" "200" "Stock Service - Validate Auto-detect Indian (TCS)"

# 5. Create Stock (AAPL)
CREATE_AAPL='{"ticker":"AAPL","company_name":"Apple Inc.","category":"ready","subcategory":"pullback1","current_price":175.50}'
test_endpoint "POST" "$STOCK_URL/stocks" \
    "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "$CREATE_AAPL" "201" "Stock Service - Create Stock (AAPL)"

# 6. Create Stock (MSFT)
CREATE_MSFT='{"ticker":"MSFT","company_name":"Microsoft Corporation","category":"near","current_price":380.00}'
test_endpoint "POST" "$STOCK_URL/stocks" \
    "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "$CREATE_MSFT" "201" "Stock Service - Create Stock (MSFT)"

# 7. Create Stock (Indian - TCS.NS)
CREATE_TCS='{"ticker":"TCS.NS","company_name":"Tata Consultancy Services Limited","category":"ready","subcategory":"pullback2","current_price":3750.00}'
test_endpoint "POST" "$STOCK_URL/stocks" \
    "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "$CREATE_TCS" "201" "Stock Service - Create Indian Stock (TCS.NS)"

# 8. Get All Stocks
test_endpoint "GET" "$STOCK_URL/stocks" \
    "-H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "" "200" "Stock Service - Get All Stocks"

# 9. Get Specific Stock
test_endpoint "GET" "$STOCK_URL/stocks/AAPL" \
    "-H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "" "200" "Stock Service - Get Specific Stock (AAPL)"

# 10. Update Stock
UPDATE_AAPL='{"category":"near"}'
test_endpoint "PUT" "$STOCK_URL/stocks/AAPL" \
    "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "$UPDATE_AAPL" "200" "Stock Service - Update Stock (AAPL)"

echo ""

# ============================================
# PHASE 3: STOCK SERVICE - USER OPERATIONS
# ============================================
echo "=========================================="
echo "👤 PHASE 3: Stock Service - User Operations"
echo "=========================================="
echo ""

# 1. Search Stock (Found in System)
test_endpoint "GET" "$STOCK_URL/stocks/search/AAPL" \
    "-H 'Authorization: Bearer $USER_TOKEN'" \
    "" "200" "Stock Service - User Search Stock (Found - AAPL)"

# 2. Search Stock (Not in System but Valid)
test_endpoint "GET" "$STOCK_URL/stocks/search/GOOGL" \
    "-H 'Authorization: Bearer $USER_TOKEN'" \
    "" "200" "Stock Service - User Search Stock (Valid but Not in DB - GOOGL)"

# 3. Search Invalid Stock
test_endpoint "GET" "$STOCK_URL/stocks/search/INVALID123" \
    "-H 'Authorization: Bearer $USER_TOKEN'" \
    "" "200" "Stock Service - User Search Invalid Stock"

# 4. Validate Ticker (User - No Limit Impact)
test_endpoint "POST" "$STOCK_URL/stocks/validate" \
    "-H 'Content-Type: application/json' -H 'Authorization: Bearer $USER_TOKEN'" \
    "$VALIDATE_US" "200" "Stock Service - User Validate Ticker (No Limit)"

echo ""

# ============================================
# PHASE 4: RATE LIMIT MANAGEMENT
# ============================================
echo "=========================================="
echo "⚙️ PHASE 4: Rate Limit Management (Admin)"
echo "=========================================="
echo ""

# Get User ID from token (decode JWT or get from /auth/me)
USER_ID_RESPONSE=$(curl -s -X GET "$AUTH_URL/auth/me" \
    -H "Authorization: Bearer $USER_TOKEN")
USER_ID=$(echo "$USER_ID_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ -n "$USER_ID" ] && [ "$USER_ID" != "None" ]; then
    # 1. Get User Rate Limit Info
    test_endpoint "GET" "$STOCK_URL/admin/rate-limits/$USER_ID" \
        "-H 'Authorization: Bearer $ADMIN_TOKEN'" \
        "" "200" "Rate Limit - Get User Rate Limit Info"
    
    # 2. Update User Rate Limit
    UPDATE_LIMIT='{"search_limit":100}'
    test_endpoint "PUT" "$STOCK_URL/admin/rate-limits/$USER_ID" \
        "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ADMIN_TOKEN'" \
        "$UPDATE_LIMIT" "200" "Rate Limit - Update User Limit to 100"
    
    # 3. Reset User Rate Limit
    test_endpoint "POST" "$STOCK_URL/admin/rate-limits/$USER_ID/reset" \
        "-H 'Authorization: Bearer $ADMIN_TOKEN'" \
        "" "200" "Rate Limit - Reset User Limit"
    
    # 4. Reset All User Limits
    test_endpoint "POST" "$STOCK_URL/admin/rate-limits/reset-all" \
        "-H 'Authorization: Bearer $ADMIN_TOKEN'" \
        "" "200" "Rate Limit - Reset All User Limits"
else
    log_test "Rate Limit Tests" "SKIP" "Could not get User ID"
fi

echo ""

# ============================================
# SUMMARY
# ============================================
echo "=========================================="
echo "📊 TEST SUMMARY"
echo "=========================================="
echo ""
echo -e "Total Tests: ${BLUE}$TOTAL_TESTS${NC}"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}"
echo -e "${RED}Failed: $FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}⚠️ Some tests failed. Check details above.${NC}"
    exit 1
fi

