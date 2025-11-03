"""
Mock Ticker Validation Service for Testing
Avoids hitting Yahoo Finance rate limits during development/testing
"""
from typing import Optional, Tuple
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class MockTickerValidationService:
    """
    Mock service that returns pre-defined ticker data without hitting external APIs
    
    Use this during development/testing to avoid rate limits
    """
    
    # Mock database of known tickers
    MOCK_TICKERS = {
        # US Stocks
        "AAPL": ("Apple Inc.", Decimal("175.50")),
        "MSFT": ("Microsoft Corporation", Decimal("380.00")),
        "GOOGL": ("Alphabet Inc.", Decimal("140.25")),
        "AMZN": ("Amazon.com Inc.", Decimal("150.00")),
        "TSLA": ("Tesla Inc.", Decimal("245.00")),
        "META": ("Meta Platforms Inc.", Decimal("350.00")),
        "NVDA": ("NVIDIA Corporation", Decimal("500.00")),
        
        # Indian Stocks (NSE)
        "RELIANCE.NS": ("Reliance Industries Limited", Decimal("2450.75")),
        "TCS.NS": ("Tata Consultancy Services Limited", Decimal("3750.00")),
        "INFY.NS": ("Infosys Limited", Decimal("1450.50")),
        "HDFCBANK.NS": ("HDFC Bank Limited", Decimal("1680.25")),
        "ICICIBANK.NS": ("ICICI Bank Limited", Decimal("950.75")),
        "SBIN.NS": ("State Bank of India", Decimal("625.00")),
        "ITC.NS": ("ITC Limited", Decimal("425.50")),
        "WIPRO.NS": ("Wipro Limited", Decimal("450.00")),
        "BHARTIARTL.NS": ("Bharti Airtel Limited", Decimal("900.00")),
        "HINDUNILVR.NS": ("Hindustan Unilever Limited", Decimal("2650.00")),
        
        # Indian Stocks (BSE)
        "RELIANCE.BO": ("Reliance Industries Limited", Decimal("2450.75")),
        "TCS.BO": ("Tata Consultancy Services Limited", Decimal("3750.00")),
        "INFY.BO": ("Infosys Limited", Decimal("1450.50")),
    }
    
    def __init__(self, auto_detect_indian: bool = True):
        """
        Initialize mock validator
        
        Args:
            auto_detect_indian: Automatically try Indian exchanges if ticker not found
        """
        self.auto_detect_indian = auto_detect_indian
        logger.info("🧪 Using MOCK ticker validator (no API calls)")
    
    async def validate_ticker(self, ticker: str) -> Tuple[bool, Optional[str], Optional[Decimal], Optional[str]]:
        """
        Validate ticker against mock database
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Tuple of (is_valid, company_name, current_price, source)
        """
        ticker = ticker.upper().strip()
        original_ticker = ticker
        
        # Check if ticker has exchange suffix
        has_exchange_suffix = any(ticker.endswith(suffix) for suffix in ['.NS', '.BO', '.N', '.O', '.L'])
        
        # Try direct lookup first
        if ticker in self.MOCK_TICKERS:
            company_name, price = self.MOCK_TICKERS[ticker]
            logger.info(f"✅ Mock: Found {ticker} - {company_name}, {price}")
            return True, company_name, price, "mock"
        
        # Auto-detect Indian stocks if enabled
        if self.auto_detect_indian and not has_exchange_suffix:
            # Try NSE
            nse_ticker = f"{original_ticker}.NS"
            if nse_ticker in self.MOCK_TICKERS:
                company_name, price = self.MOCK_TICKERS[nse_ticker]
                logger.info(f"✅ Mock: Found {original_ticker} on NSE as {nse_ticker} - {company_name}, {price}")
                return True, company_name, price, "mock (NSE)"
            
            # Try BSE
            bse_ticker = f"{original_ticker}.BO"
            if bse_ticker in self.MOCK_TICKERS:
                company_name, price = self.MOCK_TICKERS[bse_ticker]
                logger.info(f"✅ Mock: Found {original_ticker} on BSE as {bse_ticker} - {company_name}, {price}")
                return True, company_name, price, "mock (BSE)"
        
        # Not found
        logger.warning(f"❌ Mock: Ticker {original_ticker} not found in mock database")
        return False, None, None, None
    
    @classmethod
    def add_mock_ticker(cls, ticker: str, company_name: str, price: Decimal):
        """
        Add a new ticker to the mock database (for testing)
        
        Args:
            ticker: Stock ticker symbol
            company_name: Company name
            price: Stock price
        """
        cls.MOCK_TICKERS[ticker.upper()] = (company_name, price)
        logger.info(f"Added mock ticker: {ticker} - {company_name}, {price}")


# Convenience function
def create_mock_validator() -> MockTickerValidationService:
    """Create a mock validator instance"""
    return MockTickerValidationService(auto_detect_indian=True)

