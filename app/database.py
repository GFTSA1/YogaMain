import os
import ssl

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

load_dotenv()

DATABASE_URL = (
    os.environ.get("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")
).split("?")[0]

ssl_context = ssl.create_default_context()

engine = create_async_engine(
    DATABASE_URL, pool_pre_ping=True, connect_args={"ssl": ssl_context}, echo=True
)  # echo=True for dev
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
