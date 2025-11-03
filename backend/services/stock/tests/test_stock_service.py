"""
Unit tests for Stock Service business logic
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from services.stock_service import StockService
from services.ticker_validator import TickerValidationService
from models.stock import StockCategory, StockSubcategory
from schemas.stock import StockCreate, StockUpdate


class TestStockService:
    """Test stock service business logic"""
    
    @pytest.fixture
    def ticker_validator(self):
        """Mock ticker validator"""
        validator = Mock(spec=TickerValidationService)
        validator.validate_ticker = AsyncMock(return_value=(True, "Apple Inc.", 185.50, "yfinance"))
        return validator
    
    @pytest.fixture
    def stock_service(self, ticker_validator):
        """Create stock service instance"""
        return StockService(ticker_validator)
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock()
    
    @pytest.fixture
    def user_id(self):
        """Generate test user ID"""
        return uuid4()
    
    @pytest.mark.asyncio
    async def test_create_stock_success(self, stock_service, mock_db, user_id):
        """Test successful stock creation"""
        stock_data = StockCreate(
            ticker="AAPL",
            company_name="Apple Inc.",
            category=StockCategory.READY,
            subcategory=StockSubcategory.PULLBACK1,
            current_price=185.50
        )
        
        # Mock no existing stock
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        stock = await stock_service.create_stock(mock_db, stock_data, user_id)
        
        assert stock.ticker == "AAPL"
        assert stock.company_name == "Apple Inc."
        assert stock.category == StockCategory.READY
        assert stock.subcategory == StockSubcategory.PULLBACK1
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_stock_duplicate(self, stock_service, mock_db, user_id):
        """Test creating duplicate stock raises error"""
        stock_data = StockCreate(
            ticker="AAPL",
            company_name="Apple Inc.",
            category=StockCategory.NEAR
        )
        
        # Mock existing stock
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = Mock()
        mock_db.execute.return_value = mock_result
        
        with pytest.raises(ValueError, match="already exists"):
            await stock_service.create_stock(mock_db, stock_data, user_id)
    
    @pytest.mark.asyncio
    async def test_get_stock(self, stock_service, mock_db):
        """Test getting a stock by ticker"""
        mock_stock = Mock()
        mock_stock.ticker = "AAPL"
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_stock
        mock_db.execute.return_value = mock_result
        
        stock = await stock_service.get_stock(mock_db, "AAPL")
        
        assert stock is not None
        assert stock.ticker == "AAPL"
    
    @pytest.mark.asyncio
    async def test_get_stock_not_found(self, stock_service, mock_db):
        """Test getting non-existent stock"""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        stock = await stock_service.get_stock(mock_db, "NOTFOUND")
        
        assert stock is None
    
    @pytest.mark.asyncio
    async def test_get_all_stocks(self, stock_service, mock_db):
        """Test getting all stocks grouped by category"""
        # Mock stocks
        mock_stock1 = Mock()
        mock_stock1.ticker = "AAPL"
        mock_stock1.category = StockCategory.READY
        
        mock_stock2 = Mock()
        mock_stock2.ticker = "MSFT"
        mock_stock2.category = StockCategory.NEAR
        
        mock_result = AsyncMock()
        mock_result.scalars.return_value.all.return_value = [mock_stock1, mock_stock2]
        mock_db.execute.return_value = mock_result
        
        result = await stock_service.get_all_stocks(mock_db)
        
        assert result.total == 2
        # Would need to check grouped results
    
    @pytest.mark.asyncio
    async def test_update_stock(self, stock_service, mock_db, user_id):
        """Test updating a stock"""
        mock_stock = Mock()
        mock_stock.ticker = "AAPL"
        mock_stock.category = StockCategory.READY
        mock_stock.add_state_change = Mock()
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_stock
        mock_db.execute.return_value = mock_result
        
        stock_data = StockUpdate(category=StockCategory.NEAR)
        
        stock = await stock_service.update_stock(mock_db, "AAPL", stock_data, user_id)
        
        assert stock is not None
        assert stock.category == StockCategory.NEAR
        mock_stock.add_state_change.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_stock_not_found(self, stock_service, mock_db, user_id):
        """Test updating non-existent stock"""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        stock_data = StockUpdate(category=StockCategory.NEAR)
        
        stock = await stock_service.update_stock(mock_db, "NOTFOUND", stock_data, user_id)
        
        assert stock is None
    
    @pytest.mark.asyncio
    async def test_delete_stock(self, stock_service, mock_db):
        """Test deleting a stock"""
        mock_stock = Mock()
        
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_stock
        mock_db.execute.return_value = mock_result
        
        deleted = await stock_service.delete_stock(mock_db, "AAPL")
        
        assert deleted is True
        mock_db.delete.assert_called_once_with(mock_stock)
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_stock_not_found(self, stock_service, mock_db):
        """Test deleting non-existent stock"""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        deleted = await stock_service.delete_stock(mock_db, "NOTFOUND")
        
        assert deleted is False
    
    @pytest.mark.asyncio
    async def test_validate_ticker(self, stock_service):
        """Test ticker validation"""
        result = await stock_service.validate_ticker("AAPL")
        
        is_valid, company_name, price, source = result
        assert is_valid is True
        assert company_name == "Apple Inc."
        assert price == 185.50
        assert source == "yfinance"

