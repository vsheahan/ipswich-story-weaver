"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Tests for health and root endpoints."""

    def test_health_check(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "docs_url" in data


class TestNewsAPI:
    """Tests for news API endpoints (read-only)."""

    def test_get_recent_news_empty(self, client: TestClient):
        """Test getting recent news when none exist."""
        response = client.get("/api/news/recent")
        assert response.status_code == 200
        data = response.json()
        assert data["news_items"] == []
        assert data["total"] == 0

    def test_get_recent_news_with_limit(self, client: TestClient):
        """Test getting recent news with custom limit."""
        response = client.get("/api/news/recent?limit=3")
        assert response.status_code == 200
        data = response.json()
        assert "news_items" in data
        assert "total" in data


class TestStoryAPI:
    """Tests for story API endpoints."""

    def test_get_latest_story_none(self, client: TestClient):
        """Test getting latest story when none exist."""
        response = client.get("/api/story/latest")
        assert response.status_code == 200
        assert response.json() is None

    def test_get_story_by_date_not_found(self, client: TestClient):
        """Test getting story by date when it doesn't exist."""
        response = client.get("/api/story/date/2024-01-01")
        assert response.status_code == 404

    def test_get_story_archive_empty(self, client: TestClient):
        """Test getting story archive when empty."""
        response = client.get("/api/story/archive")
        assert response.status_code == 200
        data = response.json()
        assert data["chapters"] == []
        assert data["total"] == 0
        assert data["has_more"] is False

    def test_get_today_context(self, client: TestClient):
        """Test getting today's context."""
        response = client.get("/api/story/context/today")
        assert response.status_code == 200
        data = response.json()
        assert "weather" in data
        assert "tide" in data
        assert "season" in data
        assert "news_items" in data
        assert data["season"]["season"] in ["Winter", "Spring", "Summer", "Autumn"]

    def test_generate_today_story(self, client: TestClient):
        """Test generating today's story."""
        response = client.post("/api/story/generate-today")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "chapter" in data
        assert data["chapter"]["title"] is not None
        assert data["chapter"]["body"] is not None

    def test_generate_today_story_duplicate(self, client: TestClient):
        """Test generating story when one already exists."""
        # Generate first story
        client.post("/api/story/generate-today")

        # Try to generate again without force
        response = client.post("/api/story/generate-today")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "already exists" in data["message"]

    def test_generate_today_story_force(self, client: TestClient):
        """Test force regenerating today's story."""
        # Generate first story
        client.post("/api/story/generate-today")

        # Force regenerate
        response = client.post("/api/story/generate-today?force=true")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "regenerated" in data["message"]


class TestAdminAPI:
    """Tests for admin API endpoints."""

    def test_refresh_news(self, client: TestClient):
        """Test the news refresh admin endpoint."""
        # Note: This will attempt to actually scrape, which may fail
        # In a real test environment, you'd mock the HTTP calls
        response = client.post("/api/admin/refresh-news")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "items_updated" in data


class TestReadOnlyAPI:
    """Tests to verify no public POST endpoints accept arbitrary text."""

    def test_no_anecdote_post_endpoint(self, client: TestClient):
        """Verify that the anecdotes POST endpoint no longer exists."""
        response = client.post(
            "/api/anecdotes",
            json={"text": "This should not work"},
        )
        # Should return 404 since the endpoint doesn't exist
        assert response.status_code == 404

    def test_story_endpoints_are_read_only(self, client: TestClient):
        """Verify story endpoints don't accept POST with content body."""
        # The only POST endpoint for story is generate-today which doesn't
        # accept a request body with arbitrary text

        # Try to POST to latest (should fail)
        response = client.post("/api/story/latest")
        assert response.status_code == 405  # Method not allowed

        # Try to POST to archive (should fail)
        response = client.post("/api/story/archive")
        assert response.status_code == 405

    def test_news_endpoints_are_read_only(self, client: TestClient):
        """Verify news endpoints are read-only."""
        # Try to POST to recent news (should fail)
        response = client.post(
            "/api/news/recent",
            json={"headline": "Fake news"},
        )
        assert response.status_code == 405  # Method not allowed
