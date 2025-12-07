"""Pydantic schemas for news items."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NewsItemResponse(BaseModel):
    """Schema for news item responses."""

    id: int
    headline: str
    summary: str
    article_url: str
    author: Optional[str] = None
    category_label: str = "Ipswich"
    published_at: Optional[datetime] = None
    fetched_at: datetime

    model_config = {"from_attributes": True}


class NewsItemBrief(BaseModel):
    """Minimal news item for embedding in story responses."""

    id: int
    headline: str
    summary: str = Field(description="Short excerpt from the article")
    article_url: str
    author: Optional[str] = None

    model_config = {"from_attributes": True}


class NewsListResponse(BaseModel):
    """Schema for list of news items."""

    news_items: list[NewsItemResponse]
    total: int


class RefreshNewsResponse(BaseModel):
    """Response from news refresh endpoint."""

    success: bool
    message: str
    items_updated: int
