# 🔐 Demo Users for API Testing

## Quick Access Demo Users

### **Admin User** (Full Access)

**Username:** `demoadmin`  
**Password:** `Admin@123`  
**Email:** demo.admin@stockvalidator.com  
**Role:** Admin  
**Access:** All endpoints (Auth + Stock Admin + Rate Limit Management)

**Alternative Admin:**
- **Username:** `testadmin`
- **Password:** `Admin@123`

---

### **Regular User** (Limited Access)

**Username:** `demouser`  
**Password:** `User@123`  
**Email:** demo.user@stockvalidator.com  
**Role:** User  
**Access:** Stock Search + Ticker Validation (no limit impact)

**Search Limit:** 50 searches per day (default)

---

## 🧪 Quick Test Commands

### **1. Login as Admin**

```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demoadmin",
    "password": "Admin@123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Save the `access_token` for subsequent requests!**

---

### **2. Login as User**

```bash
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demouser",
    "password": "User@123"
  }'
```

---

## 📋 API Testing Examples

### **Admin Endpoints**

#### **Validate Ticker**
```bash
curl -X POST http://localhost:8002/stocks/validate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{"ticker": "AAPL"}'
```

#### **Create Stock**
```bash
curl -X POST http://localhost:8002/stocks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "category": "ready",
    "subcategory": "pullback1",
    "current_price": 175.50
  }'
```

#### **Get All Stocks**
```bash
curl -X GET http://localhost:8002/stocks \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

### **User Endpoints**

#### **Search Stock**
```bash
curl -X GET "http://localhost:8002/stocks/search/AAPL" \
  -H "Authorization: Bearer YOUR_USER_TOKEN"
```

#### **Validate Ticker (No Limit Impact)**
```bash
curl -X POST http://localhost:8002/stocks/validate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -d '{"ticker": "RELIANCE.NS"}'
```

---

## 🔑 Using Swagger UI

### **Step 1: Login**
1. Go to http://localhost:8001/docs
2. Click `POST /auth/login`
3. Click "Try it out"
4. Use credentials:
   ```json
   {
     "username": "demoadmin",
     "password": "Admin@123"
   }
   ```
5. Copy the `access_token` from response

### **Step 2: Authorize**
1. Click the **"Authorize"** button (top right)
2. Paste your `access_token`
3. Click "Authorize"
4. Now all protected endpoints will use this token automatically!

### **Step 3: Test Endpoints**
- All endpoints are now authenticated
- Click "Try it out" on any endpoint
- Fill in request body if needed
- Click "Execute"
- See the response!

---

## 📊 User Roles & Permissions

### **Admin (`demoadmin`)**
✅ Can access:
- All Auth endpoints
- All Stock CRUD operations
- Ticker validation
- Rate limit management
- User management

### **User (`demouser`)**
✅ Can access:
- Login/Profile endpoints
- Stock search (with rate limiting)
- Ticker validation (no limit impact)

❌ Cannot access:
- Stock CRUD operations
- Rate limit management
- Other users' data

---

## 🧪 Test Scenarios

### **Scenario 1: Admin Creates Stock**
1. Login as `demoadmin`
2. Validate ticker: `POST /stocks/validate` with `{"ticker": "AAPL"}`
3. Create stock: `POST /stocks` with stock data
4. View all stocks: `GET /stocks`

### **Scenario 2: User Searches Stock**
1. Login as `demouser`
2. Search stock: `GET /stocks/search/AAPL`
3. Check remaining searches in response
4. Search again (limit decrements)
5. Search invalid ticker (limit doesn't decrement)

### **Scenario 3: Rate Limit Management**
1. Login as `demoadmin`
2. Get user limit: `GET /admin/rate-limits/{user_id}`
3. Update limit: `PUT /admin/rate-limits/{user_id}` with `{"search_limit": 100}`
4. Reset limit: `POST /admin/rate-limits/{user_id}/reset`

---

## 🔄 Creating New Demo Users

If you need fresh users:

```bash
# Create Admin
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newadmin@test.com",
    "username": "newadmin",
    "password": "Admin@123",
    "role": "admin"
  }'

# Create User
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@test.com",
    "username": "newuser",
    "password": "User@123",
    "role": "user"
  }'
```

---

## 📝 Notes

- **Tokens expire in 30 minutes** - Re-login if token expires
- **Search limit:** Default is 50 searches per user
- **Mock Validator:** Currently active (no real API calls, no rate limits)
- **Indian Stocks:** Supported (e.g., `RELIANCE.NS`, `TCS.NS`)

---

## 🚀 Quick Start

**Fastest way to test:**

1. **Open Swagger:** http://localhost:8001/docs
2. **Login:** Use `demoadmin` / `Admin@123`
3. **Copy token** from response
4. **Click "Authorize"** → Paste token
5. **Test any endpoint!**

**Stock Service Swagger:** http://localhost:8002/docs  
(Same process - login first, then authorize)

---

**Happy Testing!** 🎉

