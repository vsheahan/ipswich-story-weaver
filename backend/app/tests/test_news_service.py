"""Tests for the news scraping service."""

import pytest
from datetime import datetime

from app.services.news_service import NewsService


# Sample HTML fixture mimicking The Local News category page structure
SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Ipswich - The Local News</title></head>
<body>
<main>
    <article class="post">
        <h2 class="entry-title"><a href="https://thelocalnews.news/2024/12/town-meeting-budget/">Town Meeting Approves Budget</a></h2>
        <div class="entry-excerpt">
            <p>The annual town meeting approved a new budget for the upcoming fiscal year.</p>
        </div>
        <span class="author">By Jane Smith</span>
        <time datetime="2024-12-01T10:00:00">December 1, 2024</time>
    </article>

    <article class="post">
        <h2 class="entry-title"><a href="https://thelocalnews.news/2024/11/crane-beach-winter/">Crane Beach Opens for Winter</a></h2>
        <div class="entry-excerpt">
            <p>Crane Beach now offers winter walking with reduced parking fees.</p>
        </div>
        <span class="author">By John Doe</span>
        <time datetime="2024-11-28T09:00:00">November 28, 2024</time>
    </article>

    <article class="post">
        <h2 class="entry-title"><a href="https://thelocalnews.news/2024/11/choate-bridge/">Historic Bridge Restoration</a></h2>
        <div class="entry-excerpt">
            <p>The Choate Bridge restoration project has been completed.</p>
        </div>
        <time datetime="2024-11-25T14:30:00">November 25, 2024</time>
    </article>
</main>
</body>
</html>
"""


class TestNewsServiceParsing:
    """Tests for HTML parsing functionality."""

    def test_parse_category_page(self):
        """Test parsing a sample category page."""
        service = NewsService(db=None)  # DB not needed for parsing
        articles = service._parse_category_page(SAMPLE_HTML)

        assert len(articles) == 3

        # Check first article
        assert articles[0]["headline"] == "Town Meeting Approves Budget"
        assert "budget" in articles[0]["summary"].lower()
        assert articles[0]["article_url"] == "https://thelocalnews.news/2024/12/town-meeting-budget/"

        # Check second article
        assert articles[1]["headline"] == "Crane Beach Opens for Winter"
        assert "winter" in articles[1]["summary"].lower()

        # Check third article (no author)
        assert articles[2]["headline"] == "Historic Bridge Restoration"

    def test_parse_empty_page(self):
        """Test parsing a page with no articles."""
        empty_html = "<html><body><main></main></body></html>"
        service = NewsService(db=None)
        articles = service._parse_category_page(empty_html)

        assert articles == []

    def test_parse_date_iso_format(self):
        """Test parsing ISO format dates."""
        service = NewsService(db=None)

        result = service._parse_date("2024-12-01T10:00:00")
        assert result is not None
        assert result.year == 2024
        assert result.month == 12
        assert result.day == 1

    def test_parse_date_common_format(self):
        """Test parsing common date formats."""
        service = NewsService(db=None)

        result = service._parse_date("December 1, 2024")
        assert result is not None
        assert result.year == 2024
        assert result.month == 12

    def test_parse_date_relative(self):
        """Test parsing relative dates."""
        service = NewsService(db=None)

        result = service._parse_date("today")
        assert result is not None
        assert result.date() == datetime.utcnow().date()

        result = service._parse_date("2 days ago")
        assert result is not None

    def test_parse_date_invalid(self):
        """Test parsing invalid dates returns None."""
        service = NewsService(db=None)

        result = service._parse_date("not a date")
        assert result is None

        result = service._parse_date("")
        assert result is None


class TestNewsServiceExtraction:
    """Tests for article data extraction."""

    def test_extract_article_data(self):
        """Test extracting article data from an article element."""
        from bs4 import BeautifulSoup

        html = """
        <article class="post">
            <h2><a href="/test-article">Test Headline</a></h2>
            <div class="excerpt"><p>This is the summary text.</p></div>
            <span class="author">Test Author</span>
            <time datetime="2024-12-01">Dec 1, 2024</time>
        </article>
        """

        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("article")

        service = NewsService(db=None)
        data = service._extract_article_data(element)

        assert data is not None
        assert data["headline"] == "Test Headline"
        assert "summary" in data["summary"].lower()
        assert "thelocalnews.news" in data["article_url"]
        assert data["category_label"] == "Ipswich"

    def test_extract_article_missing_link(self):
        """Test extraction fails gracefully with missing link."""
        from bs4 import BeautifulSoup

        html = """
        <article class="post">
            <h2>Headline without link</h2>
        </article>
        """

        soup = BeautifulSoup(html, "html.parser")
        element = soup.find("article")

        service = NewsService(db=None)
        data = service._extract_article_data(element)

        # Should return None since no valid URL
        assert data is None


class TestNewsServiceIntegration:
    """Integration tests for news service with database."""

    @pytest.mark.asyncio
    async def test_get_recent_news_empty(self, db_session):
        """Test getting recent news when database is empty."""
        service = NewsService(db_session)
        news_items = await service.get_recent_news_items(limit=5)

        assert news_items == []

    @pytest.mark.asyncio
    async def test_get_recent_news_with_items(self, db_session, sample_news_items):
        """Test getting recent news with items in database."""
        service = NewsService(db_session)
        news_items = await service.get_recent_news_items(limit=5)

        assert len(news_items) == 3
        # Should be sorted by published_at descending
        assert news_items[0].headline == "Ipswich Town Meeting Approves New Budget"

    @pytest.mark.asyncio
    async def test_get_news_by_ids(self, db_session, sample_news_items):
        """Test fetching news items by their IDs."""
        service = NewsService(db_session)
        ids = [sample_news_items[0].id, sample_news_items[1].id]
        news_items = await service.get_news_items_by_ids(ids)

        assert len(news_items) == 2

    @pytest.mark.asyncio
    async def test_get_news_by_empty_ids(self, db_session):
        """Test fetching news items with empty ID list."""
        service = NewsService(db_session)
        news_items = await service.get_news_items_by_ids([])

        assert news_items == []
