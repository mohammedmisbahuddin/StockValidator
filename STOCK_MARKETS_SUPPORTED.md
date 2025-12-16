# 📊 Stock Markets & Exchanges Supported for Ticker Validation

## Current Status

**Currently Active:** 🧪 **Mock Validator** (Development Mode)  
**Production Mode:** 🌐 **yfinance** (Primary) + **Finnhub** (Fallback)

---

## 🧪 Current Mode: Mock Validator

**Status:** ✅ Active (Development/Testing)  
**Configuration:** `USE_MOCK_VALIDATOR = True` in `backend/shared/config.py`

### Supported Markets in Mock Mode:

#### **1. US Stock Market (NYSE, NASDAQ)**
- **Format:** `TICKER` (no suffix needed)
- **Examples:** `AAPL`, `MSFT`, `GOOGL`, `AMZN`, `TSLA`, `META`, `NVDA`
- **Exchange:** New York Stock Exchange (NYSE) & NASDAQ

#### **2. Indian Stock Market - NSE (National Stock Exchange)**
- **Format:** `TICKER.NS`
- **Examples:** 
  - `RELIANCE.NS` - Reliance Industries Limited
  - `TCS.NS` - Tata Consultancy Services Limited
  - `INFY.NS` - Infosys Limited
  - `HDFCBANK.NS` - HDFC Bank Limited
  - `ICICIBANK.NS` - ICICI Bank Limited
  - `SBIN.NS` - State Bank of India
  - `ITC.NS` - ITC Limited
  - `WIPRO.NS` - Wipro Limited
  - `BHARTIARTL.NS` - Bharti Airtel Limited
  - `HINDUNILVR.NS` - Hindustan Unilever Limited

#### **3. Indian Stock Market - BSE (Bombay Stock Exchange)**
- **Format:** `TICKER.BO`
- **Examples:**
  - `RELIANCE.BO` - Reliance Industries Limited
  - `TCS.BO` - Tata Consultancy Services Limited
  - `INFY.BO` - Infosys Limited

### Auto-Detection Feature:
- ✅ If user enters ticker **without suffix** (e.g., `TCS`), system automatically tries:
  1. First: `TCS.NS` (NSE)
  2. Then: `TCS.BO` (BSE)
- ✅ This makes it easier for users - they don't need to remember exchange suffixes!

---

## 🌐 Production Mode: Real APIs

When `USE_MOCK_VALIDATOR = False`, the system uses real market data APIs:

### **PRIMARY: yfinance (Yahoo Finance)**

**What is yfinance?**
- Python library that accesses Yahoo Finance data
- **FREE** - No API key required
- **Rate Limit:** ~2000 requests/hour per IP
- **Data Source:** Yahoo Finance (aggregates data from multiple exchanges)

**Supported Markets:**

#### **1. US Stock Markets** ✅
- **NYSE (New York Stock Exchange)**
  - Format: `TICKER` (e.g., `AAPL`, `MSFT`, `JPM`)
  - Examples: Apple, Microsoft, JPMorgan Chase
  
- **NASDAQ**
  - Format: `TICKER` (e.g., `GOOGL`, `AMZN`, `TSLA`)
  - Examples: Google, Amazon, Tesla

- **Other US Exchanges**
  - AMEX (American Stock Exchange)
  - OTC (Over-The-Counter) markets

#### **2. Indian Stock Markets** ✅
- **NSE (National Stock Exchange)**
  - Format: `TICKER.NS`
  - Examples: `RELIANCE.NS`, `TCS.NS`, `INFY.NS`
  - Currency: INR (Indian Rupees)
  
- **BSE (Bombay Stock Exchange)**
  - Format: `TICKER.BO`
  - Examples: `RELIANCE.BO`, `TCS.BO`
  - Currency: INR (Indian Rupees)

#### **3. Other International Markets** ✅
yfinance supports many more exchanges globally:

- **London Stock Exchange (UK)**
  - Format: `TICKER.L`
  - Example: `VOD.L` (Vodafone)
  
- **Tokyo Stock Exchange (Japan)**
  - Format: `TICKER.T`
  - Example: `7203.T` (Toyota)
  
- **Toronto Stock Exchange (Canada)**
  - Format: `TICKER.TO`
  - Example: `RY.TO` (Royal Bank of Canada)
  
- **Australian Stock Exchange**
  - Format: `TICKER.AX`
  - Example: `CBA.AX` (Commonwealth Bank)
  
- **Hong Kong Stock Exchange**
  - Format: `TICKER.HK`
  - Example: `0700.HK` (Tencent)
  
- **And many more...** (yfinance supports 100+ exchanges worldwide)

**Exchange Suffix Reference:**
```
.NS  = NSE (India)
.BO  = BSE (India)
.L   = London Stock Exchange (UK)
.T   = Tokyo Stock Exchange (Japan)
.TO  = Toronto Stock Exchange (Canada)
.AX  = Australian Stock Exchange
.HK  = Hong Kong Stock Exchange
.N   = NYSE (sometimes)
.O   = Other exchanges
```

---

### **FALLBACK: Finnhub API**

