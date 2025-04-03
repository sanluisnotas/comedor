from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    future=True,
    echo=True  # Solo para desarrollo
)

AsyncSessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session