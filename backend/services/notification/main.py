"""
Notification Service - Main Application

Handles:
- Notification CRUD operations (admin)
- User notification viewing and read status (users)
"""
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.config import settings
from shared.database import init_db, close_db
from shared.redis_client import redis_client

# Import routes
from routes.notification_routes import router as notification_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the application"""
    # Startup
    logger.info("🚀 Starting Notification Service...")
    await redis_client.connect()
    logger.info("✅ Redis connected")
    await init_db()
    logger.info("✅ Database initialized")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Notification Service...")
    await redis_client.disconnect()
    await close_db()
    logger.info("✅ Notification Service stopped")


# Create FastAPI app
app = FastAPI(
    title="Notification Service",
    description="""
    Notification management service for StockValidator application.
    
    ## Features
    
    ### Admin Endpoints
    * **Notification CRUD** - Create, read, update, delete notifications
    * **View All Notifications** - See all notifications with details
    
    ### User Endpoints
    * **View My Notifications** - See all notifications with read/unread status
    * **Unread Count** - Get count of unread notifications
    * **Mark as Read** - Mark notifications as read
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notification_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "notification-service",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "notification-service",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )
