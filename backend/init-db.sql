-- Initialize database schemas for microservices

-- Create schemas for each service
CREATE SCHEMA IF NOT EXISTS auth_schema;
CREATE SCHEMA IF NOT EXISTS stock_schema;
CREATE SCHEMA IF NOT EXISTS notification_schema;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA auth_schema TO stockadmin;
GRANT ALL PRIVILEGES ON SCHEMA stock_schema TO stockadmin;
GRANT ALL PRIVILEGES ON SCHEMA notification_schema TO stockadmin;

-- Set default search path
ALTER DATABASE stockvalidator SET search_path TO auth_schema, stock_schema, notification_schema, public;

-- ===== Stock Schema Tables =====

-- Stock Categories enum
CREATE TYPE stock_schema.stock_category AS ENUM ('far', 'near', 'almost_ready', 'ready');

-- Stock Subcategories enum (only for 'ready' stocks)
CREATE TYPE stock_schema.stock_subcategory AS ENUM ('pullback1', 'pullback2');

-- Stocks table
CREATE TABLE IF NOT EXISTS stock_schema.stocks (
    ticker VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    category stock_schema.stock_category NOT NULL,
    subcategory stock_schema.stock_subcategory,
    current_price NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by UUID REFERENCES auth_schema.users(id) NOT NULL,
    state_history JSONB DEFAULT '[]'::jsonb NOT NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_stocks_category ON stock_schema.stocks(category);
CREATE INDEX IF NOT EXISTS idx_stocks_created_by ON stock_schema.stocks(created_by);

-- Comments for documentation
COMMENT ON TABLE stock_schema.stocks IS 'Stocks tracked by the admin across different categories';
COMMENT ON COLUMN stock_schema.stocks.ticker IS 'Stock ticker symbol (e.g., AAPL, MSFT)';
COMMENT ON COLUMN stock_schema.stocks.category IS 'Stock category: far, near, almost_ready, or ready';
COMMENT ON COLUMN stock_schema.stocks.subcategory IS 'Subcategory for ready stocks: pullback1 or pullback2';
COMMENT ON COLUMN stock_schema.stocks.state_history IS 'JSONB array tracking category changes with timestamps';

