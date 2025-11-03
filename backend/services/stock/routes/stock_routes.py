"""
Stock routes for admin and user operations
"""
import sys
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

# Add paths
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from shared.database import get_db
from shared.config import settings
from shared.models.user import User
from schemas.stock import (
    StockCreate,
    StockUpdate,
    StockResponse,
    StockListResponse,
    TickerValidationRequest,
    TickerValidationResponse,
    StockSearchRequest,
    StockSearchResponse,
)
from services.stock_service import StockService
from services.ticker_validator import TickerValidationService
from services.rate_limiter import RateLimitService

# Import auth middleware from shared
from shared.middleware.auth_middleware import get_current_user, require_admin

# Initialize services
ticker_validator = TickerValidationService(
    finnhub_api_key=getattr(settings, 'FINNHUB_API_KEY', None)
)
stock_service = StockService(ticker_validator)
rate_limiter = RateLimitService()

router = APIRouter(prefix="/stocks", tags=["Stocks"])


# ===== Admin Endpoints =====

@router.post("", response_model=StockResponse, status_code=status.HTTP_201_CREATED)
async def create_stock(
    stock_data: StockCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Create a new stock (Admin only)
    
    - **ticker**: Stock ticker symbol (will be uppercased)
    - **company_name**: Company name
    - **category**: Stock category (far, near, almost_ready, ready)
    - **subcategory**: Optional subcategory (only for 'ready' stocks)
    - **current_price**: Optional current market price
    """
    try:
        stock = await stock_service.create_stock(db, stock_data, current_user.id)
        return stock
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=StockListResponse)
async def get_all_stocks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get all stocks grouped by category (Admin only)
    
    Returns stocks organized by:
    - far
    - near
    - almost_ready
    - ready
    """
    return await stock_service.get_all_stocks(db)


@router.get("/{ticker}", response_model=StockResponse)
async def get_stock(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get a specific stock by ticker (Admin only)
    """
    stock = await stock_service.get_stock(db, ticker)
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock with ticker {ticker} not found"
        )
    return stock


@router.put("/{ticker}", response_model=StockResponse)
async def update_stock(
    ticker: str,
    stock_data: StockUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Update a stock (Admin only)
    
    Can update:
    - company_name
    - category (state change will be tracked)
    - subcategory (only for 'ready' stocks)
    - current_price
    """
    stock = await stock_service.update_stock(db, ticker, stock_data, current_user.id)
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock with ticker {ticker} not found"
        )
    return stock


@router.delete("/{ticker}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stock(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete a stock (Admin only)
    """
    deleted = await stock_service.delete_stock(db, ticker)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock with ticker {ticker} not found"
        )


@router.post("/validate", response_model=TickerValidationResponse)
async def validate_ticker(
    request: TickerValidationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Validate a ticker and get company information
    
    Available to both admin and users.
    Uses yfinance (primary) and Finnhub (fallback).
    
    Returns:
    - is_valid: Whether ticker exists
    - company_name: Company name if found
    - current_price: Current market price if found
    - source: Data source (yfinance or finnhub)
    """
    is_valid, company_name, current_price, source = await stock_service.validate_ticker(
        request.ticker
    )
    
    return TickerValidationResponse(
        ticker=request.ticker.upper(),
        is_valid=is_valid,
        company_name=company_name,
        current_price=current_price,
        source=source,
        error=None if is_valid else "Ticker not found"
    )


# ===== User Endpoints =====

@router.get("/search/{ticker}", response_model=StockSearchResponse)
async def search_stock(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search for a stock by ticker (User endpoint with rate limiting)
    
    - Checks if stock exists in our database
    - Validates ticker against market data (yfinance/Finnhub)
    - Only decrements search limit if ticker is valid
    - Returns remaining search limit
    """
    ticker = ticker.upper()
    
    # Check if stock exists in our database
    stock = await stock_service.get_stock(db, ticker)
    
    # Validate ticker
    is_valid, company_name, current_price, source = await stock_service.validate_ticker(ticker)
    
    # Get remaining searches BEFORE decrementing
    remaining_before = await rate_limiter.get_remaining_searches(current_user.id)
    
    # Only decrement if ticker is valid (either in DB or valid external ticker)
    if is_valid:
        success, remaining_after = await rate_limiter.decrement_search(current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Search limit exceeded. Please contact admin to reset your limit."
            )
    else:
        remaining_after = remaining_before
    
    # Prepare response
    if stock:
        # Stock found in our database
        return StockSearchResponse(
            found=True,
            ticker=ticker,
            stock=StockResponse.model_validate(stock),
            company_name=stock.company_name,
            current_price=stock.current_price,
            is_valid_ticker=True,
            remaining_searches=remaining_after,
            message="Stock found in our system"
        )
    elif is_valid:
        # Valid ticker but not in our database
        return StockSearchResponse(
            found=False,
            ticker=ticker,
            stock=None,
            company_name=company_name,
            current_price=current_price,
            is_valid_ticker=True,
            remaining_searches=remaining_after,
            message="Valid ticker but not in our system"
        )
    else:
        # Invalid ticker
        return StockSearchResponse(
            found=False,
            ticker=ticker,
            stock=None,
            company_name=None,
            current_price=None,
            is_valid_ticker=False,
            remaining_searches=remaining_after,
            message="Invalid ticker"
        )

