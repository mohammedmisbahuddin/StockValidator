"""
Pytest configuration and fixtures for Notification service tests
"""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
import sys
from pathlib import Path
from uuid import uuid4

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

from shared.database import Base
from shared.redis_client import RedisClient
from models.notification import Notification, UserNotification
from shared.models.user import User


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://stockadmin:stockpass123@localhost:5433/stockvalidator_test"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )
    
    # Create test schema and tables
    async with engine.begin() as conn:
        import sqlalchemy
        await conn.execute(sqlalchemy.text("CREATE SCHEMA IF NOT EXISTS notification_schema"))
        await conn.execute(sqlalchemy.text("CREATE SCHEMA IF NOT EXISTS auth_schema"))
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine):
    """Create a new database session for each test"""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def redis_client():
    """Create Redis client for tests"""
    client = RedisClient()
    await client.connect()
    
    yield client
    
    # Cleanup: flush test keys
    if client.client:
        await client.client.flushdb()
    await client.disconnect()


@pytest.fixture
async def sample_admin_user(db_session):
    """Create a sample admin user for tests"""
    from shared.auth_utils import hash_password
    
    admin = User(
        id=uuid4(),
        email="admin@test.com",
        username="testadmin",
        password_hash=hash_password("Admin@123"),
        role="admin",
        search_limit=50,
        searches_used=0
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


@pytest.fixture
async def sample_user(db_session):
    """Create a sample regular user for tests"""
    from shared.auth_utils import hash_password
    
    user = User(
        id=uuid4(),
        email="user@test.com",
        username="testuser",
        password_hash=hash_password("User@123"),
        role="user",
        search_limit=50,
        searches_used=0
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def sample_notification_data():
    """Sample notification data for tests"""
    return {
        "title": "Test Notification",
        "message": "This is a test notification message"
    }

