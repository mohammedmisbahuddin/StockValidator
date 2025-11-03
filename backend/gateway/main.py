"""
API Gateway - Routes requests to appropriate microservices
Port: 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent))

from shared.config import settings
from shared.redis_client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the application"""
    # Startup
    print("🚀 Starting API Gateway...")
    await redis_client.connect()
    print("✅ Redis connected")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down API Gateway...")
    await redis_client.disconnect()
    print("✅ API Gateway stopped")


app = FastAPI(
    title="Stock Validator - API Gateway",
    description="Central API gateway for all services",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "API Gateway",
        "version": "1.0.0",
        "status": "running",
        "services": {
            "auth": settings.AUTH_SERVICE_URL,
            "stock": settings.STOCK_SERVICE_URL,
            "notification": settings.NOTIFICATION_SERVICE_URL,
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    redis_status = await redis_client.ping()
    
    return {
        "status": "healthy",
        "service": "gateway",
        "redis": "connected" if redis_status else "disconnected",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

