"""Atmosphere-based environmental services.

This module provides:
- AirQualityService: PM2.5 and Ozone from EPA AirNow API
- SmokeService: Wildfire smoke detection and trajectories
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import httpx

from app.services.environmental.base import (
    IPSWICH_LAT,
    IPSWICH_LON,
    DEFAULT_TIMEOUT,
)

logger = logging.getLogger(__name__)


@dataclass
class AirQualityContext:
    """Air quality conditions for story generation."""
    pm25_aqi: Optional[int] = None
    pm25_concentration: Optional[float] = None  # µg/m³
    ozone_aqi: Optional[int] = None
    overall_aqi: Optional[int] = None
    category: str = "Good"  # EPA AQI categories
    category_color: str = "green"
    health_message: Optional[str] = None
    primary_pollutant: Optional[str] = None
    description: str = "Air quality data unavailable"


@dataclass
class SmokeContext:
    """Wildfire smoke conditions for story generation."""
    present: bool = False
    intensity: str = "none"  # "none", "light", "moderate", "heavy"
    source_direction: Optional[str] = None
    source_description: Optional[str] = None
    description: str = "No smoke detected"


# EPA AQI categories and health messages
AQI_CATEGORIES = {
    (0, 50): ("Good", "green", "Air quality is satisfactory"),
    (51, 100): ("Moderate", "yellow", "Acceptable; moderate health concern for sensitive groups"),
    (101, 150): ("Unhealthy for Sensitive Groups", "orange", "Sensitive groups may experience health effects"),
    (151, 200): ("Unhealthy", "red", "Everyone may begin to experience health effects"),
    (201, 300): ("Very Unhealthy", "purple", "Health alert: significant risk for all"),
    (301, 500): ("Hazardous", "maroon", "Health warning: emergency conditions"),
}


def get_aqi_category(aqi: int) -> tuple[str, str, str]:
    """Get category, color, and message for an AQI value."""
    for (low, high), (category, color, message) in AQI_CATEGORIES.items():
        if low <= aqi <= high:
            return category, color, message
    return "Unknown", "gray", "AQI data unavailable"


class AirQualityService:
    """Service for air quality data from EPA AirNow API.

    Fetches current PM2.5 and Ozone measurements for Ipswich area.
    Requires AirNow API key (free registration at https://docs.airnowapi.org/).
    """

    BASE_URL = "https://www.airnowapi.org/aq/observation/latLong/current/"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize air quality service.

        Args:
            api_key: EPA AirNow API key
        """
        self.api_key = api_key

    async def get_air_quality(self) -> AirQualityContext:
        """Get current air quality for Ipswich area.

        Returns:
            AirQualityContext with PM2.5, Ozone, and overall AQI
        """
        if not self.api_key:
            logger.warning("AirNow API key not configured")
            return AirQualityContext()

        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                response = await client.get(
                    self.BASE_URL,
                    params={
                        "latitude": IPSWICH_LAT,
                        "longitude": IPSWICH_LON,
                        "distance": 25,  # miles
                        "format": "application/json",
                        "API_KEY": self.api_key,
                    },
                )
                response.raise_for_status()
                data = response.json()

                if not data:
                    return AirQualityContext()

                # Parse response - AirNow returns list of observations
                pm25_aqi = None
                pm25_conc = None
                ozone_aqi = None
                primary_pollutant = None
                max_aqi = 0

                for obs in data:
                    param = obs.get("ParameterName", "")
                    aqi = obs.get("AQI")
                    category = obs.get("Category", {})

                    if aqi is None:
                        continue

                    if "PM2.5" in param:
                        pm25_aqi = aqi
                        pm25_conc = obs.get("Concentration")
                        if aqi > max_aqi:
                            max_aqi = aqi
                            primary_pollutant = "PM2.5"
                    elif "OZONE" in param or "O3" in param:
                        ozone_aqi = aqi
                        if aqi > max_aqi:
                            max_aqi = aqi
                            primary_pollutant = "Ozone"

                if max_aqi == 0:
                    return AirQualityContext()

                category, color, health_msg = get_aqi_category(max_aqi)

                # Build description
                desc_parts = [f"AQI: {max_aqi} ({category})"]
                if pm25_aqi:
                    desc_parts.append(f"PM2.5: {pm25_aqi}")
                if ozone_aqi:
                    desc_parts.append(f"Ozone: {ozone_aqi}")

                return AirQualityContext(
                    pm25_aqi=pm25_aqi,
                    pm25_concentration=pm25_conc,
                    ozone_aqi=ozone_aqi,
                    overall_aqi=max_aqi,
                    category=category,
                    category_color=color,
                    health_message=health_msg,
                    primary_pollutant=primary_pollutant,
                    description=" | ".join(desc_parts),
                )

        except httpx.TimeoutException:
            logger.warning("AirNow request timed out")
            return AirQualityContext()
        except httpx.HTTPStatusError as e:
            logger.warning(f"AirNow HTTP error: {e.response.status_code}")
            return AirQualityContext()
        except Exception as e:
            logger.error(f"AirNow unexpected error: {e}")
            return AirQualityContext()

    def format_for_story(self, context: AirQualityContext) -> str:
        """Format air quality info for story context."""
        if context.overall_aqi is None:
            return ""

        lines = ["## Air Quality (EPA AirNow)"]
        lines.append(f"- {context.description}")
        if context.health_message:
            lines.append(f"- {context.health_message}")

        return "\n".join(lines)


class SmokeService:
    """Service for wildfire smoke detection.

    Uses EPA AirNow's smoke-related data and NOAA HRRR-Smoke when available.
    Also monitors for elevated PM2.5 which often indicates smoke.
    """

    # AirNow smoke forecasts endpoint
    AIRNOW_SMOKE_URL = "https://www.airnowapi.org/aq/forecast/latLong/"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize smoke service.

        Args:
            api_key: EPA AirNow API key (same as air quality)
        """
        self.api_key = api_key

    async def get_smoke_conditions(
        self,
        air_quality: Optional[AirQualityContext] = None
    ) -> SmokeContext:
        """Get current smoke conditions for Ipswich area.

        Args:
            air_quality: Optional pre-fetched air quality context to avoid duplicate calls

        Returns:
            SmokeContext with smoke detection and intensity
        """
        # Check air quality for smoke indicators
        if air_quality and air_quality.pm25_aqi:
            # High PM2.5 with certain patterns suggests smoke
            # This is a simplified heuristic - real implementation would use
            # HRRR-Smoke model output
            if air_quality.pm25_aqi > 100:
                return await self._analyze_elevated_pm25(air_quality)

        # Try to get smoke forecast from AirNow
        if self.api_key:
            try:
                smoke_forecast = await self._get_airnow_forecast()
                if smoke_forecast:
                    return smoke_forecast
            except Exception as e:
                logger.debug(f"Could not fetch smoke forecast: {e}")

        return SmokeContext()

    async def _analyze_elevated_pm25(
        self,
        air_quality: AirQualityContext
    ) -> SmokeContext:
        """Analyze elevated PM2.5 for smoke likelihood."""
        pm25 = air_quality.pm25_aqi or 0

        # High PM2.5 could be smoke, especially in summer/fall
        month = datetime.now().month

        # Wildfire smoke is more common in summer/fall
        is_fire_season = month in [6, 7, 8, 9, 10]

        if pm25 > 150 and is_fire_season:
            return SmokeContext(
                present=True,
                intensity="heavy",
                description=f"Elevated PM2.5 ({pm25} AQI) - possible wildfire smoke",
            )
        elif pm25 > 100 and is_fire_season:
            return SmokeContext(
                present=True,
                intensity="moderate",
                description=f"Elevated PM2.5 ({pm25} AQI) - possible smoke influence",
            )
        elif pm25 > 100:
            return SmokeContext(
                present=False,
                intensity="none",
                description=f"Elevated PM2.5 ({pm25} AQI) - likely not smoke-related",
            )

        return SmokeContext()

    async def _get_airnow_forecast(self) -> Optional[SmokeContext]:
        """Get AirNow forecast which may include smoke information."""
        if not self.api_key:
            return None

        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                response = await client.get(
                    self.AIRNOW_SMOKE_URL,
                    params={
                        "latitude": IPSWICH_LAT,
                        "longitude": IPSWICH_LON,
                        "distance": 25,
                        "format": "application/json",
                        "API_KEY": self.api_key,
                    },
                )
                response.raise_for_status()
                data = response.json()

                # Check forecast for fire/smoke category
                for forecast in data:
                    category = forecast.get("Category", {})
                    action_day = forecast.get("ActionDay", False)

                    # AirNow may flag action days for smoke events
                    if action_day:
                        discussion = forecast.get("Discussion", "")
                        if "smoke" in discussion.lower() or "fire" in discussion.lower():
                            return SmokeContext(
                                present=True,
                                intensity="moderate",
                                description=discussion[:200],
                            )

                return None

        except Exception as e:
            logger.debug(f"AirNow forecast error: {e}")
            return None

    def format_for_story(self, context: SmokeContext) -> str:
        """Format smoke info for story context."""
        if not context.present:
            return ""

        lines = ["## Wildfire Smoke"]
        lines.append(f"- Intensity: {context.intensity}")
        lines.append(f"- {context.description}")
        if context.source_direction:
            lines.append(f"- Source direction: {context.source_direction}")

        return "\n".join(lines)
