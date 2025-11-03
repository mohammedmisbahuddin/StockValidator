# API Flow Diagram - Ticker Validation

## Overview

This document explains the complete API flow from client to backend to external services for ticker validation.

---

## 1. Client-Facing APIs (Frontend → Your Backend)

### Admin APIs (Require Admin Role)

#### 1. `POST /stocks/validate`
**Purpose:** Validate a ticker before adding to system

**Request:**
```json
{
  "ticker": "AAPL"
}
```

**Response:**
```json
{
  "ticker": "AAPL",
  "is_valid": true,
  "company_name": "Apple Inc.",
  "current_price": 150.25,
  "source": "yfinance"
}
```

**External API Calls:** ✅ YES (yfinance → Finnhub fallback)

---

#### 2. `POST /stocks`
**Purpose:** Create a new stock entry

**Request:**
```json
{
  "ticker": "AAPL",
  "category": "ready",
  "subcategory": "pullback1"
}
```

**External API Calls:** ✅ YES (validates ticker and fetches company info)

---

#### 3. `GET /stocks`
**Purpose:** Get all stocks grouped by category

**External API Calls:** ❌ NO (database only)

---

#### 4. `GET /stocks/{ticker}`
**Purpose:** Get specific stock details

**External API Calls:** ❌ NO (database only)

---

#### 5. `PUT /stocks/{ticker}`
**Purpose:** Update stock category/subcategory

**External API Calls:** ❌ NO (database only)

---

#### 6. `DELETE /stocks/{ticker}`
**Purpose:** Delete a stock from system

**External API Calls:** ❌ NO (database only)

---

### User APIs (Require User Role)

#### 7. `GET /stocks/search/{ticker}`
**Purpose:** Search for a stock (with rate limiting)

**Example:** `GET /stocks/search/AAPL`

**Response:**
```json
{
  "found": true,
  "ticker": "AAPL",
  "stock": { "category": "ready", "subcategory": "pullback1", ... },
  "company_name": "Apple Inc.",
  "current_price": 150.25,
  "is_valid_ticker": true,
  "remaining_searches": 45,
  "message": "Stock found in system"
}
```

**External API Calls:** ✅ CONDITIONAL
- If ticker exists in database: NO external calls
- If ticker NOT in database: YES (validates with yfinance/Finnhub)

---

## 2. External APIs (Backend → Internet)

### PRIMARY: yfinance (Yahoo Finance)

**URL:** `https://query2.finance.yahoo.com/`  
**Method:** Python library (`yfinance`)  
**Authentication:** None required  
**Rate Limit:** ~2000 requests/hour per IP  
**Cost:** FREE ✅

**What we fetch:**
- Company name (longName, shortName)
- Current price (currentPrice, regularMarketPrice)
- Basic stock info

**Code Example:**
```python
import yfinance as yf

stock = yf.Ticker("AAPL")
info = stock.info
company_name = info.get('longName')         # "Apple Inc."
current_price = info.get('currentPrice')    # 150.25
```

---

### FALLBACK: Finnhub API

**URL:** `https://finnhub.io/api/v1/`  
**Method:** REST API  
**Authentication:** API Key required  
**Rate Limit:** 60 calls/minute (free tier)  
**Cost:** FREE tier available (requires signup at https://finnhub.io)

**Endpoints Used:**

#### 1. Company Profile
```
GET https://finnhub.io/api/v1/stock/profile2
Params: { symbol: "AAPL", token: "YOUR_API_KEY" }

Response:
{
  "name": "Apple Inc.",
  "ticker": "AAPL",
  "country": "US",
  "currency": "USD",
  ...
}
```

#### 2. Stock Quote
```
GET https://finnhub.io/api/v1/quote
Params: { symbol: "AAPL", token: "YOUR_API_KEY" }

Response:
{
  "c": 150.25,      // Current price
  "h": 152.00,      // High price of the day
  "l": 149.50,      // Low price of the day
  "o": 150.00,      // Open price
  ...
}
```

---

## 3. Complete Ticker Validation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js)                          │
│                                                                 │
│  User enters ticker: "AAPL"                                     │
│  Admin clicks "Validate Ticker"                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ POST /stocks/validate
                              │ { "ticker": "AAPL" }
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  YOUR BACKEND (FastAPI)                         │
│                      Port: 8002                                 │
│                                                                 │
│  Route Handler: stock_routes.py                                 │
│  ↓                                                               │
│  Service: TickerValidationService.validate_ticker("AAPL")       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Call validate_ticker()
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   STEP 1: Try yfinance                          │
│                                                                 │
│  → Python library: yf.Ticker("AAPL")                            │
│  → Fetch: stock.info                                            │
│  → Extract: company_name, current_price                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │                    │
                ✅ Success           ❌ Failed
                    │                    │
                    ↓                    ↓
         ┌──────────────────┐  ┌────────────────────────────┐
         │ Return data:     │  │  STEP 2: Try Finnhub      │
         │ - company_name   │  │                            │
         │ - current_price  │  │  Request 1:                │
         │ - source: "yf"   │  │  GET /stock/profile2       │
         └──────────────────┘  │  → Get company name        │
                    │           │                            │
                    │           │  Request 2:                │
                    │           │  GET /quote                │
                    │           │  → Get current price       │
                    │           └────────────────────────────┘
                    │                         │
                    │              ┌──────────┴──────────┐
                    │              │                     │
                    │          ✅ Success           ❌ Failed
                    │              │                     │
                    │              ↓                     ↓
                    │    ┌──────────────────┐  ┌─────────────────┐
                    │    │ Return data:     │  │ Return:         │
                    │    │ - company_name   │  │ - is_valid:false│
                    │    │ - current_price  │  │ - source: null  │
                    │    │ - source:"fhub"  │  └─────────────────┘
                    │    └──────────────────┘           │
                    │              │                    │
                    └──────────────┴────────────────────┘
                                   │
                                   ↓
┌─────────────────────────────────────────────────────────────────┐
│               BACKEND RESPONSE TO FRONTEND                      │
│                                                                 │
│  Success:                        Failed:                        │
│  {                               {                              │
│    "ticker": "AAPL",              "ticker": "INVALID",         │
│    "is_valid": true,              "is_valid": false,          │
│    "company_name": "Apple Inc.",  "company_name": null,       │
│    "current_price": 150.25,       "current_price": null,      │
│    "source": "yfinance"           "source": null,             │
│  }                                "error": "Invalid ticker"    │
│                                  }                              │
└─────────────────────────────────────────────────────────────────┘
                                   │
                                   ↓
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js)                          │
│                                                                 │
│  Display validation result to admin:                            │
│  ✅ "AAPL - Apple Inc. - $150.25"                              │
│  OR                                                             │
│  ❌ "Invalid ticker symbol"                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Which Client APIs Call External Services?

