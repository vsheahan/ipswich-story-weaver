"""API v1 routes."""

from fastapi import APIRouter

from app.api.v1.routes_story import router as story_router
from app.api.v1.routes_news import router as news_router
from app.api.v1.routes_admin import router as admin_router

api_router = APIRouter()

api_router.include_router(story_router, prefix="/story", tags=["story"])
api_router.include_router(news_router, prefix="/news", tags=["news"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])
