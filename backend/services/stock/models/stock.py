"""
Stock model for tracking stocks across different categories
"""
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ENUM as PG_ENUM
from sqlalchemy.orm import relationship
import sys
from pathlib import Path

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from shared.database import Base


class StockCategory(str, Enum):
    """Stock category enum"""
    FAR = "far"
    NEAR = "near"
    ALMOST_READY = "almost_ready"
    READY = "ready"


class StockSubcategory(str, Enum):
    """Stock subcategory enum (only for READY stocks)"""
    PULLBACK1 = "pullback1"
    PULLBACK2 = "pullback2"


class Stock(Base):
    """
    Stock model with state tracking
    
    Categories: far → near → almost_ready → ready
    Subcategories (only for ready): pullback1, pullback2
    """
    __tablename__ = "stocks"
    __table_args__ = (
        Index('idx_stocks_category', 'category'),
        Index('idx_stocks_created_by', 'created_by'),
        {"schema": "stock_schema"}
    )

    # Primary Key
    ticker = Column(String(10), primary_key=True)
    
    # Stock Information
    company_name = Column(String(255), nullable=False)
    # Use PostgreSQL ENUM type (existing types in database)
    category = Column(
        PG_ENUM('far', 'near', 'almost_ready', 'ready', name='stock_category', schema='stock_schema', create_type=False),
        nullable=False,
        index=True
    )
    subcategory = Column(
        PG_ENUM('pullback1', 'pullback2', name='stock_subcategory', schema='stock_schema', create_type=False),
        nullable=True
    )
    current_price = Column(Numeric(10, 2), nullable=True)
    
    # Audit Fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(PGUUID(as_uuid=True), ForeignKey('auth_schema.users.id'), nullable=False)
    
    # State History - JSONB array to track category changes
    # Format: [{"from": "far", "to": "near", "changed_at": "2024-01-01T00:00:00", "changed_by": "uuid"}]
    state_history = Column(JSONB, default=list, nullable=False)
    
    def __repr__(self):
        return f"<Stock(ticker={self.ticker}, company={self.company_name}, category={self.category})>"
    
    def add_state_change(self, from_category: str, to_category: str, changed_by: UUID):
        """
        Add a state change record to history
        
        Args:
            from_category: Previous category
            to_category: New category
            changed_by: UUID of user who made the change
        """
        if self.state_history is None:
            self.state_history = []
        
        change_record = {
            "from": from_category,
            "to": to_category,
            "changed_at": datetime.utcnow().isoformat(),
            "changed_by": str(changed_by)
        }
        
        # Append to existing history
        if isinstance(self.state_history, list):
            self.state_history.append(change_record)
        else:
            self.state_history = [change_record]
    
    @property
    def latest_state_change(self):
        """Get the most recent state change"""
        if self.state_history and len(self.state_history) > 0:
            return self.state_history[-1]
        return None

