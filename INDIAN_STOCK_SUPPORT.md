# Indian Stock Market Support

## Current Status

### ✅ **YES - Both yfinance and Finnhub Support Indian Stocks**

## Indian Stock Ticker Format

Indian stocks trade on two major exchanges:
- **NSE (National Stock Exchange)** - Suffix: `.NS`
- **BSE (Bombay Stock Exchange)** - Suffix: `.BO`

### Examples:
```
RELIANCE.NS   → Reliance Industries (NSE)
TCS.NS        → Tata Consultancy Services (NSE)
INFY.NS       → Infosys (NSE)
HDFCBANK.NS   → HDFC Bank (NSE)
TATAMOTORS.BO → Tata Motors (BSE)
```

## API Support for Indian Stocks

### 1. **yfinance** (Primary - FREE) ✅
- **Supports:** NSE (`.NS`) and BSE (`.BO`)
- **Format:** `TICKER.NS` or `TICKER.BO`
- **Data Available:**
  - Company name
  - Current price (in INR)
  - Historical data
  - Market cap, volume, etc.
- **Rate Limits:** Free but rate-limited (429 errors possible)
- **Documentation:** https://pypi.org/project/yfinance/

**Example Usage:**
```python
import yfinance as yf

# NSE stocks
reliance = yf.Ticker("RELIANCE.NS")
tcs = yf.Ticker("TCS.NS")

# BSE stocks
infosys = yf.Ticker("INFY.BO")
```

### 2. **Finnhub** (Fallback - Requires API Key) ✅
- **Supports:** NSE and BSE
- **Exchange Codes:**
  - NSE: `IC` (e.g., `IC:RELIANCE`)
  - BSE: `BS` (e.g., `BS:500325`)
- **Free Tier:** 60 API calls/minute
- **Pricing:** Free tier available, paid plans for more requests
- **Documentation:** https://finnhub.io/docs/api/indian-stock-exchanges

### 3. **Alternative: NSEPy** (India-Specific) 🆕
- **Python Library:** `nsepy`
- **Free:** No API key needed
- **Direct NSE/BSE Access:** Real-time and historical data
- **Better for Indian Markets:** No rate limiting like yfinance

## Recommended Approach for Indian Stocks

### Option 1: **Enhance Current Implementation** (Recommended)

Add automatic exchange suffix detection:

```python
async def validate_indian_ticker(self, ticker: str) -> Tuple[bool, Optional[str], Optional[Decimal], Optional[str]]:
    """
    Validate Indian stock ticker with automatic exchange detection
    
    Tries both NSE (.NS) and BSE (.BO) if no suffix provided
    """
    ticker = ticker.upper().strip()
    
    # If already has suffix, use as-is
    if ticker.endswith('.NS') or ticker.endswith('.BO'):
        return await self.validate_ticker(ticker)
    
    # Try NSE first (larger exchange)
    is_valid, name, price, source = await self.validate_ticker(f"{ticker}.NS")
    if is_valid:
        return is_valid, name, price, source
    
    # Fallback to BSE
    is_valid, name, price, source = await self.validate_ticker(f"{ticker}.BO")
    return is_valid, name, price, source
```

### Option 2: **Add NSEPy as Third Fallback** (Best for Indian Markets)

Install:
```bash
pip install nsepy
```

Advantages:
- Direct NSE/BSE access
- No rate limiting
- More reliable for Indian stocks
- Historical data support

## Implementation Changes Required

### 1. **Update `ticker_validator.py`**

Add Indian stock auto-detection:

```python
class TickerValidationService:
    def __init__(self, finnhub_api_key: Optional[str] = None, default_exchange: str = "NS"):
        self.finnhub_api_key = finnhub_api_key or ""
        self.default_exchange = default_exchange  # "NS" for NSE, "BO" for BSE
    
    async def validate_ticker(self, ticker: str) -> Tuple[bool, Optional[str], Optional[Decimal], Optional[str]]:
        ticker = ticker.upper().strip()
        
        # Auto-add Indian exchange suffix if not present
        if not any(ticker.endswith(suffix) for suffix in ['.NS', '.BO', '.N', '.O']):
            # Assume Indian stock if no exchange suffix
            ticker = f"{ticker}.{self.default_exchange}"
        
        # Continue with existing validation logic...
```

### 2. **Update Frontend/User Input**

**Option A: User specifies exchange**
```
Ticker: RELIANCE
Exchange: [NSE ▼] (dropdown: NSE, BSE, US)
```

**Option B: Auto-detect (recommended)**
```
Ticker: RELIANCE  → Automatically tries RELIANCE.NS, then RELIANCE.BO
Ticker: AAPL      → Automatically tries AAPL (US stock)
```

### 3. **Database Schema - Already Compatible ✅**

Current schema supports Indian stocks:
```sql
ticker VARCHAR(10) PRIMARY KEY  -- Can store "RELIANCE.NS"
company_name VARCHAR(255)       -- Can store "Reliance Industries Limited"
```

**Note:** If ticker length becomes an issue, increase to `VARCHAR(15)`:
```sql
ALTER TABLE stock_schema.stocks ALTER COLUMN ticker TYPE VARCHAR(15);
```

## Currency Handling

Indian stocks are priced in **INR (Indian Rupees)**, not USD.

### Recommendation:
Add a `currency` column to the stocks table:

```sql
ALTER TABLE stock_schema.stocks ADD COLUMN currency VARCHAR(3) DEFAULT 'INR';
```

Update the schema:
```python
class Stock(Base):
    # ... existing fields ...
    current_price = Column(Numeric(10, 2), nullable=True)
    currency = Column(String(3), default='INR', nullable=False)  # NEW
```

## Testing Indian Stocks

### Test Case 1: NSE Stocks
```bash
# Test with NSE suffix
curl -X POST http://localhost:8002/stocks \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "ticker": "RELIANCE.NS",
    "company_name": "Reliance Industries",
    "category": "ready",
    "current_price": 2450.75
  }'
```

### Test Case 2: Auto-Detection
```python
# Should automatically try RELIANCE.NS
await validate_ticker("RELIANCE")
```

### Popular Indian Stocks for Testing:
- **RELIANCE.NS** - Reliance Industries
- **TCS.NS** - Tata Consultancy Services
- **INFY.NS** - Infosys
- **HDFCBANK.NS** - HDFC Bank
- **ICICIBANK.NS** - ICICI Bank
- **SBIN.NS** - State Bank of India
- **ITC.NS** - ITC Limited

## Action Items

### Phase 1: Minimal Changes (Quick Fix) ✅
1. Update ticker validation to accept `.NS` and `.BO` suffixes
2. Test with Indian stocks
3. Update JMeter tests with Indian tickers

### Phase 2: Enhanced Support (Recommended) 📋
1. Add auto-detection for Indian stocks
2. Add `currency` column to database
3. Update frontend to show currency
4. Add exchange selection dropdown

### Phase 3: Production-Ready (Optional) 🎯
1. Add NSEPy as third fallback
2. Implement caching to avoid rate limits
3. Add exchange-specific validation rules
4. Support for Indian stock market hours

## Conclusion

**✅ Your current implementation WILL WORK with Indian stocks!**

**Required Changes:**
1. **Immediate:** Ensure tickers include `.NS` or `.BO` suffix
2. **Short-term:** Add auto-detection for Indian stocks
3. **Long-term:** Consider adding NSEPy for better Indian market coverage

**No major code changes needed** - just ticker format awareness!

---

**Last Updated:** November 3, 2025  
**Status:** ✅ **Indian stocks supported with minor configuration**

