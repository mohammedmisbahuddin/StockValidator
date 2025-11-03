"""
Ticker validation service using yfinance (primary) and Finnhub (fallback)
"""
import yfinance as yf
import requests
from typing import Optional, Tuple
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class TickerValidationService:
    """
    Service to validate stock tickers and fetch company information
    
    Supports:
    - US stocks: AAPL, MSFT, GOOGL
    - Indian stocks (NSE): RELIANCE.NS, TCS.NS, INFY.NS
    - Indian stocks (BSE): RELIANCE.BO, TCS.BO, INFY.BO
    
    Uses:
    1. yfinance (primary) - Free, no API key needed
    2. Finnhub (fallback) - Requires API key
    """
    
    def __init__(self, finnhub_api_key: Optional[str] = None, auto_detect_indian: bool = True):
        """
        Initialize ticker validation service
        
        Args:
            finnhub_api_key: Optional Finnhub API key for fallback
            auto_detect_indian: Automatically try Indian exchanges (.NS, .BO) if no suffix
        """
        self.finnhub_api_key = finnhub_api_key or ""
        self.auto_detect_indian = auto_detect_indian
        
    async def validate_ticker(self, ticker: str) -> Tuple[bool, Optional[str], Optional[Decimal], Optional[str]]:
        """
        Validate a stock ticker and fetch company name and price
        
        Supports:
        - US stocks: AAPL, MSFT, GOOGL
        - Indian stocks: RELIANCE.NS, TCS.NS (NSE) or RELIANCE.BO (BSE)
        
        Auto-detection for Indian stocks:
        - If ticker has no exchange suffix and US validation fails,
          automatically tries NSE (.NS) and BSE (.BO)
        
        Args:
            ticker: Stock ticker symbol (e.g., "AAPL", "RELIANCE.NS", "RELIANCE")
        
        Returns:
            Tuple of (is_valid, company_name, current_price, source)
            - is_valid: Whether the ticker exists
            - company_name: Company name if found
            - current_price: Current market price if found
            - source: "yfinance" or "finnhub" indicating data source
        """
        ticker = ticker.upper().strip()
        original_ticker = ticker
        
        # Check if ticker already has an exchange suffix
        has_exchange_suffix = any(ticker.endswith(suffix) for suffix in ['.NS', '.BO', '.N', '.O', '.L'])
        
        # Try yfinance first (primary)
        try:
            is_valid, company_name, price = await self._validate_with_yfinance(ticker)
            if is_valid:
                return is_valid, company_name, price, "yfinance"
        except Exception as e:
            logger.warning(f"yfinance validation failed for {ticker}: {e}")
        
        # Auto-detect Indian stocks if enabled and no exchange suffix
        if self.auto_detect_indian and not has_exchange_suffix:
            logger.info(f"Ticker {original_ticker} not found, trying Indian exchanges...")
            
            # Try NSE (.NS) first (larger exchange)
            try:
                nse_ticker = f"{original_ticker}.NS"
                is_valid, company_name, price = await self._validate_with_yfinance(nse_ticker)
                if is_valid:
                    logger.info(f"Found {original_ticker} on NSE as {nse_ticker}")
                    return is_valid, company_name, price, "yfinance (NSE)"
            except Exception as e:
                logger.debug(f"NSE validation failed for {nse_ticker}: {e}")
            
            # Try BSE (.BO) if NSE failed
            try:
                bse_ticker = f"{original_ticker}.BO"
                is_valid, company_name, price = await self._validate_with_yfinance(bse_ticker)
                if is_valid:
                    logger.info(f"Found {original_ticker} on BSE as {bse_ticker}")
                    return is_valid, company_name, price, "yfinance (BSE)"
            except Exception as e:
                logger.debug(f"BSE validation failed for {bse_ticker}: {e}")
        
        # Fallback to Finnhub if yfinance fails
        if self.finnhub_api_key:
            try:
                is_valid, company_name, price = await self._validate_with_finnhub(ticker)
                if is_valid:
                    return is_valid, company_name, price, "finnhub"
            except Exception as e:
                logger.warning(f"Finnhub validation failed for {ticker}: {e}")
        
        # All attempts failed
        logger.warning(f"Ticker validation failed for {original_ticker} (tried all sources)")
        return False, None, None, None
    
    async def _validate_with_yfinance(self, ticker: str) -> Tuple[bool, Optional[str], Optional[Decimal]]:
        """
        Validate ticker using yfinance
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Tuple of (is_valid, company_name, current_price)
        """
        try:
            # Create ticker object
            stock = yf.Ticker(ticker)
            
            # Fetch info
            info = stock.info
            
            # Check if ticker is valid (has basic information)
            if not info or len(info) < 5:
                return False, None, None
            
            # Get company name
            company_name = (
                info.get('longName') or 
                info.get('shortName') or 
                info.get('name')
            )
            
            if not company_name:
                return False, None, None
            
            # Get current price
            current_price = (
                info.get('currentPrice') or 
                info.get('regularMarketPrice') or 
                info.get('previousClose')
            )
            
            if current_price:
                current_price = Decimal(str(current_price))
            
            logger.info(f"yfinance validation successful for {ticker}: {company_name}, ${current_price}")
            return True, company_name, current_price
            
        except Exception as e:
            logger.error(f"yfinance validation error for {ticker}: {e}")
            return False, None, None
    
    async def _validate_with_finnhub(self, ticker: str) -> Tuple[bool, Optional[str], Optional[Decimal]]:
        """
        Validate ticker using Finnhub API
        
        Args:
            ticker: Stock ticker symbol
        
        Returns:
            Tuple of (is_valid, company_name, current_price)
        """
        if not self.finnhub_api_key:
            return False, None, None
        
        try:
            # Get company profile
            profile_url = f"https://finnhub.io/api/v1/stock/profile2"
            profile_params = {
                "symbol": ticker,
                "token": self.finnhub_api_key
            }
            
            profile_response = requests.get(profile_url, params=profile_params, timeout=5)
            profile_response.raise_for_status()
            profile_data = profile_response.json()
            
            # Check if valid ticker
            if not profile_data or 'name' not in profile_data:
                return False, None, None
            
            company_name = profile_data.get('name')
            
            # Get current price
            quote_url = f"https://finnhub.io/api/v1/quote"
            quote_params = {
                "symbol": ticker,
                "token": self.finnhub_api_key
            }
            
            quote_response = requests.get(quote_url, params=quote_params, timeout=5)
            quote_response.raise_for_status()
            quote_data = quote_response.json()
            
            current_price = quote_data.get('c')  # Current price
            if current_price:
                current_price = Decimal(str(current_price))
            
            logger.info(f"Finnhub validation successful for {ticker}: {company_name}, ${current_price}")
            return True, company_name, current_price
            
        except Exception as e:
            logger.error(f"Finnhub validation error for {ticker}: {e}")
            return False, None, None

