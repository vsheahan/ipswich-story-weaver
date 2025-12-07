"""Lambda handler using Mangum to wrap FastAPI ASGI app."""

import asyncio
import json
from mangum import Mangum
from app.main import app

# Mangum wraps the FastAPI ASGI app for Lambda
_mangum_handler = Mangum(app, lifespan="off")


async def generate_daily_story():
    """Generate the daily story - called by scheduled event."""
    from app.core.database import async_session_maker
    from app.services.story_service import StoryService
    from app.services.news_service import NewsService

    async with async_session_maker() as session:
        # First refresh news
        news_service = NewsService(session)
        await news_service.refresh_news()

        # Then generate story
        story_service = StoryService(session)
        result = await story_service.generate_daily_story()
        return result


def handler(event, context):
    """Handle both HTTP requests and scheduled events."""
    # Check if this is a scheduled EventBridge event
    if event.get("source") == "scheduled" and event.get("action") == "generate-story":
        try:
            result = asyncio.get_event_loop().run_until_complete(generate_daily_story())
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "success": True,
                    "message": "Daily story generated",
                    "title": result.get("chapter", {}).get("title") if result else None
                })
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "success": False,
                    "error": str(e)
                })
            }

    # Otherwise, handle as HTTP request via Mangum
    return _mangum_handler(event, context)
