"""
Stock Service - Main Application

Handles:
- Stock CRUD operations (admin)
- Stock search with rate limiting (users)
- Ticker validation (yfinance + Finnhub)
- Rate limit management (admin)
"""
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.config import settings

# Import routes
from routes.stock_routes import router as stock_router
from routes.rate_limit_routes import router as rate_limit_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Stock Service",
    description="""
    Stock management service for StockValidator application.
    
    ## Features
    
    ### Admin Endpoints
    * **Stock CRUD** - Create, read, update, delete stocks
    * **Ticker Validation** - Validate stock tickers with market data
    * **Rate Limit Management** - Manage user search limits
    
    ### User Endpoints
    * **Stock Search** - Search stocks with rate limiting
    * **Ticker Validation** - Validate tickers before searching
    
    ## Stock Categories
    * **far** - Early stage stocks
    * **near** - Getting closer
    * **almost_ready** - Nearly ready
    * **ready** - Ready to trade (with subcategories: pullback1, pullback2)
    
    ## Rate Limiting
    * Users have configurable search limits
    * Only valid ticker searches count against limit
    * Admin can reset limits individually or universally
    * No automatic 24-hour reset (manual only)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(stock_router)
app.include_router(rate_limit_router)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "stock-service",
        "version": "1.0.0"
    }


@app.on_event("startup")
async def startup_event():
    """Application startup"""
    logger.info("Stock Service starting up...")
    logger.info(f"Database: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}")
    logger.info(f"Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    logger.info("Stock Service ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown"""
    logger.info("Stock Service shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
