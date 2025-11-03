# Stock Service PostgreSQL Enum Fix

## Problem

The Stock Service `/stocks` endpoint was failing with the error:
```
invalid input value for enum stock_category: "NEAR"
```

## Root Cause

SQLAlchemy was using the Python enum's **name** (e.g., `"NEAR"`, `"ALMOST_READY"`) instead of its **value** (e.g., `"near"`, `"almost_ready"`) when inserting records into the PostgreSQL database.

The database enum types were defined with lowercase values:
```sql
CREATE TYPE stock_schema.stock_category AS ENUM ('far', 'near', 'almost_ready', 'ready');
```

But the Python enum had uppercase names:
```python
class StockCategory(str, Enum):
    FAR = "far"
    NEAR = "near"
    ALMOST_READY = "almost_ready"
    READY = "ready"
```

## Solution

Changed the Stock model (`backend/services/stock/models/stock.py`) to use PostgreSQL's `ENUM` type directly:

```python
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

category = Column(
    PG_ENUM('far', 'near', 'almost_ready', 'ready', 
            name='stock_category', 
            schema='stock_schema', 
            create_type=False),  # Don't create, use existing type
    nullable=False,
    index=True
)
```

## Key Changes

1. **`backend/services/stock/models/stock.py`**:
   - Changed from `SQLEnum(StockCategory)` to `PG_ENUM(...)` with explicit values
   - Added `schema='stock_schema'` to reference the correct PostgreSQL schema
   - Added `create_type=False` to use existing database enum types

2. **`backend/services/stock/services/stock_service.py`**:
   - Updated `create_stock()` to convert enum to string value
   - Updated `update_stock()` to handle string values from database
   - Fixed `get_all_stocks()` to handle category as string (not enum)

## Verification

All Stock Service endpoints now work correctly:

✅ **POST /stocks** - Create new stock
```bash
curl -X POST http://localhost:8002/stocks \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"ticker":"AAPL","company_name":"Apple Inc.","category":"ready","subcategory":"pullback1","current_price":150.25}'
```

✅ **GET /stocks** - List all stocks grouped by category
```bash
curl http://localhost:8002/stocks -H "Authorization: Bearer $TOKEN"
# Response: { "far": [], "near": [...], "almost_ready": [], "ready": [...], "total": 2 }
```

✅ **GET /stocks/{ticker}** - Get specific stock
```bash
curl http://localhost:8002/stocks/AAPL -H "Authorization: Bearer $TOKEN"
```

✅ **PUT /stocks/{ticker}** - Update stock
```bash
curl -X PUT http://localhost:8002/stocks/MSFT \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"category":"almost_ready"}'
```

✅ **DELETE /stocks/{ticker}** - Delete stock
```bash
curl -X DELETE http://localhost:8002/stocks/AAPL \
  -H "Authorization: Bearer $TOKEN"
```

## Lessons Learned

1. **SQLAlchemy Enums**: When using enums with SQLAlchemy and PostgreSQL, explicitly define the enum values in the column definition to avoid name/value confusion.

2. **Schema-Qualified Enums**: PostgreSQL enum types in non-public schemas require `schema='schema_name'` in the SQLAlchemy column definition.

3. **Existing Database Types**: Use `create_type=False` when the enum type already exists in the database to prevent SQLAlchemy from trying to create it again.

4. **String vs Enum Handling**: When reading from the database, PostgreSQL enums are returned as strings, not Python enum objects. Handle both cases in the service layer.

## Date Fixed

November 3, 2025

## Status

✅ **RESOLVED** - All `/stocks` endpoints working correctly.