| Client API | External Calls? | External Service | Notes |
|------------|----------------|------------------|-------|
| `POST /stocks/validate` | ✅ YES | yfinance → Finnhub | Always validates ticker |
| `POST /stocks` | ✅ YES | yfinance → Finnhub | Validates during creation |
| `GET /stocks/search/{ticker}` | ✅ CONDITIONAL | yfinance → Finnhub | Only if not in database |
| `GET /stocks` | ❌ NO | None | Database only |
| `GET /stocks/{ticker}` | ❌ NO | None | Database only |
| `PUT /stocks/{ticker}` | ❌ NO | None | Database only |
| `DELETE /stocks/{ticker}` | ❌ NO | None | Database only |

---

## 5. Rate Limiting

### External API Rate Limits

| Service | Rate Limit | Cost | Notes |
|---------|-----------|------|-------|
| **yfinance** | ~2000 requests/hour per IP | FREE | No auth required |
| **Finnhub** | 60 requests/minute (free tier) | FREE tier available | API key required |

### Your Rate Limiting (Redis-based)

- **User search limit:** Configurable per user (default: 50 searches)
- **Admin control:** Can reset limits manually
- **Smart limiting:** Only valid searches count against limit
- **No auto-reset:** Admin controls when limits reset

---

## 6. Caching Strategy (Recommended for Production)

### Current Implementation

```python
# Already implemented in backend/shared/redis_client.py
async def get_ticker_cache(ticker: str) -> Optional[dict]:
    """Get cached ticker validation data"""
    key = f"ticker:{ticker.upper()}"
    return await self.get_cached(key)

async def set_ticker_cache(ticker: str, data: dict, ttl: int = 3600):
    """Cache ticker validation data (1 hour TTL)"""
    key = f"ticker:{ticker.upper()}"
    await self.set_cached(key, data, ttl)
```

### Benefits

- Reduces external API calls by 80-90%
- Faster response times
- Protects against rate limiting
- Saves on API quota

### When to Use

Cache ticker validation for:
- ✅ Popular tickers (AAPL, MSFT, GOOGL, etc.)
- ✅ Recently searched tickers
- ❌ Don't cache: Invalid tickers (always revalidate)

---

## 7. Error Handling

### yfinance Errors

```python
try:
    stock = yf.Ticker("AAPL")
    info = stock.info
except Exception as e:
    # Fall back to Finnhub
    logger.warning(f"yfinance failed: {e}")
```

**Common Errors:**
- `429 Too Many Requests` → Rate limited (use Finnhub)
- `404 Not Found` → Invalid ticker
- Network timeout → Retry with Finnhub

### Finnhub Errors

```python
try:
    response = requests.get(url, params=params, timeout=5)
    response.raise_for_status()
except Exception as e:
    # Return invalid ticker
    logger.error(f"Finnhub failed: {e}")
    return False, None, None
```

**Common Errors:**
- `401 Unauthorized` → Invalid API key
- `429 Too Many Requests` → Rate limited (wait or upgrade)
- `404 Not Found` → Invalid ticker

---

## 8. Environment Variables

Add to your `.env` file:

```bash
# Optional: Finnhub API Key (for fallback)
FINNHUB_API_KEY=your_finnhub_api_key_here

# Get free API key at: https://finnhub.io
```

---

## Summary

### Architecture

```
Frontend → Your Backend → External APIs (yfinance/Finnhub) → Your Backend → Frontend
```

### Client APIs: 7 total
- 3 admin APIs that call external services
- 4 admin APIs that use database only
- 1 user API that conditionally calls external services

### External APIs: 2 services
- **yfinance** (Yahoo Finance) - PRIMARY, FREE, no auth
- **Finnhub API** - FALLBACK, FREE tier, requires API key

### Data Fetched
- Company name (e.g., "Apple Inc.")
- Current stock price (e.g., $150.25)
- Ticker validation (exists/doesn't exist)

---

## Need Help?

- **yfinance docs:** https://pypi.org/project/yfinance/
- **Finnhub docs:** https://finnhub.io/docs/api
- **Finnhub signup (free):** https://finnhub.io

---

**Last Updated:** November 3, 2025  
**Services:** Auth (Phase 2) + Stock (Phase 3)  
**Status:** ✅ Operational

