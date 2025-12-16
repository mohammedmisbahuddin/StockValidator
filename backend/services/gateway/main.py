"""
API Gateway - Main Application

Unified entry point for all microservices:
- /api/auth/* → Auth Service (8001)
- /api/stocks/* → Stock Service (8002)
- /api/notifications/* → Notification Service (8003)
"""
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.config import settings
from routes.proxy_routes import router as proxy_router
from middleware.logging_middleware import LoggingMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="StockValidator API Gateway",
    description="""
    Unified API Gateway for StockValidator microservices.
    
    ## Routes
    
    All requests are routed to appropriate backend services:
    
    - **`/api/auth/*`** → Auth Service (port 8001)
      - Authentication, registration, user management
    
    - **`/api/stocks/*`** → Stock Service (port 8002)
      - Stock CRUD, ticker validation, search, rate limiting
    
    - **`/api/notifications/*`** → Notification Service (port 8003)
      - Notification management, user notifications
    
    ## Benefits
    
    - ✅ Single entry point for all APIs
    - ✅ Unified API documentation
    - ✅ Centralized CORS configuration
    - ✅ Request logging and monitoring
    - ✅ Easy to add new services
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(proxy_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "api-gateway",
        "version": "1.0.0",
        "status": "running",
        "routes": {
            "/api/auth": "Auth Service",
            "/api/stocks": "Stock Service",
            "/api/notifications": "Notification Service"
        },
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

