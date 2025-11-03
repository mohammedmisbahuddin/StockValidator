"""
Test script to verify database and Redis connections
"""
import asyncio
import sys
from pathlib import Path
import sqlalchemy

# Add shared modules to path
sys.path.append(str(Path(__file__).parent))

from shared.config import settings
from shared.database import engine
from shared.redis_client import redis_client


async def test_postgres():
    """Test PostgreSQL connection"""
    print("\n🔍 Testing PostgreSQL connection...")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                sqlalchemy.text("SELECT version();")
            )
            version = result.scalar()
            print(f"✅ PostgreSQL connected!")
            print(f"   Version: {version}")
            return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False


async def test_redis():
    """Test Redis connection"""
    print("\n🔍 Testing Redis connection...")
    try:
        await redis_client.connect()
        pong = await redis_client.ping()
        if pong:
            print("✅ Redis connected!")
            
            # Test set/get
            await redis_client.client.set("test_key", "test_value")
            value = await redis_client.client.get("test_key")
            print(f"   Test write/read: {value}")
            await redis_client.client.delete("test_key")
            
            await redis_client.disconnect()
            return True
        else:
            print("❌ Redis connection failed: No response")
            return False
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False


async def main():
    """Run all connection tests"""
    print("=" * 60)
    print("🧪 Testing Infrastructure Connections")
    print("=" * 60)
    
    print(f"\n📋 Configuration:")
    print(f"   Database URL: {settings.database_url_computed}")
    print(f"   Redis URL: {settings.redis_url_computed}")
    
    # Test connections
    postgres_ok = await test_postgres()
    redis_ok = await test_redis()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print("=" * 60)
    print(f"   PostgreSQL: {'✅ PASS' if postgres_ok else '❌ FAIL'}")
    print(f"   Redis:      {'✅ PASS' if redis_ok else '❌ FAIL'}")
    print("=" * 60)
    
    if postgres_ok and redis_ok:
        print("\n✅ All tests passed! Infrastructure is ready.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check your Docker setup.")
        print("\nTo start infrastructure:")
        print("   docker-compose up -d postgres redis")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

