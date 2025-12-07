"""Additional data sources for enriching story generation.

This module fetches data from:
- eBird API: Recent bird sightings in Essex County
- NOAA: Marine forecasts for Massachusetts Bay
- Town of Ipswich: Meeting calendar and announcements (when available)
"""

import logging
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

# eBird API configuration
# Region code for Essex County, MA
EBIRD_REGION = "US-MA-009"
EBIRD_API_URL = "https://api.ebird.org/v2"

# NOAA API configuration
# Massachusetts Bay coastal waters zone
NOAA_MARINE_ZONE = "ANZ230"  # Coastal waters from Ipswich Bay to Boston
NOAA_API_URL = "https://api.weather.gov"

# Ipswich coordinates for NOAA lookups
IPSWICH_LAT = 42.6792
IPSWICH_LON = -70.8417


@dataclass
class BirdSighting:
    """A recent bird sighting from eBird."""
    species_name: str
    common_name: str
    location_name: str
    observation_date: str
    count: Optional[int]
    is_notable: bool = False


@dataclass
class MarineForecast:
    """Marine forecast for coastal waters."""
    zone_name: str
    forecast_time: str
    conditions: str
    wind: Optional[str]
    seas: Optional[str]
    hazards: List[str]


@dataclass
class TownEvent:
    """A town meeting or event."""
    title: str
    date: str
    time: Optional[str]
    location: Optional[str]
    description: Optional[str]


class EBirdService:
    """Service for fetching bird sightings from eBird API."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize eBird service.

        Args:
            api_key: eBird API key (get free at https://ebird.org/api/keygen)
        """
        self.api_key = api_key

    async def get_recent_sightings(
        self,
        days_back: int = 3,
        max_results: int = 10,
        notable_only: bool = False,
    ) -> List[BirdSighting]:
        """Fetch recent bird sightings for Essex County.

        Args:
            days_back: Number of days to look back (max 30)
            max_results: Maximum sightings to return
            notable_only: If True, only return notable/rare sightings

        Returns:
            List of BirdSighting objects
        """
        if not self.api_key:
            logger.warning("eBird API key not configured, skipping bird sightings")
            return []

        endpoint = f"{EBIRD_API_URL}/data/obs/{EBIRD_REGION}/recent"
        if notable_only:
            endpoint = f"{EBIRD_API_URL}/data/obs/{EBIRD_REGION}/recent/notable"

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    endpoint,
                    headers={"x-ebirdapitoken": self.api_key},
                    params={"back": min(days_back, 30), "maxResults": max_results},
                )
                response.raise_for_status()
                data = response.json()

                sightings = []
                for obs in data:
                    sightings.append(BirdSighting(
                        species_name=obs.get("sciName", ""),
                        common_name=obs.get("comName", "Unknown"),
                        location_name=obs.get("locName", "Essex County"),
                        observation_date=obs.get("obsDt", ""),
                        count=obs.get("howMany"),
                        is_notable=notable_only,
                    ))

                logger.info(f"Fetched {len(sightings)} bird sightings from eBird")
                return sightings

        except httpx.HTTPError as e:
            logger.error(f"Error fetching eBird data: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error with eBird: {e}")
            return []

    def format_for_story(self, sightings: List[BirdSighting]) -> str:
        """Format bird sightings for inclusion in story context."""
        if not sightings:
            return ""

        lines = ["## Recent Bird Sightings (from eBird)"]
        for s in sightings[:5]:
            count_str = f" ({s.count} seen)" if s.count else ""
            notable_str = " [Notable!]" if s.is_notable else ""
            lines.append(f"- {s.common_name}{count_str} at {s.location_name}{notable_str}")

        return "\n".join(lines)


