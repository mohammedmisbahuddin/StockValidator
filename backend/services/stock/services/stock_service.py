"""
Stock service business logic
"""
import sys
from pathlib import Path
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from models.stock import Stock, StockCategory, StockSubcategory
from schemas.stock import StockCreate, StockUpdate, StockListResponse, StockResponse
from services.ticker_validator import TickerValidationService

logger = logging.getLogger(__name__)


class StockService:
    """Service for stock management operations"""
    
    def __init__(self, ticker_validator: TickerValidationService):
        self.ticker_validator = ticker_validator
    
    async def create_stock(
        self,
        db: AsyncSession,
        stock_data: StockCreate,
        created_by: UUID
    ) -> Stock:
        """
        Create a new stock
        
        Args:
            db: Database session
            stock_data: Stock creation data
            created_by: UUID of user creating the stock
        
        Returns:
            Created stock
        
        Raises:
            ValueError: If ticker already exists or validation fails
        """
        # Check if ticker already exists
        result = await db.execute(
            select(Stock).where(Stock.ticker == stock_data.ticker.upper())
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise ValueError(f"Stock with ticker {stock_data.ticker} already exists")
        
        # Create stock
        # Convert enum to string value for database
        if hasattr(stock_data.category, 'value'):
            category_value = str(stock_data.category.value)
        else:
            category_value = str(stock_data.category)
            
        if stock_data.subcategory and hasattr(stock_data.subcategory, 'value'):
            subcategory_value = str(stock_data.subcategory.value)
        else:
            subcategory_value = str(stock_data.subcategory) if stock_data.subcategory else None
        
        logger.info(f"Creating stock with category: '{category_value}' (type: {type(category_value)})")
        
        stock = Stock(
            ticker=stock_data.ticker.upper(),
            company_name=stock_data.company_name,
            category=category_value,
            subcategory=subcategory_value,
            current_price=stock_data.current_price,
            created_by=created_by,
            state_history=[]
        )
        
        db.add(stock)
        await db.commit()
        await db.refresh(stock)
        
        logger.info(f"Created stock {stock.ticker} in category {stock.category}")
        return stock
    
    async def get_stock(self, db: AsyncSession, ticker: str) -> Optional[Stock]:
        """
        Get a stock by ticker
        
        Args:
            db: Database session
            ticker: Stock ticker symbol
        
        Returns:
            Stock if found, None otherwise
        """
        result = await db.execute(
            select(Stock).where(Stock.ticker == ticker.upper())
        )
        return result.scalar_one_or_none()
    
    async def get_all_stocks(self, db: AsyncSession) -> StockListResponse:
        """
        Get all stocks grouped by category
        
        Args:
            db: Database session
        
        Returns:
            StockListResponse with stocks grouped by category
        """
        result = await db.execute(select(Stock))
        stocks = result.scalars().all()
        
        # Group by category
        grouped = {
            "far": [],
            "near": [],
            "almost_ready": [],
            "ready": []
        }
        
        for stock in stocks:
            # category is now a string from PG_ENUM, not a Python enum
            category_key = stock.category if isinstance(stock.category, str) else stock.category.value
            stock_response = StockResponse.model_validate(stock)
            grouped[category_key].append(stock_response)
        
        return StockListResponse(
            far=grouped["far"],
            near=grouped["near"],
            almost_ready=grouped["almost_ready"],
            ready=grouped["ready"],
            total=len(stocks)
        )
    
    async def update_stock(
        self,
        db: AsyncSession,
        ticker: str,
        stock_data: StockUpdate,
        updated_by: UUID
    ) -> Optional[Stock]:
        """
        Update a stock
        
        Args:
            db: Database session
            ticker: Stock ticker symbol
            stock_data: Updated stock data
            updated_by: UUID of user updating the stock
        
        Returns:
            Updated stock if found, None otherwise
        """
        stock = await self.get_stock(db, ticker)
        if not stock:
            return None
        
        # Track category change
        old_category = stock.category
        
        # Update fields
        if stock_data.company_name is not None:
            stock.company_name = stock_data.company_name
        
        if stock_data.category is not None:
            new_category_value = stock_data.category.value if isinstance(stock_data.category, StockCategory) else stock_data.category
            stock.category = new_category_value
            
            # Add state history if category changed
            old_category_value = old_category.value if isinstance(old_category, StockCategory) else old_category
            if old_category_value != new_category_value:
                stock.add_state_change(
                    from_category=old_category_value,
                    to_category=new_category_value,
                    changed_by=updated_by
                )
        
        if stock_data.subcategory is not None:
            stock.subcategory = stock_data.subcategory.value if isinstance(stock_data.subcategory, StockSubcategory) else stock_data.subcategory
        elif stock_data.category is not None and stock_data.category != StockCategory.READY:
            # Clear subcategory if not ready
            stock.subcategory = None
        
        if stock_data.current_price is not None:
            stock.current_price = stock_data.current_price
        
        await db.commit()
        await db.refresh(stock)
        
        logger.info(f"Updated stock {stock.ticker}")
        return stock
    
    async def delete_stock(self, db: AsyncSession, ticker: str) -> bool:
        """
        Delete a stock
        
        Args:
            db: Database session
            ticker: Stock ticker symbol
        
        Returns:
            True if deleted, False if not found
        """
        stock = await self.get_stock(db, ticker)
        if not stock:
            return False
        
        await db.delete(stock)
        await db.commit()
        
        logger.info(f"Deleted stock {ticker}")
        return True
    
    async def validate_ticker(self, ticker: str):
        """
        Validate a ticker and get company information
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Tuple of (is_valid, company_name, current_price, source)
        """
        return await self.ticker_validator.validate_ticker(ticker)

