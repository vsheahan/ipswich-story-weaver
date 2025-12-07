"""NewsItem model for Ipswich local news articles."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class NewsItem(Base):
    """Local news item from The Local News Ipswich category."""

    __tablename__ = "news_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    headline: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    article_url: Mapped[str] = mapped_column(String(1000), nullable=False, unique=True)
    author: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    category_label: Mapped[str] = mapped_column(String(100), default="Ipswich", nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("article_url", name="uq_news_article_url"),
    )

    def __repr__(self) -> str:
        return f"<NewsItem(id={self.id}, headline={self.headline[:40]}...)>"
