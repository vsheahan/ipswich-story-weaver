"""Tide service for Ipswich coastal area."""

import logging
import math
from datetime import date, datetime, timedelta
from typing import Optional

import httpx

from app.core.config import get_settings
from app.schemas.story import TideContext

logger = logging.getLogger(__name__)
settings = get_settings()


class TideService:
    """Service for tide information for Ipswich Bay area.

    Uses NOAA Tides and Currents API when available, falls back to
    a deterministic simulation based on lunar cycles.
    """

    def __init__(self):
        self.station_id = settings.tide_station_id
        self.base_url = settings.tide_api_base_url

    async def get_tide_for_date(self, target_date: date) -> TideContext:
        """Get tide state for a specific date."""
        # Try to fetch real tide data
        tide_data = await self._fetch_tide_predictions(target_date)
        if tide_data:
            return tide_data

        # Fall back to simulated tides
        return self._simulate_tide(target_date)

    async def _fetch_tide_predictions(self, target_date: date) -> Optional[TideContext]:
        """Fetch tide predictions from NOAA API."""
        try:
            begin_date = target_date.strftime("%Y%m%d")
            end_date = (target_date + timedelta(days=1)).strftime("%Y%m%d")

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "begin_date": begin_date,
                        "end_date": end_date,
                        "station": self.station_id,
                        "product": "predictions",
                        "datum": "MLLW",
                        "units": "english",
                        "time_zone": "lst_ldt",
                        "format": "json",
                        "interval": "hilo",
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()

            predictions = data.get("predictions", [])
            if not predictions:
                return None

            # Find the most relevant tide event
            now = datetime.now()
            current_time = now.time()

            # Find closest tide event to current time
            closest_event = None
            min_diff = float("inf")

            for pred in predictions:
                pred_time = datetime.strptime(pred["t"], "%Y-%m-%d %H:%M")
                diff = abs((pred_time - now).total_seconds())
                if diff < min_diff:
                    min_diff = diff
                    closest_event = pred

            if closest_event:
                tide_type = closest_event.get("type", "").upper()
                height = float(closest_event.get("v", 0))
                event_time = datetime.strptime(closest_event["t"], "%Y-%m-%d %H:%M")

                # Determine state based on whether we're before or after the event
                if event_time > now:
                    state = "rising" if tide_type == "H" else "falling"
                else:
                    state = "falling" if tide_type == "H" else "rising"

                return TideContext(
                    state=state,
                    time_of_next=event_time,
                    height=height,
                )

            return None

        except httpx.HTTPError as e:
            logger.warning(f"Failed to fetch tide data: {e}")
            return None
        except Exception as e:
            logger.warning(f"Error processing tide data: {e}")
            return None

    def _simulate_tide(self, target_date: date) -> TideContext:
        """Simulate tide state based on lunar cycle.

        This provides a deterministic but realistic-feeling tide pattern
        when the real API is unavailable.
        """
        # Use a simplified tidal model
        # Tides roughly follow a 12.42 hour cycle (2 high tides per day)
        # We'll simulate based on day of year and time

        day_of_year = target_date.timetuple().tm_yday

        # Lunar cycle is approximately 29.5 days
        # Spring tides occur at new moon and full moon
        lunar_day = day_of_year % 29.5

        # Simulate the dominant tide cycle
        # Using a simple sinusoidal model
        cycle_position = (day_of_year * 2 * math.pi) / 0.517  # ~12.42 hour period scaled to days

        # Determine the tide state based on cycle position
        # Normalize to 0-1 range
        normalized = (math.sin(cycle_position) + 1) / 2

        if normalized > 0.75:
            state = "high"
        elif normalized > 0.5:
            state = "falling"
        elif normalized > 0.25:
            state = "low"
        else:
            state = "rising"

        # Calculate a simulated height (typical range 0-10 feet for this area)
        base_height = 5.0  # Mean tide level
        tide_amplitude = 4.5  # Typical amplitude

        # Add spring/neap variation based on lunar cycle
        spring_neap_factor = math.cos(lunar_day * 2 * math.pi / 14.75)
        adjusted_amplitude = tide_amplitude * (0.7 + 0.3 * abs(spring_neap_factor))

        height = base_height + adjusted_amplitude * math.sin(cycle_position)

        return TideContext(
            state=state,
            time_of_next=None,  # Simulated, so no specific time
            height=round(height, 1),
        )

    def get_tide_description(self, tide: TideContext) -> str:
        """Generate a narrative description of the tide state."""
        descriptions = {
            "high": "The tide is high, water lapping at the marsh edges.",
            "low": "The tide is out, revealing mudflats and tidal pools.",
            "rising": "The tide is coming in, slowly filling the estuaries.",
            "falling": "The tide is ebbing, water draining back to the sea.",
        }
        return descriptions.get(tide.state, "The tides turn as they always have.")