class NOAAMarineService:
    """Service for fetching NOAA marine forecasts."""

    async def get_marine_forecast(self) -> Optional[MarineForecast]:
        """Fetch marine forecast for Massachusetts Bay area.

        Returns:
            MarineForecast object or None if unavailable
        """
        # First, get the forecast office and grid point for Ipswich
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Get point metadata
                point_url = f"{NOAA_API_URL}/points/{IPSWICH_LAT},{IPSWICH_LON}"
                response = await client.get(point_url)
                response.raise_for_status()
                point_data = response.json()

                # Get the forecast
                forecast_url = point_data["properties"]["forecast"]
                response = await client.get(forecast_url)
                response.raise_for_status()
                forecast_data = response.json()

                # Extract current period
                periods = forecast_data.get("properties", {}).get("periods", [])
                if not periods:
                    return None

                current = periods[0]

                # Also check for active alerts
                alerts_url = f"{NOAA_API_URL}/alerts/active?point={IPSWICH_LAT},{IPSWICH_LON}"
                alerts_response = await client.get(alerts_url)
                alerts_data = alerts_response.json() if alerts_response.status_code == 200 else {}

                hazards = []
                for alert in alerts_data.get("features", []):
                    event = alert.get("properties", {}).get("event", "")
                    if event:
                        hazards.append(event)

                return MarineForecast(
                    zone_name="Ipswich Bay / Massachusetts Bay",
                    forecast_time=current.get("name", ""),
                    conditions=current.get("detailedForecast", ""),
                    wind=current.get("windSpeed", ""),
                    seas=None,  # Not always available in land forecasts
                    hazards=hazards,
                )

        except httpx.HTTPError as e:
            logger.error(f"Error fetching NOAA forecast: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error with NOAA: {e}")
            return None

    async def get_coastal_conditions(self) -> Dict[str, Any]:
        """Get simplified coastal/marine conditions for storytelling."""
        forecast = await self.get_marine_forecast()
        if not forecast:
            return {}

        return {
            "conditions": forecast.conditions,
            "wind": forecast.wind,
            "hazards": forecast.hazards,
            "has_warnings": len(forecast.hazards) > 0,
        }

    def format_for_story(self, forecast: Optional[MarineForecast]) -> str:
        """Format marine forecast for inclusion in story context."""
        if not forecast:
            return ""

        lines = ["## Coastal Conditions (from NOAA)"]
        lines.append(f"- {forecast.forecast_time}: {forecast.conditions[:200]}...")
        if forecast.wind:
            lines.append(f"- Wind: {forecast.wind}")
        if forecast.hazards:
            lines.append(f"- Active alerts: {', '.join(forecast.hazards)}")

        return "\n".join(lines)


class TownCalendarService:
    """Service for fetching Ipswich town calendar and announcements.

    Note: The town website (ipswichma.gov) uses CivicPlus platform.
    RSS feeds may be available at /RSSFeed.aspx but are not always enabled.
    This service provides the structure for integration when feeds become available.
    """

    TOWN_CALENDAR_URL = "https://www.ipswichma.gov/calendar.aspx"
    TOWN_NEWS_URL = "https://www.ipswichma.gov/CivicAlerts.aspx"

    async def get_upcoming_meetings(self) -> List[TownEvent]:
        """Fetch upcoming town meetings and events.

        Currently returns empty list as town RSS may not be available.
        Future implementation can scrape or use RSS when available.
        """
        # TODO: Implement when town RSS feed is confirmed available
        # The CivicPlus platform often has RSS at /RSSFeed.aspx?Type=1 (news)
        # or /RSSFeed.aspx?Type=2 (calendar)
        logger.debug("Town calendar integration not yet implemented")
        return []

    def format_for_story(self, events: List[TownEvent]) -> str:
        """Format town events for inclusion in story context."""
        if not events:
            return ""

        lines = ["## Town Events This Week"]
        for e in events[:3]:
            time_str = f" at {e.time}" if e.time else ""
            lines.append(f"- {e.title} ({e.date}{time_str})")

        return "\n".join(lines)


