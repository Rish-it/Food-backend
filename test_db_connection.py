import asyncio
import logging
from sqlalchemy import text
from shared.database import engine
from shared.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test():
    try:
        logger.info(f"Attempting to connect to database with URL: {settings.database_url}")
        async with engine.connect() as conn:
            result = await conn.execute(text('SELECT 1'))
            print('Database connection successful!')
            # Print the result
            row = result.scalar()
            print(f'Test query result: {row}')
    except Exception as e:
        logger.error(f'Database connection failed: {str(e)}', exc_info=True)
        raise

if __name__ == "__main__":
    try:
        asyncio.run(test())
    except Exception as e:
        print(f"Test failed: {str(e)}")
        exit(1) 