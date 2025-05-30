#!/usr/bin/env python3
"""
Test script to verify database connection with new credentials
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from shared.config import settings

async def test_connection():
    """Test database connection"""
    try:
        print(f"Testing connection to: {settings.database_url}")
        
        # Create engine
        engine = create_async_engine(settings.database_url)
        
        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute("SELECT 1 as test")
            row = result.fetchone()
            print(f"✅ Database connection successful! Test query result: {row[0]}")
            
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    # Load environment variables from config.env
    if os.path.exists("config.env"):
        with open("config.env", "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
    
    success = asyncio.run(test_connection())
    exit(0 if success else 1) 