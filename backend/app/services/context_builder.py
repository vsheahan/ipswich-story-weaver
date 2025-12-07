"""Context builder for assembling story generation context."""

from datetime import date
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.schemas.news import NewsItemBrief
from app.schemas.story import (
    NewsContext,
    SeasonContext,
    StoryContext,
)
from app.services.weather_service import WeatherService
from app.services.tide_service import TideService
from app.services.news_service import NewsService

settings = get_settings()


class ContextBuilder:
    """Builds the complete context needed for story generation."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.weather_service = WeatherService(db)
        self.tide_service = TideService()
        self.news_service = NewsService(db)

    async def build_context(
        self,
        target_date: date,
        include_news: bool = True,
        max_news_items: Optional[int] = None,
    ) -> StoryContext:
        """Build complete story context for a given date."""
        max_news_items = max_news_items or settings.max_news_items_per_story

        # Gather all context components
        weather = await self.weather_service.get_weather_for_date(target_date)
        tide = await self.tide_service.get_tide_for_date(target_date)
        season = self._build_season_context(target_date)

        news_items = []
        if include_news:
            news_items = await self._get_news_context(max_news_items, target_date)

        return StoryContext(
            weather=weather,
            tide=tide,
            season=season,
            news_items=news_items,
            location=settings.ipswich_location_name,
        )

    def _build_season_context(self, target_date: date) -> SeasonContext:
        """Build seasonal and calendar context."""
        month = target_date.month
        day = target_date.day

        # Determine season (astronomical seasons for Northern Hemisphere)
        if (month == 12 and day >= 21) or month in (1, 2) or (month == 3 and day < 20):
            season = "Winter"
        elif (month == 3 and day >= 20) or month in (4, 5) or (month == 6 and day < 21):
            season = "Spring"
        elif (month == 6 and day >= 21) or month in (7, 8) or (month == 9 and day < 22):
            season = "Summer"
        else:
            season = "Autumn"

        # Day length classification (rough, based on month)
        if month in (11, 12, 1, 2):
            day_length = "short"
        elif month in (5, 6, 7, 8):
            day_length = "long"
        else:
            day_length = "medium"

        return SeasonContext(
            season=season,
            month_name=target_date.strftime("%B"),
            day_of_week=target_date.strftime("%A"),
            day_length=day_length,
            date=target_date,
        )

    async def _get_news_context(self, max_count: int, target_date: date) -> list[NewsContext]:
        """Get news items for story context, filtered by target date."""
        news_items = await self.news_service.get_news_for_date(target_date, limit=max_count)

        return [
            NewsContext(
                id=item.id,
                headline=item.headline,
                summary=item.summary,
                article_url=item.article_url,
                category_label=item.category_label,
            )
            for item in news_items
        ]

    async def get_news_items_by_ids(self, ids: list[int]) -> list[NewsItemBrief]:
        """Fetch specific news items by their IDs for response building."""
        if not ids:
            return []

        news_items = await self.news_service.get_news_items_by_ids(ids)

        return [
            NewsItemBrief(
                id=item.id,
                headline=item.headline,
                summary=item.summary[:200] + "..." if len(item.summary) > 200 else item.summary,
                article_url=item.article_url,
                author=item.author,
            )
            for item in news_items
        ]
