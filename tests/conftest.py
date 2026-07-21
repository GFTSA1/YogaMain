import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from httpx import AsyncClient, ASGITransport
from app.utils.auth.google import GoogleVerifier, GoogleIdentity, get_google_verifier


from app.main import app
from app.database import get_session

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
)


# SQLite disables foreign-key enforcement (and therefore ON DELETE CASCADE) by
# default; enable it per connection so tests exercise the same cascade behavior
# Postgres uses in production.
@event.listens_for(engine.sync_engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


AsyncTestingSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
async def db_session():
    async with AsyncTestingSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


class StubGoogleVerifier(GoogleVerifier):
    def __init__(self, identity_or_exc):
        self._payload = identity_or_exc

    def verify(self, id_token: str):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


@pytest.fixture
def google_override():
    def _install(payload):
        app.dependency_overrides[get_google_verifier] = lambda: StubGoogleVerifier(
            payload
        )

    yield _install
    app.dependency_overrides.pop(get_google_verifier, None)
