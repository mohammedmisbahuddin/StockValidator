# Authentication Service

Microservice for user authentication, JWT token management, and user profile handling.

## Features

- ✅ User registration (admin and regular users)
- ✅ JWT-based authentication (access & refresh tokens)
- ✅ Secure password hashing with bcrypt
- ✅ Token refresh mechanism
- ✅ User profile management
- ✅ Role-based access control (admin/user)
- ✅ Redis integration for session management

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL (async with SQLAlchemy 2.0)
- **Caching:** Redis
- **Authentication:** JWT (python-jose)
- **Password Hashing:** bcrypt 4.3.0 + passlib
- **Testing:** pytest, pytest-asyncio, httpx

## Project Structure

```
auth/
├── main.py                 # FastAPI application entry point
├── models/                 # SQLAlchemy models
│   ├── user.py            # User, RefreshToken, Settings models
│   └── __init__.py
├── routes/                 # API endpoints
│   ├── auth_routes.py     # Authentication routes
│   └── __init__.py
├── schemas/                # Pydantic models
│   ├── user.py            # Request/response schemas
│   └── __init__.py
├── services/               # Business logic
│   ├── auth_service.py    # Authentication service
│   └── __init__.py
├── middleware/             # Custom middleware
│   ├── auth_middleware.py # JWT verification
│   └── __init__.py
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── conftest.py        # Pytest fixtures
│   ├── test_auth_utils.py # Utility tests
│   ├── test_auth_service.py # Service tests
│   └── test_auth_endpoints.py # API tests
├── requirements.txt        # Service dependencies
├── requirements-test.txt   # Test dependencies
├── pytest.ini             # Pytest configuration
├── test_comprehensive.sh  # E2E test script
└── README.md              # This file
```

## Setup

### 1. Install Dependencies

```bash
cd backend/services/auth
source ../../venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-test.txt  # For testing
```

### 2. Environment Variables

Create a `.env` file in the project root with:

```env
POSTGRES_USER=stockadmin
POSTGRES_PASSWORD=stockpass123
POSTGRES_DB=stockvalidator
POSTGRES_HOST=localhost
POSTGRES_PORT=5433

REDIS_HOST=localhost
REDIS_PORT=6379

JWT_SECRET_KEY=super-secret-jwt-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. Start Infrastructure

```bash
cd backend
docker-compose up -d postgres redis
```

### 4. Run Service

```bash
cd backend/services/auth
source ../../venv/bin/activate
python main.py
```

Service will be available at `http://localhost:8001`

## API Endpoints

### Health Check
```http
GET /health
```

### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "Password123",
  "role": "user"
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "username",
  "password": "Password123"
}
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Get Current User
```http
GET /auth/me
Authorization: Bearer <access_token>
```

### Refresh Token
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ..."
}
```

## Testing

### Run Unit Tests
```bash
cd backend/services/auth
source ../../venv/bin/activate
pytest tests/test_auth_utils.py -v
```

### Run All Tests
```bash
pytest tests/ -v
```

### Run Comprehensive Integration Tests
```bash
./test_comprehensive.sh
```

### Test Coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

## Database Schema

### Users Table (`auth_schema.users`)
- `id` - UUID (Primary Key)
- `email` - VARCHAR (Unique)
- `username` - VARCHAR (Unique)
- `password_hash` - VARCHAR
- `role` - ENUM (admin, user)
- `search_limit` - INTEGER (Default: 50)
- `searches_used` - INTEGER (Default: 0)
- `last_reset_at` - TIMESTAMP
- `created_at` - TIMESTAMP
- `updated_at` - TIMESTAMP

### Refresh Tokens Table (`auth_schema.refresh_tokens`)
- `id` - UUID (Primary Key)
- `user_id` - UUID (Foreign Key → users.id)
- `token` - VARCHAR (Unique)
- `expires_at` - TIMESTAMP
- `created_at` - TIMESTAMP

### Settings Table (`auth_schema.settings`)
- `id` - UUID (Primary Key)
- `key` - VARCHAR (Unique)
- `value` - TEXT
- `created_at` - TIMESTAMP
- `updated_at` - TIMESTAMP

## Security

### Password Hashing
- Algorithm: bcrypt (cost factor: 12)
- Max length: 72 bytes
- Min length: 8 characters (enforced by Pydantic)

### JWT Tokens
- **Access Token:** 30-minute expiration
- **Refresh Token:** 7-day expiration
- Algorithm: HS256
- Includes: user_id, username, role, expiration

### Rate Limiting
- Managed manually by admin
- Per-user search limits stored in database
- Redis-backed for fast lookups

## Common Issues

### Issue: "password cannot be longer than 72 bytes"
**Solution:** Ensure bcrypt version is `4.x` (not `5.x`)
```bash
pip install "bcrypt>=4.0.0,<5.0.0"
```

### Issue: Port 8001 already in use
**Solution:** Kill stale processes
```bash
pkill -9 -f "python.*main.py"
lsof -ti:8001 | xargs kill -9
```

### Issue: Database connection fails
**Solution:** Check Docker containers and port mapping
```bash
docker ps
# PostgreSQL should be on port 5433:5432
# Redis should be on port 6379:6379
```

## Development

### Adding New Endpoints

1. Define schema in `schemas/user.py`
2. Add business logic in `services/auth_service.py`
3. Create route in `routes/auth_routes.py`
4. Write tests in `tests/`

### Running in Debug Mode

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001 --log-level debug
```

## Documentation

- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc
- **OpenAPI JSON:** http://localhost:8001/openapi.json

## Status

✅ **Production Ready** - All tests passing, fully functional

Last Updated: October 31, 2025

