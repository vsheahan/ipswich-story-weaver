"""Test fixtures and configuration."""

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.main import app
from app.models.news import NewsItem


# Use SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """Create a test client with database dependency override."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_news_items(db_session: AsyncSession) -> list[NewsItem]:
    """Create sample news items for testing."""
    news_items = [
        NewsItem(
            headline="Ipswich Town Meeting Approves New Budget",
            summary="The annual town meeting approved a $50 million budget for the upcoming fiscal year.",
            article_url="https://thelocalnews.news/ipswich/budget-approved",
            author="Jane Smith",
            category_label="Ipswich",
            published_at=datetime(2024, 12, 1, 10, 0, 0),
            fetched_at=datetime(2024, 12, 1, 12, 0, 0),
        ),
        NewsItem(
            headline="Crane Beach Opens for Winter Walking",
            summary="Crane Beach now open for off-season visitors with reduced parking fees.",
            article_url="https://thelocalnews.news/ipswich/crane-beach-winter",
            author="John Doe",
            category_label="Ipswich",
            published_at=datetime(2024, 11, 28, 9, 0, 0),
            fetched_at=datetime(2024, 11, 28, 10, 0, 0),
        ),
        NewsItem(
            headline="Historic Choate Bridge Restoration Complete",
            summary="The oldest stone arch bridge in America has been fully restored.",
            article_url="https://thelocalnews.news/ipswich/choate-bridge",
            author=None,
            category_label="Ipswich",
            published_at=datetime(2024, 11, 25, 14, 30, 0),
            fetched_at=datetime(2024, 11, 25, 15, 0, 0),
        ),
    ]

    for news_item in news_items:
        db_session.add(news_item)

    await db_session.commit()

    for news_item in news_items:
        await db_session.refresh(news_item)

    return news_items
