from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from shared.config import settings
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
engine = create_async_engine(
    settings.database_url,
    echo=True,
    pool_size=20,
    max_overflow=0,
)

#sessin creation 
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

#get Db
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()    
