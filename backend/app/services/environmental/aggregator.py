"""Aggregator for all environmental data sources.

This module provides the main entry point for gathering environmental context
from all available sources, with graceful degradation for any that fail.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from app.services.environmental.astronomy_services import (
    MeteorShowerService,
    MeteorShowerContext,
    get_planetary_service,
    PlanetaryContext,
)
from app.services.environmental.atmosphere_services import (
    AirQualityService,
    AirQualityContext,
    SmokeService,
    SmokeContext,
)
from app.services.environmental.land_services import (
    DroughtMonitorService,
    DroughtContext,
    SnowCoverService,
    SnowCoverContext,
    NDVIService,
    VegetationContext,
    CoastalErosionService,
    CoastalErosionContext,
)
from app.services.environmental.ocean_services import (
    SeaSurfaceTempService,
    SeaSurfaceTempContext,
    OceanColorService,
    OceanColorContext,
    WaveWatchService,
    WaveContext,
    HABForecastService,
    HABContext,
)

logger = logging.getLogger(__name__)


@dataclass
class EnvironmentalContext:
    """Aggregated environmental context for story generation."""

    # Ocean
    waves: Optional[WaveContext] = None
    sst: Optional[SeaSurfaceTempContext] = None
    ocean_color: Optional[OceanColorContext] = None
    hab: Optional[HABContext] = None

    # Atmosphere
    air_quality: Optional[AirQualityContext] = None
    smoke: Optional[SmokeContext] = None

    # Land
    vegetation: Optional[VegetationContext] = None
    snow: Optional[SnowCoverContext] = None
    drought: Optional[DroughtContext] = None
    coastal_erosion: Optional[CoastalErosionContext] = None

    # Astronomy
    planets: Optional[PlanetaryContext] = None
    meteor_shower: Optional[MeteorShowerContext] = None

    def has_any_data(self) -> bool:
        """Check if any environmental data was successfully fetched."""
        return any([
            self.waves and self.waves.significant_height_ft is not None,
            self.sst and self.sst.temp_fahrenheit is not None,
            self.ocean_color and self.ocean_color.chlorophyll_mg_m3 is not None,
            self.hab and self.hab.status != "none",
            self.air_quality and self.air_quality.overall_aqi is not None,
            self.smoke and self.smoke.present,
            self.vegetation and self.vegetation.ndvi_value is not None,
            self.snow and self.snow.coverage != "none",
            self.drought and self.drought.severity != "none",
            self.planets and self.planets.visible_planets,
            self.meteor_shower and self.meteor_shower.active_shower,
        ])


async def gather_environmental_context(
    airnow_api_key: Optional[str] = None,
    target_date: Optional[date] = None,
) -> EnvironmentalContext:
    """Gather all environmental context for story generation.

    This function calls all environmental services in parallel and aggregates
    their results. Any service that fails will return None for its component
    without affecting other services.

    Args:
        airnow_api_key: EPA AirNow API key for air quality data
        target_date: Date for queries (defaults to today)

    Returns:
        EnvironmentalContext with all available environmental data
    """
    if target_date is None:
        target_date = date.today()

    logger.info("Gathering environmental context...")

    # Initialize services
    wave_service = WaveWatchService()
    sst_service = SeaSurfaceTempService()
    ocean_color_service = OceanColorService()
    hab_service = HABForecastService()
    air_quality_service = AirQualityService(api_key=airnow_api_key)
    smoke_service = SmokeService(api_key=airnow_api_key)
    drought_service = DroughtMonitorService()
    snow_service = SnowCoverService()
    ndvi_service = NDVIService()
    erosion_service = CoastalErosionService()
    meteor_service = MeteorShowerService()
    planet_service = get_planetary_service()

    # Gather data in parallel using asyncio.gather with return_exceptions=True
    # This ensures one failing service doesn't bring down others
    results = await asyncio.gather(
        _safe_fetch("waves", wave_service.get_wave_conditions()),
        _safe_fetch("sst", sst_service.get_sst()),
        _safe_fetch("ocean_color", ocean_color_service.get_ocean_color()),
        _safe_fetch("hab", hab_service.get_hab_status()),
        _safe_fetch("air_quality", air_quality_service.get_air_quality()),
        _safe_fetch("drought", drought_service.get_drought_status(target_date)),
        _safe_fetch("snow", snow_service.get_snow_cover()),
        return_exceptions=True,
    )

    # Parse results from async operations
    waves = _extract_result(results, 0, "waves")
    sst = _extract_result(results, 1, "sst")
    ocean_color = _extract_result(results, 2, "ocean_color")
    hab = _extract_result(results, 3, "hab")
    air_quality = _extract_result(results, 4, "air_quality")
    drought = _extract_result(results, 5, "drought")
    snow = _extract_result(results, 6, "snow")

    # Get smoke status (uses air_quality data to avoid redundant API call)
    smoke = None
    try:
        smoke = await smoke_service.get_smoke_conditions(air_quality)
    except Exception as e:
        logger.warning(f"Failed to get smoke conditions: {e}")

    # Synchronous services (no external API calls)
    vegetation = ndvi_service.get_vegetation_status(target_date)
    erosion = erosion_service.get_erosion_status()
    meteor_shower = meteor_service.get_current_shower(target_date)
    planets = planet_service.get_visible_planets(target_date)

    context = EnvironmentalContext(
        waves=waves,
        sst=sst,
        ocean_color=ocean_color,
        hab=hab,
        air_quality=air_quality,
        smoke=smoke,
        vegetation=vegetation,
        snow=snow,
        drought=drought,
        coastal_erosion=erosion,
        planets=planets,
        meteor_shower=meteor_shower,
    )

    logger.info(f"Environmental context gathered: has_data={context.has_any_data()}")
    return context


async def _safe_fetch(name: str, coro):
    """Wrap a coroutine with error handling."""
    try:
        return await coro
    except Exception as e:
        logger.warning(f"Failed to fetch {name}: {e}")
        return None


def _extract_result(results: list, index: int, name: str):
    """Extract a result from the gather results, handling exceptions."""
    if index >= len(results):
        return None

    result = results[index]
    if isinstance(result, Exception):
        logger.warning(f"Exception fetching {name}: {result}")
        return None
    return result


def format_environmental_context(context: EnvironmentalContext) -> str:
    """Format all environmental context for inclusion in story generation prompt.

    Args:
        context: The aggregated environmental context

    Returns:
        Formatted markdown string for the LLM prompt
    """
    sections = []

    # Ocean conditions section
    ocean_parts = []
    if context.waves:
        wave_service = WaveWatchService()
        ocean_parts.append(wave_service.format_for_story(context.waves))
    if context.sst:
        sst_service = SeaSurfaceTempService()
        ocean_parts.append(sst_service.format_for_story(context.sst))
    if context.ocean_color:
        oc_service = OceanColorService()
        ocean_parts.append(oc_service.format_for_story(context.ocean_color))
    if context.hab and context.hab.status != "none":
        hab_service = HABForecastService()
        ocean_parts.append(hab_service.format_for_story(context.hab))

    if ocean_parts:
        sections.append("\n".join(filter(None, ocean_parts)))

    # Atmosphere section
    atmo_parts = []
    if context.air_quality:
        aq_service = AirQualityService()
        atmo_parts.append(aq_service.format_for_story(context.air_quality))
    if context.smoke and context.smoke.present:
        smoke_service = SmokeService()
        atmo_parts.append(smoke_service.format_for_story(context.smoke))

    if atmo_parts:
        sections.append("\n".join(filter(None, atmo_parts)))

    # Land section
    land_parts = []
    if context.vegetation:
        ndvi_service = NDVIService()
        land_parts.append(ndvi_service.format_for_story(context.vegetation))
    if context.snow and context.snow.coverage != "none":
        snow_service = SnowCoverService()
        land_parts.append(snow_service.format_for_story(context.snow))
    if context.drought and context.drought.severity != "none":
        drought_service = DroughtMonitorService()
        land_parts.append(drought_service.format_for_story(context.drought))
    if context.coastal_erosion and context.coastal_erosion.high_risk_areas:
        erosion_service = CoastalErosionService()
        land_parts.append(erosion_service.format_for_story(context.coastal_erosion))

    if land_parts:
        sections.append("\n".join(filter(None, land_parts)))

    # Astronomy section
    astro_parts = []
    if context.planets and context.planets.visible_planets:
        planet_service = get_planetary_service()
        astro_parts.append(planet_service.format_for_story(context.planets))
    if context.meteor_shower and context.meteor_shower.active_shower:
        meteor_service = MeteorShowerService()
        astro_parts.append(meteor_service.format_for_story(context.meteor_shower))

    if astro_parts:
        sections.append("\n".join(filter(None, astro_parts)))

    return "\n\n".join(sections)
