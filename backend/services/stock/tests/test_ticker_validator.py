"""
Unit tests for Ticker Validation Service
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from services.ticker_validator import TickerValidationService


class TestTickerValidationService:
    """Test ticker validation with yfinance and Finnhub"""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance"""
        return TickerValidationService(finnhub_api_key="test_key")
    
    @pytest.mark.asyncio
    async def test_validate_ticker_yfinance_success(self, validator):
        """Test successful ticker validation with yfinance"""
        with patch('yfinance.Ticker') as mock_ticker:
            # Mock yfinance response
            mock_info = {
                'longName': 'Apple Inc.',
                'currentPrice': 185.50
            }
            mock_ticker.return_value.info = mock_info
            
            is_valid, company_name, price, source = await validator.validate_ticker("AAPL")
            
            assert is_valid is True
            assert company_name == "Apple Inc."
            assert price == 185.50
            assert source == "yfinance"
    
    @pytest.mark.asyncio
    async def test_validate_ticker_yfinance_no_price(self, validator):
        """Test yfinance response with missing price"""
        with patch('yfinance.Ticker') as mock_ticker:
            # Mock yfinance response without price
            mock_info = {
                'longName': 'Test Company',
                'regularMarketPrice': 100.00
            }
            mock_ticker.return_value.info = mock_info
            
            is_valid, company_name, price, source = await validator.validate_ticker("TEST")
            
            assert is_valid is True
            assert company_name == "Test Company"
            assert price == 100.00
            assert source == "yfinance"
    
    @pytest.mark.asyncio
    async def test_validate_ticker_finnhub_fallback(self, validator):
        """Test Finnhub fallback when yfinance fails"""
        with patch('yfinance.Ticker') as mock_ticker:
            # Mock yfinance failure
            mock_ticker.return_value.info = {}
            
            with patch('requests.get') as mock_get:
                # Mock Finnhub success
                mock_response = Mock()
                mock_response.json.return_value = {
                    'name': 'Microsoft Corporation',
                    'c': 380.50  # current price
                }
                mock_response.raise_for_status = Mock()
                mock_get.return_value = mock_response
                
                is_valid, company_name, price, source = await validator.validate_ticker("MSFT")
                
                assert is_valid is True
                assert company_name == "Microsoft Corporation"
                assert price == 380.50
                assert source == "finnhub"
    
    @pytest.mark.asyncio
    async def test_validate_ticker_invalid(self, validator):
        """Test invalid ticker (both sources fail)"""
        with patch('yfinance.Ticker') as mock_ticker:
            # Mock yfinance failure
            mock_ticker.return_value.info = {}
            
            with patch('requests.get') as mock_get:
                # Mock Finnhub failure
                mock_response = Mock()
                mock_response.json.return_value = {}
                mock_response.raise_for_status = Mock()
                mock_get.return_value = mock_response
                
                is_valid, company_name, price, source = await validator.validate_ticker("INVALID")
                
                assert is_valid is False
                assert company_name is None
                assert price is None
                assert source == "none"
    
    @pytest.mark.asyncio
    async def test_validate_ticker_network_error(self, validator):
        """Test network error handling"""
        with patch('yfinance.Ticker') as mock_ticker:
            # Mock yfinance exception
            mock_ticker.side_effect = Exception("Network error")
            
            with patch('requests.get') as mock_get:
                # Mock Finnhub exception
                mock_get.side_effect = Exception("Network error")
                
                is_valid, company_name, price, source = await validator.validate_ticker("AAPL")
                
                assert is_valid is False
                assert company_name is None
                assert price is None
                assert source == "none"

