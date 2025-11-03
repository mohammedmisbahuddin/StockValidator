#!/bin/bash

#  Comprehensive Auth Service Test

echo "=========================================="
echo "🧪 Comprehensive Auth Service Test"
echo "=========================================="
echo ""

# Start auth service
echo "🚀 Starting Auth Service..."
cd /Users/mmisbahuddin/Documents/Personal_work/StockValidator/backend/services/auth
source ../../venv/bin/activate
python main.py > /tmp/auth_comp_test.log 2>&1 &
AUTH_PID=$!
sleep 5

echo "✅ Auth Service started (PID: $AUTH_PID)"
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "----------------------------------------"
HEALTH=$(curl -s http://localhost:8001/health)
echo "$HEALTH" | python3 -m json.tool
if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ Health check passed"
else
    echo "❌ Health check failed"
fi
echo ""

# Test 2: Register Admin User
echo "Test 2: Register Admin User"
echo "----------------------------------------"
ADMIN_RESP=$(curl -s -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","username":"admin","password":"AdminPass123","role":"admin"}')
echo "$ADMIN_RESP" | python3 -m json.tool
if echo "$ADMIN_RESP" | grep -q "admin@test.com"; then
    echo "✅ Admin registration successful"
else
    echo "❌ Admin registration failed"
fi
echo ""

# Test 3: Register Regular User
echo "Test 3: Register Regular User"
echo "----------------------------------------"
USER_RESP=$(curl -s -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","username":"testuser","password":"UserPass123","role":"user"}')
echo "$USER_RESP" | python3 -m json.tool
if echo "$USER_RESP" | grep -q "user@test.com"; then
    echo "✅ User registration successful"
else
    echo "❌ User registration failed"
fi
echo ""

# Test 4: Login with Admin
echo "Test 4: Admin Login"
echo "----------------------------------------"
ADMIN_LOGIN=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"AdminPass123"}')
echo "$ADMIN_LOGIN" | python3 -m json.tool
ADMIN_TOKEN=$(echo "$ADMIN_LOGIN" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)
if [ ! -z "$ADMIN_TOKEN" ]; then
    echo "✅ Admin login successful"
    echo "   Token: ${ADMIN_TOKEN:0:40}..."
else
    echo "❌ Admin login failed"
fi
echo ""

# Test 5: Login with User
echo "Test 5: User Login"
echo "----------------------------------------"
USER_LOGIN=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"UserPass123"}')
echo "$USER_LOGIN" | python3 -m json.tool
USER_TOKEN=$(echo "$USER_LOGIN" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)
REFRESH_TOKEN=$(echo "$USER_LOGIN" | python3 -c "import sys,json; print(json.load(sys.stdin).get('refresh_token',''))" 2>/dev/null)
if [ ! -z "$USER_TOKEN" ]; then
    echo "✅ User login successful"
    echo "   Token: ${USER_TOKEN:0:40}..."
else
    echo "❌ User login failed"
fi
echo ""

# Test 6: Get Current User (Admin)
echo "Test 6: Get Current User (Admin)"
echo "----------------------------------------"
if [ ! -z "$ADMIN_TOKEN" ]; then
    CURRENT_ADMIN=$(curl -s http://localhost:8001/auth/me \
      -H "Authorization: Bearer $ADMIN_TOKEN")
    echo "$CURRENT_ADMIN" | python3 -m json.tool
    if echo "$CURRENT_ADMIN" | grep -q "admin@test.com"; then
        echo "✅ Get current admin successful"
    else
        echo "❌ Get current admin failed"
    fi
else
    echo "⚠️  Skipped (no admin token)"
fi
echo ""

# Test 7: Get Current User (Regular User)
echo "Test 7: Get Current User (Regular User)"
echo "----------------------------------------"
if [ ! -z "$USER_TOKEN" ]; then
    CURRENT_USER=$(curl -s http://localhost:8001/auth/me \
      -H "Authorization: Bearer $USER_TOKEN")
    echo "$CURRENT_USER" | python3 -m json.tool
    if echo "$CURRENT_USER" | grep -q "user@test.com"; then
        echo "✅ Get current user successful"
    else
        echo "❌ Get current user failed"
    fi
else
    echo "⚠️  Skipped (no user token)"
fi
echo ""

# Test 8: Refresh Token
echo "Test 8: Refresh Token"
echo "----------------------------------------"
if [ ! -z "$REFRESH_TOKEN" ]; then
    REFRESH_RESP=$(curl -s -X POST http://localhost:8001/auth/refresh \
      -H "Content-Type: application/json" \
      -d "{\"refresh_token\":\"$REFRESH_TOKEN\"}")
    echo "$REFRESH_RESP" | python3 -m json.tool
    NEW_TOKEN=$(echo "$REFRESH_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)
    if [ ! -z "$NEW_TOKEN" ]; then
        echo "✅ Token refresh successful"
        echo "   New Token: ${NEW_TOKEN:0:40}..."
    else
        echo "❌ Token refresh failed"
    fi
else
    echo "⚠️  Skipped (no refresh token)"
fi
echo ""

# Test 9: Wrong Password
echo "Test 9: Wrong Password Login"
echo "----------------------------------------"
WRONG_PASS=$(curl -s -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"WrongPassword"}')
echo "$WRONG_PASS" | python3 -m json.tool
if echo "$WRONG_PASS" | grep -q "Incorrect username or password"; then
    echo "✅ Wrong password correctly rejected"
else
    echo "❌ Wrong password handling failed"
fi
echo ""

# Test 10: Duplicate Registration
echo "Test 10: Duplicate Username Registration"
echo "----------------------------------------"
DUP_RESP=$(curl -s -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"newuser@test.com","username":"testuser","password":"SomePass123","role":"user"}')
echo "$DUP_RESP" | python3 -m json.tool
if echo "$DUP_RESP" | grep -q "already exists"; then
    echo "✅ Duplicate username correctly rejected"
else
    echo "❌ Duplicate username handling failed"
fi
echo ""

# Cleanup
echo "🧹 Cleaning up..."
kill $AUTH_PID 2>/dev/null
wait $AUTH_PID 2>/dev/null

echo ""
echo "=========================================="
echo "✅ All Tests Complete!"
echo "=========================================="

