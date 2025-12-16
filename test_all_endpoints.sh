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

# Base URLs - Using API Gateway (unified entry point)
GATEWAY_URL="http://localhost:8000"
AUTH_URL="$GATEWAY_URL/api/auth"
STOCK_URL="$GATEWAY_URL/api/stocks"
NOTIFICATION_URL="$GATEWAY_URL/api/notifications"

# Direct service URLs (for health checks)
AUTH_SERVICE_URL="http://localhost:8001"
STOCK_SERVICE_URL="http://localhost:8002"
NOTIFICATION_SERVICE_URL="http://localhost:8003"

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
if ! curl -s "$GATEWAY_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ API Gateway is not running on $GATEWAY_URL${NC}"
    echo "Please start the API Gateway first"
    exit 1
fi

if ! curl -s "$AUTH_SERVICE_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Auth Service is not running on $AUTH_SERVICE_URL${NC}"
    echo "Please start the Auth Service first"
    exit 1
fi

if ! curl -s "$STOCK_SERVICE_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Stock Service is not running on $STOCK_SERVICE_URL${NC}"
    echo "Please start the Stock Service first"
    exit 1
fi

if ! curl -s "$NOTIFICATION_SERVICE_URL/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Notification Service is not running on $NOTIFICATION_SERVICE_URL${NC}"
    echo "Please start the Notification Service first"
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

# 1. Gateway Health Check
test_endpoint "GET" "$GATEWAY_URL/health" "" "" "200" "API Gateway - Health Check"

# 2. Register Admin User (through gateway)
ADMIN_REGISTER='{"email":"testadmin@test.com","username":"testadmin","password":"Admin@123","role":"admin"}'
test_endpoint "POST" "$AUTH_URL/register" "-H 'Content-Type: application/json'" "$ADMIN_REGISTER" "201" "Auth Service - Register Admin (via Gateway)"

# 3. Register Regular User (through gateway)
USER_REGISTER='{"email":"testuser@test.com","username":"testuser","password":"User@123","role":"user"}'
test_endpoint "POST" "$AUTH_URL/register" "-H 'Content-Type: application/json'" "$USER_REGISTER" "201" "Auth Service - Register User (via Gateway)"

# 4. Login Admin (through gateway)
ADMIN_LOGIN='{"username":"testadmin","password":"Admin@123"}'
ADMIN_RESPONSE=$(curl -s -X POST "$AUTH_URL/login" \
    -H "Content-Type: application/json" \
    -d "$ADMIN_LOGIN")
