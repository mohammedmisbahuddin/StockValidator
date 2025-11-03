"""
Pydantic schemas for Stock service
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal

from models.stock import StockCategory, StockSubcategory


# ===== Base Schemas =====

class StockBase(BaseModel):
    """Base stock schema with common fields"""
    ticker: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    company_name: str = Field(..., min_length=1, max_length=255, description="Company name")
    category: StockCategory = Field(..., description="Stock category")
    subcategory: Optional[StockSubcategory] = Field(None, description="Subcategory (only for 'ready' stocks)")
    current_price: Optional[Decimal] = Field(None, ge=0, description="Current market price")
    
    @field_validator('ticker')
    @classmethod
    def ticker_uppercase(cls, v: str) -> str:
        """Convert ticker to uppercase"""
        return v.upper().strip()
    
    @field_validator('subcategory')
    @classmethod
    def validate_subcategory(cls, v: Optional[StockSubcategory], info) -> Optional[StockSubcategory]:
        """Subcategory can only be set if category is 'ready'"""
        if v is not None:
            # Get category from the model being validated
            category = info.data.get('category')
            if category != StockCategory.READY:
                raise ValueError("Subcategory can only be set for 'ready' stocks")
        return v


# ===== Request Schemas =====

class StockCreate(StockBase):
    """Schema for creating a new stock"""
    pass


class StockUpdate(BaseModel):
    """Schema for updating a stock"""
    company_name: Optional[str] = Field(None, min_length=1, max_length=255, description="Company name")
    category: Optional[StockCategory] = Field(None, description="Stock category")
    subcategory: Optional[StockSubcategory] = Field(None, description="Subcategory (only for 'ready' stocks)")
    current_price: Optional[Decimal] = Field(None, ge=0, description="Current market price")
    
    @field_validator('subcategory')
    @classmethod
    def validate_subcategory(cls, v: Optional[StockSubcategory], info) -> Optional[StockSubcategory]:
        """Subcategory can only be set if category is 'ready'"""
        if v is not None:
            category = info.data.get('category')
            if category and category != StockCategory.READY:
                raise ValueError("Subcategory can only be set for 'ready' stocks")
        return v


# ===== Response Schemas =====

class StateChange(BaseModel):
    """Schema for a single state change record"""
    from_category: str = Field(..., alias="from")
    to_category: str = Field(..., alias="to")
    changed_at: str
    changed_by: str
    
    model_config = {"populate_by_name": True}


class StockResponse(StockBase):
    """Schema for stock response"""
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    state_history: List[Dict[str, Any]] = Field(default_factory=list, description="History of category changes")
    
    model_config = {"from_attributes": True}


class StockListResponse(BaseModel):
    """Schema for list of stocks grouped by category"""
    far: List[StockResponse] = Field(default_factory=list)
    near: List[StockResponse] = Field(default_factory=list)
    almost_ready: List[StockResponse] = Field(default_factory=list)
    ready: List[StockResponse] = Field(default_factory=list)
    total: int = Field(..., description="Total number of stocks")


# ===== Validation Schemas =====

class TickerValidationRequest(BaseModel):
    """Schema for ticker validation request"""
    ticker: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    
    @field_validator('ticker')
    @classmethod
    def ticker_uppercase(cls, v: str) -> str:
        """Convert ticker to uppercase"""
        return v.upper().strip()


class TickerValidationResponse(BaseModel):
    """Schema for ticker validation response"""
    ticker: str
    is_valid: bool
    company_name: Optional[str] = None
    current_price: Optional[Decimal] = None
    error: Optional[str] = None
    source: Optional[str] = Field(None, description="Data source: yfinance or finnhub")


# ===== Search Schemas =====

class StockSearchRequest(BaseModel):
    """Schema for stock search request"""
    ticker: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    
    @field_validator('ticker')
    @classmethod
    def ticker_uppercase(cls, v: str) -> str:
        """Convert ticker to uppercase"""
        return v.upper().strip()


class StockSearchResponse(BaseModel):
    """Schema for stock search response"""
    found: bool
    ticker: str
    stock: Optional[StockResponse] = None
    company_name: Optional[str] = None
    current_price: Optional[Decimal] = None
    is_valid_ticker: bool = Field(..., description="Whether ticker exists in market")
    remaining_searches: int = Field(..., description="User's remaining search limit")
    message: Optional[str] = None


# ===== Rate Limit Schemas =====

class RateLimitInfo(BaseModel):
    """Schema for rate limit information"""
    user_id: UUID
    username: str
    search_limit: int
    searches_used: int
    remaining_searches: int
    last_reset_at: Optional[datetime] = None


class RateLimitUpdate(BaseModel):
    """Schema for updating user's rate limit"""
    search_limit: int = Field(..., ge=0, description="New search limit")


class UniversalRateLimitUpdate(BaseModel):
    """Schema for updating universal rate limit"""
    search_limit: int = Field(..., ge=0, description="New universal search limit for all users")


class RateLimitResetResponse(BaseModel):
    """Schema for rate limit reset response"""
    success: bool
    message: str
    affected_users: int = Field(..., description="Number of users affected")

