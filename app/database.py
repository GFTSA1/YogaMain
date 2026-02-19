import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL").replace(
    "postgresql://", "postgresql+asyncpg://"
)
engine = create_async_engine(
    DATABASE_URL, pool_pre_ping=True, echo=True
)  # echo=True for dev
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