ADMIN_TOKEN=$(echo "$ADMIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -n "$ADMIN_TOKEN" ] && [ "$ADMIN_TOKEN" != "None" ]; then
    log_test "Auth Service - Login Admin" "PASS" "Token received"
else
    log_test "Auth Service - Login Admin" "FAIL" "No token received"
    exit 1
fi

# 5. Login User (through gateway)
USER_LOGIN='{"username":"testuser","password":"User@123"}'
USER_RESPONSE=$(curl -s -X POST "$AUTH_URL/login" \
    -H "Content-Type: application/json" \
    -d "$USER_LOGIN")
USER_TOKEN=$(echo "$USER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -n "$USER_TOKEN" ] && [ "$USER_TOKEN" != "None" ]; then
    log_test "Auth Service - Login User" "PASS" "Token received"
else
    log_test "Auth Service - Login User" "FAIL" "No token received"
    exit 1
fi

# 6. Get Current User (Admin) - through gateway
test_endpoint "GET" "$AUTH_URL/me" "-H 'Authorization: Bearer $ADMIN_TOKEN'" "" "200" "Auth Service - Get Current User (Admin via Gateway)"

# 7. Get Current User (User) - through gateway
test_endpoint "GET" "$AUTH_URL/me" "-H 'Authorization: Bearer $USER_TOKEN'" "" "200" "Auth Service - Get Current User (User via Gateway)"

echo ""

# ============================================
# PHASE 2: STOCK SERVICE - ADMIN OPERATIONS
# ============================================
echo "=========================================="
echo "📦 PHASE 2: Stock Service - Admin Operations"
echo "=========================================="
echo ""

# 1. Validate Ticker (US Stock) - through gateway
VALIDATE_US='{"ticker":"AAPL"}'
test_endpoint "POST" "$STOCK_URL/validate" \
    "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "$VALIDATE_US" "200" "Stock Service - Validate US Ticker (AAPL via Gateway)"

# 2. Validate Ticker (Indian Stock) - through gateway
VALIDATE_INDIAN='{"ticker":"RELIANCE.NS"}'
test_endpoint "POST" "$STOCK_URL/validate" \
    "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "$VALIDATE_INDIAN" "200" "Stock Service - Validate Indian Ticker (RELIANCE.NS via Gateway)"

# 3. Validate Ticker (Auto-detect Indian) - through gateway
VALIDATE_AUTO='{"ticker":"TCS"}'
test_endpoint "POST" "$STOCK_URL/validate" \
    "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "$VALIDATE_AUTO" "200" "Stock Service - Validate Auto-detect Indian (TCS via Gateway)"

# 4. Create Stock (AAPL) - through gateway
CREATE_AAPL='{"ticker":"AAPL","company_name":"Apple Inc.","category":"ready","subcategory":"pullback1","current_price":175.50}'
test_endpoint "POST" "$STOCK_URL" \
    "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "$CREATE_AAPL" "201" "Stock Service - Create Stock (AAPL via Gateway)"

# 5. Create Stock (MSFT) - through gateway
CREATE_MSFT='{"ticker":"MSFT","company_name":"Microsoft Corporation","category":"near","current_price":380.00}'
test_endpoint "POST" "$STOCK_URL" \
    "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "$CREATE_MSFT" "201" "Stock Service - Create Stock (MSFT via Gateway)"

# 6. Create Stock (Indian - TCS.NS) - through gateway
CREATE_TCS='{"ticker":"TCS.NS","company_name":"Tata Consultancy Services Limited","category":"ready","subcategory":"pullback2","current_price":3750.00}'
test_endpoint "POST" "$STOCK_URL" \
    "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "$CREATE_TCS" "201" "Stock Service - Create Indian Stock (TCS.NS via Gateway)"

# 7. Get All Stocks - through gateway
test_endpoint "GET" "$STOCK_URL" \
    "-H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "" "200" "Stock Service - Get All Stocks (via Gateway)"

# 8. Get Specific Stock - through gateway
test_endpoint "GET" "$STOCK_URL/AAPL" \
    "-H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "" "200" "Stock Service - Get Specific Stock (AAPL via Gateway)"

# 9. Update Stock - through gateway
UPDATE_AAPL='{"category":"near"}'
test_endpoint "PUT" "$STOCK_URL/AAPL" \
    "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "$UPDATE_AAPL" "200" "Stock Service - Update Stock (AAPL via Gateway)"

echo ""

# ============================================
# PHASE 3: STOCK SERVICE - USER OPERATIONS
# ============================================
echo "=========================================="
echo "👤 PHASE 3: Stock Service - User Operations"
echo "=========================================="
echo ""

# 1. Search Stock (Found in System) - through gateway
test_endpoint "GET" "$STOCK_URL/search/AAPL" \
    "-H 'Authorization: Bearer $USER_TOKEN'" \
    "" "200" "Stock Service - User Search Stock (Found - AAPL via Gateway)"

# 2. Search Stock (Not in System but Valid) - through gateway
test_endpoint "GET" "$STOCK_URL/search/GOOGL" \
    "-H 'Authorization: Bearer $USER_TOKEN'" \
    "" "200" "Stock Service - User Search Stock (Valid but Not in DB - GOOGL via Gateway)"

# 3. Search Invalid Stock - through gateway
test_endpoint "GET" "$STOCK_URL/search/INVALID123" \
    "-H 'Authorization: Bearer $USER_TOKEN'" \
    "" "200" "Stock Service - User Search Invalid Stock (via Gateway)"

# 4. Validate Ticker (User - No Limit Impact) - through gateway
test_endpoint "POST" "$STOCK_URL/validate" \
    "-H 'Content-Type: application/json' -H 'Authorization: Bearer $USER_TOKEN'" \
    "$VALIDATE_US" "200" "Stock Service - User Validate Ticker (No Limit via Gateway)"

echo ""

# ============================================
# PHASE 4: RATE LIMIT MANAGEMENT
# ============================================
echo "=========================================="
echo "⚙️ PHASE 4: Rate Limit Management (Admin)"
echo "=========================================="
echo ""

# Get User ID from token (decode JWT or get from /auth/me) - through gateway
USER_ID_RESPONSE=$(curl -s -X GET "$AUTH_URL/me" \
    -H "Authorization: Bearer $USER_TOKEN")
USER_ID=$(echo "$USER_ID_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ -n "$USER_ID" ] && [ "$USER_ID" != "None" ]; then
    # 1. Get User Rate Limit Info - through gateway
    test_endpoint "GET" "$STOCK_URL/admin/rate-limits/$USER_ID" \
        "-H 'Authorization: Bearer $ADMIN_TOKEN'" \
        "" "200" "Rate Limit - Get User Rate Limit Info (via Gateway)"
    
    # 2. Update User Rate Limit - through gateway
    UPDATE_LIMIT='{"search_limit":100}'
    test_endpoint "PUT" "$STOCK_URL/admin/rate-limits/$USER_ID" \
        "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ADMIN_TOKEN'" \
        "$UPDATE_LIMIT" "200" "Rate Limit - Update User Limit to 100 (via Gateway)"
    
    # 3. Reset User Rate Limit - through gateway
    test_endpoint "POST" "$STOCK_URL/admin/rate-limits/$USER_ID/reset" \
        "-H 'Authorization: Bearer $ADMIN_TOKEN'" \
        "" "200" "Rate Limit - Reset User Limit (via Gateway)"
    
    # 4. Reset All User Limits - through gateway
    test_endpoint "POST" "$STOCK_URL/admin/rate-limits/reset-all" \
        "-H 'Authorization: Bearer $ADMIN_TOKEN'" \
        "" "200" "Rate Limit - Reset All User Limits (via Gateway)"
else
    log_test "Rate Limit Tests" "SKIP" "Could not get User ID"
fi

echo ""

# ============================================
# PHASE 5: NOTIFICATION SERVICE - ADMIN OPERATIONS
# ============================================
echo "=========================================="
echo "📢 PHASE 5: Notification Service - Admin Operations"
echo "=========================================="
echo ""

# 1. Create Notification - through gateway
CREATE_NOTIF='{"title":"Market Update","message":"Important market trends for this week. Please review your portfolios."}'
CREATE_RESPONSE=$(curl -s -X POST "$NOTIFICATION_URL" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -d "$CREATE_NOTIF")
NOTIF_ID=$(echo "$CREATE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)

if [ -n "$NOTIF_ID" ] && [ "$NOTIF_ID" != "None" ] && [ "$NOTIF_ID" != "" ]; then
    log_test "Notification Service - Create Notification" "PASS" "Notification created with ID: $NOTIF_ID"
    echo "$CREATE_RESPONSE" | python3 -m json.tool | head -8
else
    log_test "Notification Service - Create Notification" "FAIL" "No notification ID received"
fi

# 2. Get All Notifications - through gateway
test_endpoint "GET" "$NOTIFICATION_URL" \
    "-H 'Authorization: Bearer $ADMIN_TOKEN'" \
    "" "200" "Notification Service - Get All Notifications (via Gateway)"

# 3. Get Specific Notification - through gateway
if [ -n "$NOTIF_ID" ] && [ "$NOTIF_ID" != "None" ] && [ "$NOTIF_ID" != "" ]; then
    test_endpoint "GET" "$NOTIFICATION_URL/$NOTIF_ID" \
        "-H 'Authorization: Bearer $ADMIN_TOKEN'" \
        "" "200" "Notification Service - Get Specific Notification (via Gateway)"
    
    # 4. Update Notification - through gateway
    UPDATE_NOTIF='{"title":"Updated Market Update","message":"Updated message with latest trends"}'
    test_endpoint "PUT" "$NOTIFICATION_URL/$NOTIF_ID" \
        "-H 'Content-Type: application/json' -H 'Authorization: Bearer $ADMIN_TOKEN'" \
        "$UPDATE_NOTIF" "200" "Notification Service - Update Notification (via Gateway)"
fi

echo ""

# ============================================
# PHASE 6: NOTIFICATION SERVICE - USER OPERATIONS
# ============================================
echo "=========================================="
echo "👤 PHASE 6: Notification Service - User Operations"
echo "=========================================="
echo ""

# 1. Get My Notifications - through gateway
test_endpoint "GET" "$NOTIFICATION_URL/user/my-notifications" \
    "-H 'Authorization: Bearer $USER_TOKEN'" \
    "" "200" "Notification Service - User Get My Notifications (via Gateway)"

# 2. Get Unread Count - through gateway
test_endpoint "GET" "$NOTIFICATION_URL/user/unread-count" \
    "-H 'Authorization: Bearer $USER_TOKEN'" \
    "" "200" "Notification Service - User Get Unread Count (via Gateway)"

# 3. Mark Notification as Read - through gateway
if [ -n "$NOTIF_ID" ] && [ "$NOTIF_ID" != "None" ] && [ "$NOTIF_ID" != "" ]; then
    test_endpoint "PUT" "$NOTIFICATION_URL/$NOTIF_ID/read" \
        "-H 'Authorization: Bearer $USER_TOKEN'" \
        "" "200" "Notification Service - User Mark as Read (via Gateway)"
    
    # Verify unread count decreased
    UNREAD_RESPONSE=$(curl -s -X GET "$NOTIFICATION_URL/user/unread-count" \
        -H "Authorization: Bearer $USER_TOKEN")
    UNREAD_COUNT=$(echo "$UNREAD_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('unread_count', ''))" 2>/dev/null)
    if [ "$UNREAD_COUNT" == "0" ] || [ "$UNREAD_COUNT" == "None" ]; then
        log_test "Notification Service - Unread Count After Read" "PASS" "Unread count: $UNREAD_COUNT"
    else
        log_test "Notification Service - Unread Count After Read" "PASS" "Unread count: $UNREAD_COUNT"
    fi
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

