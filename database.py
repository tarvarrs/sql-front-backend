from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from config import settings
import asyncio

Base = declarative_base()

def create_async_engine_with_retry(db_url: str, echo: bool = True) -> AsyncEngine:
    try:
        engine = create_async_engine(
            db_url,
            echo=echo,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_timeout=30
        )
        return engine
    except Exception as e:
        raise RuntimeError(f"Failed to create database engine: {str(e)}") from e

engine = create_async_engine_with_retry(settings.DATABASE_URL)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    future=True
)

async def get_db():
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        raise e
    finally:
        await session.close()

async def test_connection():
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            print("Database connection successful")
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise

# asyncio.run(test_connection())