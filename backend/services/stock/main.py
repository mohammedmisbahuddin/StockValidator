"""
Stock Service - Handles stock management and search with market data
Port: 8002
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.config import settings
from shared.database import init_db, close_db
from shared.redis_client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the application"""
    # Startup
    print("🚀 Starting Stock Service...")
    await redis_client.connect()
    print("✅ Redis connected")
    await init_db()
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Stock Service...")
    await redis_client.disconnect()
    await close_db()
    print("✅ Stock Service stopped")


app = FastAPI(
    title="Stock Validator - Stock Service",
    description="Stock management and market data service",
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
        "service": "Stock Service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    redis_status = await redis_client.ping()
    
    return {
        "status": "healthy",
        "service": "stock",
        "redis": "connected" if redis_status else "disconnected",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

