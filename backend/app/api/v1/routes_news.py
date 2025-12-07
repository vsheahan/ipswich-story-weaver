"""News API routes (read-only public endpoints)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.news import (
    NewsItemResponse,
    NewsListResponse,
    RefreshNewsResponse,
)
from app.services.news_service import NewsService

router = APIRouter()


@router.get("/recent", response_model=NewsListResponse)
async def get_recent_news(
    limit: int = Query(default=5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
) -> NewsListResponse:
    """Get recent Ipswich news items.

    This is a read-only endpoint that returns cached news items
    from The Local News Ipswich category.
    """
    news_service = NewsService(db)
    news_items = await news_service.get_recent_news_items(limit=limit)

    return NewsListResponse(
        news_items=[
            NewsItemResponse(
                id=item.id,
                headline=item.headline,
                summary=item.summary,
                article_url=item.article_url,
                author=item.author,
                category_label=item.category_label,
                published_at=item.published_at,
                fetched_at=item.fetched_at,
            )
            for item in news_items
        ],
        total=len(news_items),
    )
