"""Pydantic schemas for story chapters."""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.news import NewsItemBrief


class WeatherContext(BaseModel):
    """Weather context for story generation."""

    temp_high: Optional[float] = None
    temp_low: Optional[float] = None
    temp_current: Optional[float] = None
    condition: Optional[str] = None
    condition_description: Optional[str] = None
    humidity: Optional[int] = None
    wind_speed: Optional[float] = None
    sunrise: Optional[datetime] = None
    sunset: Optional[datetime] = None
    summary: str = "Weather data unavailable"


class TideContext(BaseModel):
    """Tide context for story generation."""

    state: str = Field(description="high, low, rising, falling")
    time_of_next: Optional[datetime] = None
    height: Optional[float] = None


class SeasonContext(BaseModel):
    """Seasonal and calendar context."""

    season: str
    month_name: str
    day_of_week: str
    day_length: str = Field(description="long, medium, short")
    date: date


class NewsContext(BaseModel):
    """News item context for story generation."""

    id: int
    headline: str
    summary: str
    article_url: str
    category_label: str = "Ipswich"


class StoryContext(BaseModel):
    """Complete context for story generation."""

    weather: WeatherContext
    tide: TideContext
    season: SeasonContext
    news_items: list[NewsContext] = []
    location: str = "Ipswich, MA"


class StoryContextResponse(BaseModel):
    """API response for story context."""

    weather: WeatherContext
    tide: TideContext
    season: SeasonContext
    news_items: list[NewsItemBrief] = []


class StoryChapterResponse(BaseModel):
    """Schema for story chapter responses."""

    id: int
    chapter_date: date
    title: str
    body: str
    weather_summary: Optional[str]
    tide_state: Optional[str]
    season: str
    month_name: str
    day_of_week: str
    used_news_item_ids: Optional[list[int]]
    created_at: datetime
    # Include the news items that were used
    news_items: Optional[list[NewsItemBrief]] = None

    model_config = {"from_attributes": True}


class StoryArchiveItem(BaseModel):
    """Minimal chapter data for archive listing."""

    id: int
    chapter_date: date
    title: str
    snippet: str = Field(description="First ~100 chars of the body")
    season: str

    model_config = {"from_attributes": True}


class StoryArchiveResponse(BaseModel):
    """Paginated archive response."""

    chapters: list[StoryArchiveItem]
    total: int
    page: int
    page_size: int
    has_more: bool


class GenerateStoryResponse(BaseModel):
    """Response from story generation endpoint."""

    success: bool
    message: str
    chapter: Optional[StoryChapterResponse] = None
