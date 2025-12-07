"""Weather service for fetching Ipswich, MA weather data."""

import logging
from datetime import date, datetime
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.story import WeatherSnapshot
from app.schemas.story import WeatherContext

logger = logging.getLogger(__name__)
settings = get_settings()


class WeatherService:
    """Service for fetching and storing weather data for Ipswich, MA."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_key = settings.weather_api_key
        self.base_url = settings.weather_api_base_url
        self.lat = settings.ipswich_lat
        self.lon = settings.ipswich_lon

    async def get_weather_for_date(self, target_date: date) -> WeatherContext:
        """Get weather for a specific date, fetching from API if needed."""
        # Check if we have cached weather data
        snapshot = await self._get_cached_snapshot(target_date)
        if snapshot:
            return self._snapshot_to_context(snapshot)

        # Fetch fresh data
        if target_date == date.today():
            snapshot = await self._fetch_and_store_current_weather(target_date)
            if snapshot:
                return self._snapshot_to_context(snapshot)

        # Return fallback if no data available
        return self._get_fallback_weather(target_date)

    async def _get_cached_snapshot(self, target_date: date) -> Optional[WeatherSnapshot]:
        """Get cached weather snapshot from database."""
        result = await self.db.execute(
            select(WeatherSnapshot).where(WeatherSnapshot.snapshot_date == target_date)
        )
        return result.scalar_one_or_none()

    async def _fetch_and_store_current_weather(
        self, target_date: date
    ) -> Optional[WeatherSnapshot]:
        """Fetch current weather from OpenWeatherMap and store it."""
        if not self.api_key:
            logger.warning("No weather API key configured, using fallback data")
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "lat": self.lat,
                        "lon": self.lon,
                        "appid": self.api_key,
                        "units": "imperial",
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()

            snapshot = WeatherSnapshot(
                snapshot_date=target_date,
                temp_current=data.get("main", {}).get("temp"),
                temp_high=data.get("main", {}).get("temp_max"),
                temp_low=data.get("main", {}).get("temp_min"),
                feels_like=data.get("main", {}).get("feels_like"),
                humidity=data.get("main", {}).get("humidity"),
                condition=data.get("weather", [{}])[0].get("main"),
                condition_description=data.get("weather", [{}])[0].get("description"),
                icon=data.get("weather", [{}])[0].get("icon"),
                wind_speed=data.get("wind", {}).get("speed"),
                wind_direction=data.get("wind", {}).get("deg"),
                sunrise=datetime.fromtimestamp(data.get("sys", {}).get("sunrise", 0))
                if data.get("sys", {}).get("sunrise")
                else None,
                sunset=datetime.fromtimestamp(data.get("sys", {}).get("sunset", 0))
                if data.get("sys", {}).get("sunset")
                else None,
                raw_data=data,
            )

            self.db.add(snapshot)
            await self.db.flush()
            return snapshot

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch weather data: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing weather data: {e}")
            return None

    def _snapshot_to_context(self, snapshot: WeatherSnapshot) -> WeatherContext:
        """Convert a database snapshot to a WeatherContext."""
        summary_parts = []
        if snapshot.condition_description:
            summary_parts.append(snapshot.condition_description.capitalize())
        if snapshot.temp_high and snapshot.temp_low:
            summary_parts.append(f"High of {snapshot.temp_high:.0f}F, low of {snapshot.temp_low:.0f}F")
        elif snapshot.temp_current:
            summary_parts.append(f"Currently {snapshot.temp_current:.0f}F")

        return WeatherContext(
            temp_high=snapshot.temp_high,
            temp_low=snapshot.temp_low,
            temp_current=snapshot.temp_current,
            condition=snapshot.condition,
            condition_description=snapshot.condition_description,
            humidity=snapshot.humidity,
            wind_speed=snapshot.wind_speed,
            sunrise=snapshot.sunrise,
            sunset=snapshot.sunset,
            summary=". ".join(summary_parts) if summary_parts else "Weather data available",
        )

    def _get_fallback_weather(self, target_date: date) -> WeatherContext:
        """Generate fallback weather based on season (for when API is unavailable)."""
        month = target_date.month

        # Seasonal defaults for coastal Massachusetts
        seasonal_weather = {
            (12, 1, 2): ("Cold", "Cold winter day along the coast", 28, 38),
            (3, 4, 5): ("Mild", "Cool spring day with sea breeze", 45, 58),
            (6, 7, 8): ("Warm", "Warm summer day by the shore", 68, 82),
            (9, 10, 11): ("Cool", "Crisp autumn day in New England", 48, 62),
        }

        for months, (condition, desc, low, high) in seasonal_weather.items():
            if month in months:
                return WeatherContext(
                    temp_high=float(high),
                    temp_low=float(low),
                    temp_current=float((high + low) // 2),
                    condition=condition,
                    condition_description=desc,
                    summary=f"{desc}. High near {high}F, low near {low}F.",
                )

        return WeatherContext(summary="Weather data unavailable")
