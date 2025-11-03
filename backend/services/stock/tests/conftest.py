"""
Pytest configuration and fixtures for Stock service tests
"""
import pytest
import sys
from pathlib import Path

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from shared.database import Base, engine
from shared.redis_client import redis_client


@pytest.fixture(scope="function")
async def test_db():
    """Create test database session"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def test_redis():
    """Create test Redis client"""
    yield redis_client
    
    # Cleanup test keys
    await redis_client.flushdb()

