"""Story chapter and weather snapshot models."""

from datetime import date, datetime
from typing import Optional

from sqlalchemy import ARRAY, Date, DateTime, Float, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WeatherSnapshot(Base):
    """Daily weather snapshot for Ipswich, MA."""

    __tablename__ = "weather_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    snapshot_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False, index=True)

    # Temperature
    temp_high: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    temp_low: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    temp_current: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    feels_like: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Conditions
    condition: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    condition_description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Other metrics
    humidity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    wind_speed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    wind_direction: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Sun times
    sunrise: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    sunset: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Raw API response for debugging
    raw_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<WeatherSnapshot(date={self.snapshot_date}, condition={self.condition})>"


class StoryChapter(Base):
    """A daily chapter in Ipswich's ongoing story."""

    __tablename__ = "story_chapters"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    chapter_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # Story content
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    # Context metadata
    weather_summary: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    tide_state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    season: Mapped[str] = mapped_column(String(20), nullable=False)
    month_name: Mapped[str] = mapped_column(String(20), nullable=False)
    day_of_week: Mapped[str] = mapped_column(String(15), nullable=False)

    # References to news items used
    used_news_item_ids: Mapped[Optional[list[int]]] = mapped_column(ARRAY(Integer), nullable=True)

    # Generation metadata
    generation_context: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, onupdate=datetime.utcnow, nullable=True
    )

    __table_args__ = (
        UniqueConstraint("chapter_date", name="uq_chapter_date"),
    )

    def __repr__(self) -> str:
        return f"<StoryChapter(date={self.chapter_date}, title={self.title[:30]}...)>"
