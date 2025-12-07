"""Admin API routes (internal/development use only).

These endpoints are for development and administrative purposes.
In production, these should be protected or disabled.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.schemas.news import RefreshNewsResponse
from app.services.news_service import NewsService

router = APIRouter()
settings = get_settings()


@router.post("/refresh-news", response_model=RefreshNewsResponse)
async def refresh_ipswich_news(
    db: AsyncSession = Depends(get_db),
) -> RefreshNewsResponse:
    """Refresh Ipswich news from The Local News.

    This endpoint triggers a scrape of the Ipswich category page
    and updates the news_items database table.

    For production use, this should be called via a scheduled task
    rather than a public endpoint.
    """
    news_service = NewsService(db)
    updated_items = await news_service.fetch_and_update_ipswich_news()

    return RefreshNewsResponse(
        success=True,
        message=f"Successfully refreshed Ipswich news from The Local News",
        items_updated=len(updated_items),
    )
