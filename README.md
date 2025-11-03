# Stock Validator - Premium Stock Trading Admin Platform

A microservices-based application for stock traders to manage and share stock information with their users.

## 🏗️ Architecture

- **Frontend**: Next.js 14 (React 18) with TailwindCSS
- **Backend**: FastAPI (Python 3.11+) Microservices
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+
- **Theme**: Premium White/Black/Gold

## 🎯 Services

1. **Gateway Service** (Port 8000) - API Gateway & routing
2. **Auth Service** (Port 8001) - Authentication & user management
3. **Stock Service** (Port 8002) - Stock CRUD & search with market data
4. **Notification Service** (Port 8003) - Bulletin board

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### Development Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd StockValidator

# 2. Copy environment variables
cp .env.example .env

# 3. Start infrastructure (PostgreSQL + Redis)
docker-compose up -d postgres redis

# 4. Run database migrations
cd backend/services/auth
alembic upgrade head

cd ../stock
alembic upgrade head

cd ../notification
alembic upgrade head

# 5. Start backend services
# Terminal 1 - Gateway
cd backend/gateway
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2 - Auth Service
cd backend/services/auth
pip install -r requirements.txt
uvicorn main:app --reload --port 8001

# Terminal 3 - Stock Service
cd backend/services/stock
pip install -r requirements.txt
uvicorn main:app --reload --port 8002

# Terminal 4 - Notification Service
cd backend/services/notification
pip install -r requirements.txt
uvicorn main:app --reload --port 8003

# 6. Start frontend
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
StockValidator/
├── backend/
│   ├── gateway/              # API Gateway
│   ├── services/
│   │   ├── auth/             # Auth microservice
│   │   ├── stock/            # Stock microservice
│   │   └── notification/     # Notification microservice
│   └── shared/               # Shared utilities
├── frontend/                 # Next.js application
├── docker-compose.yml
└── .env
```

## 🧪 Testing

```bash
# Backend tests
cd backend/services/auth
pytest

cd ../stock
pytest

cd ../notification
pytest

# Frontend tests
cd frontend
npm test
```

## 🎨 UI Theme

Premium White/Black/Gold color scheme with shadcn/ui components.

## 📝 License

MIT