class IpswichRiverService:
    """Service for Ipswich River watershed information.

    The Ipswich River Watershed Association (ipswichriver.org) monitors
    river conditions and flow rates.
    """

    # USGS water gauge on Ipswich River at South Middleton
    USGS_GAUGE_ID = "01101500"
    USGS_API_URL = "https://waterservices.usgs.gov/nwis/iv/"

    async def get_river_conditions(self) -> Dict[str, Any]:
        """Fetch current Ipswich River conditions from USGS.

        Returns:
            Dictionary with flow rate, water level, and status
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    self.USGS_API_URL,
                    params={
                        "format": "json",
                        "sites": self.USGS_GAUGE_ID,
                        "parameterCd": "00060,00065",  # Discharge and gauge height
                        "siteStatus": "active",
                    },
                )
                response.raise_for_status()
                data = response.json()

                # Parse the USGS response
                timeseries = data.get("value", {}).get("timeSeries", [])

                result = {
                    "gauge_name": "Ipswich River at South Middleton",
                    "flow_cfs": None,
                    "water_level_ft": None,
                    "status": "unknown",
                }

                for series in timeseries:
                    param = series.get("variable", {}).get("variableCode", [{}])[0].get("value", "")
                    values = series.get("values", [{}])[0].get("value", [])

                    if values:
                        latest = values[-1].get("value")
                        if param == "00060":  # Discharge (cubic feet per second)
                            result["flow_cfs"] = float(latest) if latest else None
                        elif param == "00065":  # Gauge height (feet)
                            result["water_level_ft"] = float(latest) if latest else None

                # Determine river status based on flow
                if result["flow_cfs"]:
                    flow = result["flow_cfs"]
                    if flow < 10:
                        result["status"] = "very low"
                    elif flow < 50:
                        result["status"] = "low"
                    elif flow < 150:
                        result["status"] = "normal"
                    elif flow < 500:
                        result["status"] = "high"
                    else:
                        result["status"] = "flood stage"

                logger.info(f"Fetched river conditions: {result['status']} flow")
                return result

        except httpx.HTTPError as e:
            logger.error(f"Error fetching USGS river data: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error with USGS: {e}")
            return {}

    def format_for_story(self, conditions: Dict[str, Any]) -> str:
        """Format river conditions for inclusion in story context."""
        if not conditions or not conditions.get("flow_cfs"):
            return ""

        lines = ["## Ipswich River Conditions (from USGS)"]
        lines.append(f"- Flow rate: {conditions['flow_cfs']:.1f} cubic feet per second ({conditions['status']})")
        if conditions.get("water_level_ft"):
            lines.append(f"- Water level: {conditions['water_level_ft']:.2f} feet at South Middleton gauge")

        return "\n".join(lines)


async def gather_additional_context(ebird_api_key: Optional[str] = None) -> str:
    """Gather all additional context for story generation.

    Args:
        ebird_api_key: Optional eBird API key for bird sightings

    Returns:
        Formatted string with all additional context
    """
    context_parts = []

    # Bird sightings (if API key available)
    if ebird_api_key:
        ebird = EBirdService(api_key=ebird_api_key)
        sightings = await ebird.get_recent_sightings(days_back=3, max_results=5)
        if sightings:
            context_parts.append(ebird.format_for_story(sightings))

    # NOAA marine/coastal conditions
    noaa = NOAAMarineService()
    forecast = await noaa.get_marine_forecast()
    if forecast:
        context_parts.append(noaa.format_for_story(forecast))

    # River conditions
    river = IpswichRiverService()
    river_conditions = await river.get_river_conditions()
    if river_conditions:
        context_parts.append(river.format_for_story(river_conditions))

    # Town events (placeholder for future)
    # town = TownCalendarService()
    # events = await town.get_upcoming_meetings()
    # if events:
    #     context_parts.append(town.format_for_story(events))

    return "\n\n".join(context_parts)
