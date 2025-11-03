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