**What is Finnhub?**
- Professional financial data API
- **FREE tier:** 60 API calls/minute
- **Requires:** API key (signup at https://finnhub.io)
- **Better for:** Production environments with higher volume

**Supported Markets:**

#### **1. US Stock Markets** ✅
- NYSE, NASDAQ, AMEX
- Format: `TICKER` (e.g., `AAPL`, `MSFT`)

#### **2. Indian Stock Markets** ✅
- **NSE (National Stock Exchange)**
  - Format: `IC:TICKER` or `TICKER.NS`
  - Example: `IC:RELIANCE` or `RELIANCE.NS`
  
- **BSE (Bombay Stock Exchange)**
  - Format: `BS:STOCK_CODE` (uses numeric codes)
  - Example: `BS:500325` (Reliance Industries)

#### **3. Global Markets** ✅
Finnhub supports 50+ exchanges worldwide:
- European markets (LSE, Euronext, etc.)
- Asian markets (Tokyo, Hong Kong, Singapore, etc.)
- Australian markets
- And more...

**Finnhub Exchange Codes:**
```
US  = US Markets (NYSE, NASDAQ)
IC  = NSE (India)
BS  = BSE (India)
L   = London Stock Exchange
T   = Tokyo Stock Exchange
... (many more)
```

---

## 🔄 Validation Flow

### **Current Flow (Mock Mode):**
```
User Input: "TCS"
    ↓
1. Check Mock Database for "TCS"
    ↓ (Not found)
2. Try "TCS.NS" (NSE)
    ↓ (Found!)
✅ Return: TCS.NS - Tata Consultancy Services Limited
```

### **Production Flow (Real APIs):**
```
User Input: "TCS"
    ↓
1. Try yfinance with "TCS" (US market)
    ↓ (Not found)
2. Try yfinance with "TCS.NS" (NSE)
    ↓ (Found!)
✅ Return: TCS.NS - Tata Consultancy Services Limited, ₹3750.00
```

**If yfinance fails:**
```
3. Try Finnhub with "TCS.NS"
    ↓ (Found!)
✅ Return: TCS.NS - Tata Consultancy Services Limited
```

---

## 📋 Summary Table

| Market/Exchange | Format | Example | Mock Mode | yfinance | Finnhub |
|----------------|--------|---------|-----------|----------|---------|
| **US - NYSE** | `TICKER` | `AAPL` | ✅ | ✅ | ✅ |
| **US - NASDAQ** | `TICKER` | `GOOGL` | ✅ | ✅ | ✅ |
| **India - NSE** | `TICKER.NS` | `RELIANCE.NS` | ✅ | ✅ | ✅ |
| **India - BSE** | `TICKER.BO` | `TCS.BO` | ✅ | ✅ | ✅ |
| **UK - LSE** | `TICKER.L` | `VOD.L` | ❌ | ✅ | ✅ |
| **Japan - TSE** | `TICKER.T` | `7203.T` | ❌ | ✅ | ✅ |
| **Canada - TSX** | `TICKER.TO` | `RY.TO` | ❌ | ✅ | ✅ |
| **Australia - ASX** | `TICKER.AX` | `CBA.AX` | ❌ | ✅ | ✅ |
| **Hong Kong - HKEX** | `TICKER.HK` | `0700.HK` | ❌ | ✅ | ✅ |

---

## 🎯 What Markets Are Currently Validated?

### **In Mock Mode (Current):**
- ✅ **US Stocks:** AAPL, MSFT, GOOGL, AMZN, TSLA, META, NVDA
- ✅ **Indian Stocks (NSE):** RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS, ICICIBANK.NS, SBIN.NS, ITC.NS, WIPRO.NS, BHARTIARTL.NS, HINDUNILVR.NS
- ✅ **Indian Stocks (BSE):** RELIANCE.BO, TCS.BO, INFY.BO
- ✅ **Auto-detection:** Tries NSE/BSE if no suffix provided

### **In Production Mode (Real APIs):**
- ✅ **US Markets:** All NYSE & NASDAQ stocks
- ✅ **Indian Markets:** All NSE & BSE stocks
- ✅ **Global Markets:** 100+ exchanges worldwide (via yfinance)
- ✅ **Auto-detection:** Enabled for Indian stocks

---

## 🔧 How to Switch Between Modes

### **Use Mock Validator (Current - Development):**
```python
# In backend/shared/config.py
USE_MOCK_VALIDATOR: bool = True
```

### **Use Real APIs (Production):**
```python
# In backend/shared/config.py
USE_MOCK_VALIDATOR: bool = False

# Optional: Add Finnhub API key for fallback
FINNHUB_API_KEY: str = "your_api_key_here"
```

---

## 📝 Notes

1. **Mock Mode:** Only validates pre-defined tickers (no real API calls)
2. **Production Mode:** Validates ANY valid ticker from supported exchanges
3. **Auto-Detection:** Currently enabled for Indian stocks (tries .NS then .BO)
4. **Rate Limits:** 
   - Mock: No limits
   - yfinance: ~2000/hour
   - Finnhub: 60/minute (free tier)
5. **Currency:** 
   - US stocks: USD ($)
   - Indian stocks: INR (₹)
   - Other markets: Respective currencies

---

## 🚀 Recommendations

### **For Development/Testing:**
- ✅ Use Mock Validator (current setup)
- ✅ Fast, no rate limits
- ✅ Predictable results

### **For Production:**
- ✅ Use Real APIs (`USE_MOCK_VALIDATOR = False`)
- ✅ Add Finnhub API key for reliability
- ✅ Consider caching to reduce API calls
- ✅ Monitor rate limits

### **For Indian Stock Focus:**
- ✅ Consider adding NSEPy library (India-specific, no rate limits)
- ✅ Better reliability for Indian markets
- ✅ Direct NSE/BSE access

---

**Last Updated:** December 16, 2025  
**Current Mode:** 🧪 Mock Validator  
**Supported Markets:** US (NYSE/NASDAQ) + India (NSE/BSE)  
**Auto-Detection:** ✅ Enabled for Indian stocks

