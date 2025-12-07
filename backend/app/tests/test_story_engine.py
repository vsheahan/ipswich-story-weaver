"""Tests for the story engine and context building."""

from datetime import date

import pytest

from app.schemas.story import (
    NewsContext,
    SeasonContext,
    StoryContext,
    TideContext,
    WeatherContext,
)
from app.services.story_engine import TemplateStoryGenerator
from app.services.tide_service import TideService


class TestSeasonContext:
    """Tests for season context building."""

    def test_winter_season(self):
        """Test winter season detection."""
        from app.services.context_builder import ContextBuilder

        # January should be winter
        ctx = ContextBuilder._build_season_context(None, date(2024, 1, 15))
        assert ctx.season == "Winter"
        assert ctx.month_name == "January"
        assert ctx.day_length == "short"

    def test_spring_season(self):
        """Test spring season detection."""
        from app.services.context_builder import ContextBuilder

        # April should be spring
        ctx = ContextBuilder._build_season_context(None, date(2024, 4, 15))
        assert ctx.season == "Spring"
        assert ctx.month_name == "April"
        assert ctx.day_length == "medium"

    def test_summer_season(self):
        """Test summer season detection."""
        from app.services.context_builder import ContextBuilder

        # July should be summer
        ctx = ContextBuilder._build_season_context(None, date(2024, 7, 15))
        assert ctx.season == "Summer"
        assert ctx.month_name == "July"
        assert ctx.day_length == "long"

    def test_autumn_season(self):
        """Test autumn season detection."""
        from app.services.context_builder import ContextBuilder

        # October should be autumn
        ctx = ContextBuilder._build_season_context(None, date(2024, 10, 15))
        assert ctx.season == "Autumn"
        assert ctx.month_name == "October"
        assert ctx.day_length == "medium"


class TestTideService:
    """Tests for tide simulation."""

    def test_tide_simulation_returns_valid_state(self):
        """Test that simulated tides return valid states."""
        service = TideService()
        tide = service._simulate_tide(date(2024, 6, 15))

        assert tide.state in ["high", "low", "rising", "falling"]
        assert tide.height is not None
        assert 0 <= tide.height <= 12  # Reasonable tide range

    def test_tide_simulation_deterministic(self):
        """Test that same date produces same tide state."""
        service = TideService()
        tide1 = service._simulate_tide(date(2024, 6, 15))
        tide2 = service._simulate_tide(date(2024, 6, 15))

        assert tide1.state == tide2.state
        assert tide1.height == tide2.height

    def test_tide_description(self):
        """Test tide state descriptions."""
        service = TideService()

        high_tide = TideContext(state="high", height=9.5)
        desc = service.get_tide_description(high_tide)
        assert "high" in desc.lower()

        low_tide = TideContext(state="low", height=1.5)
        desc = service.get_tide_description(low_tide)
        assert "low" in desc.lower() or "out" in desc.lower()


class TestTemplateStoryGenerator:
    """Tests for the template-based story generator."""

    @pytest.fixture
    def generator(self):
        return TemplateStoryGenerator()

    @pytest.fixture
    def sample_context(self):
        return StoryContext(
            weather=WeatherContext(
                temp_high=75.0,
                temp_low=62.0,
                temp_current=70.0,
                condition="Clear",
                condition_description="Clear sky",
                summary="Clear sky. High of 75F, low of 62F.",
            ),
            tide=TideContext(state="rising", height=5.5),
            season=SeasonContext(
                season="Summer",
                month_name="July",
                day_of_week="Tuesday",
                day_length="long",
                date=date(2024, 7, 16),
            ),
            news_items=[],
            location="Ipswich, MA",
        )

    @pytest.mark.asyncio
    async def test_generates_title_and_body(self, generator, sample_context):
        """Test that generator produces title and body."""
        title, body = await generator.generate(sample_context)

        assert title is not None
        assert len(title) > 0
        assert body is not None
        assert len(body) > 100  # Should be substantial

    @pytest.mark.asyncio
    async def test_includes_seasonal_content(self, generator, sample_context):
        """Test that story includes seasonal references."""
        title, body = await generator.generate(sample_context)

        # Summer context should influence the story
        # (checking for seasonal opening templates)
        assert any(
            word in body.lower()
            for word in ["sun", "warm", "light", "summer", "beach", "heat"]
        )

    @pytest.mark.asyncio
    async def test_weaves_news_items(self, generator, sample_context):
        """Test that news items are woven into stories."""
        sample_context.news_items = [
            NewsContext(
                id=1,
                headline="Town Meeting Approves New Budget",
                summary="Annual budget approved for fiscal year.",
                article_url="https://example.com/budget",
                category_label="Ipswich",
            )
        ]

        title, body = await generator.generate(sample_context)

        # The news headline topic should appear in the body
        assert "budget" in body.lower() or "town" in body.lower()

    @pytest.mark.asyncio
    async def test_handles_empty_news(self, generator, sample_context):
        """Test that generator handles no news items gracefully."""
        sample_context.news_items = []
        title, body = await generator.generate(sample_context)

        assert title is not None
        assert body is not None

    def test_weather_key_mapping(self, generator):
        """Test weather condition to key mapping."""
        assert generator._get_weather_key("Clear") == "Clear"
        assert generator._get_weather_key("Partly cloudy") == "Clouds"
        assert generator._get_weather_key("Light rain") == "Rain"
        assert generator._get_weather_key("Heavy snow") == "Snow"
        assert generator._get_weather_key("Thunderstorm") == "Thunderstorm"
        assert generator._get_weather_key(None) == "Clear"


class TestNewsWeaving:
    """Tests for news item integration in stories."""

    @pytest.fixture
    def generator(self):
        return TemplateStoryGenerator()

    def test_weave_single_news_item(self, generator):
        """Test weaving a single news item."""
        news_items = [
            NewsContext(
                id=1,
                headline="Local Festival Draws Record Crowds",
                summary="The annual clam festival saw its biggest turnout.",
                article_url="https://example.com/festival",
                category_label="Ipswich",
            )
        ]

        result = generator._weave_news(news_items)
        assert "festival" in result.lower()

    def test_weave_multiple_news_items(self, generator):
        """Test weaving multiple news items."""
        news_items = [
            NewsContext(
                id=1,
                headline="Town Budget Approved",
                summary="Town meeting approves new budget.",
                article_url="https://example.com/budget",
                category_label="Ipswich",
            ),
            NewsContext(
                id=2,
                headline="Beach Cleanup Scheduled",
                summary="Volunteers needed for annual cleanup.",
                article_url="https://example.com/cleanup",
                category_label="Ipswich",
            ),
        ]

        result = generator._weave_news(news_items)
        # Should mention both topics
        assert "budget" in result.lower() or "town" in result.lower()
        assert "beach" in result.lower() or "cleanup" in result.lower()

    def test_empty_news_items(self, generator):
        """Test handling empty news items list."""
        result = generator._weave_news([])
        assert result == ""
