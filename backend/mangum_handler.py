"""Lambda handler using Mangum to wrap FastAPI ASGI app."""

import asyncio
import json
from datetime import date
from mangum import Mangum
from app.main import app

# Mangum wraps the FastAPI ASGI app for Lambda
_mangum_handler = Mangum(app, lifespan="off")


async def generate_daily_story():
    """Generate the daily story - called by scheduled event."""
    from app.core.database import async_session_maker
    from app.core.config import get_settings
    from app.services.news_service import NewsService
    from app.services.context_builder import ContextBuilder
    from app.services.story_engine import StoryEngine, TemplateStoryGenerator
    from app.services.llm_story_generator import LLMStoryGeneratorWithFallback

    settings = get_settings()

    async with async_session_maker() as session:
        # First refresh news
        news_service = NewsService(session)
        await news_service.fetch_and_update_ipswich_news()

        # Build context for today
        today = date.today()
        context_builder = ContextBuilder(session)
        context = await context_builder.build_context(today)

        # Get the appropriate story generator (LLM or template-based)
        fallback = TemplateStoryGenerator()
        if settings.use_llm_for_stories and settings.anthropic_api_key:
            generator = LLMStoryGeneratorWithFallback(
                api_key=settings.anthropic_api_key,
                fallback_generator=fallback,
                model=settings.llm_model,
            )
        else:
            generator = fallback

        # Generate story
        engine = StoryEngine(session, generator=generator)
        chapter = await engine.generate_story_for_date(
            context=context,
            target_date=today,
            force_regenerate=False,
        )

        await session.commit()

        return {
            "chapter": {
                "title": chapter.title,
                "date": str(chapter.chapter_date),
            }
        }


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
