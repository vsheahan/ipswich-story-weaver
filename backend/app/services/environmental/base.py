"""Base utilities and shared components for environmental services.

This module provides:
- Common constants for Ipswich, MA location
- ERDDAPClient for querying NOAA CoastWatch ERDDAP servers
- Shared dataclasses used across multiple services
- Error handling utilities
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)

# Ipswich, MA coordinates
IPSWICH_LAT = 42.6792
IPSWICH_LON = -70.8417

# Bounding box for coastal/ocean queries (covers Plum Island, Crane Beach, Ipswich Bay)
IPSWICH_BBOX = {
    "lat_min": 42.55,
    "lat_max": 42.80,
    "lon_min": -71.0,
    "lon_max": -70.65,
}

# Default timeout for external API calls
DEFAULT_TIMEOUT = 15.0


@dataclass
class DataFetchResult:
    """Result wrapper for data fetching operations."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    source: str = ""


class ERDDAPClient:
    """Client for querying NOAA CoastWatch ERDDAP servers.

    ERDDAP (Environmental Research Division's Data Access Program) provides
    access to gridded environmental data including SST, ocean color, and wave data.
    """

    DEFAULT_BASE_URL = "https://coastwatch.noaa.gov/erddap"

    def __init__(self, base_url: Optional[str] = None, timeout: float = DEFAULT_TIMEOUT):
        """Initialize ERDDAP client.

        Args:
            base_url: ERDDAP server URL. Defaults to NOAA CoastWatch.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.timeout = timeout

    async def query_griddap(
        self,
        dataset_id: str,
        variables: list[str],
        lat_range: tuple[float, float],
        lon_range: tuple[float, float],
        time_range: Optional[tuple[str, str]] = None,
    ) -> Optional[dict]:
        """Query a griddap dataset for the specified region and time.

        Args:
            dataset_id: ERDDAP dataset identifier
            variables: List of variable names to fetch
            lat_range: (min_lat, max_lat) tuple
            lon_range: (min_lon, max_lon) tuple
            time_range: Optional (start_time, end_time) in ISO format.
                       Defaults to latest available data.

        Returns:
            JSON response data or None on error
        """
        # Build the constraint string
        var_str = ",".join(variables)

        # Time constraint - default to last available
        if time_range:
            time_constraint = f"[({time_range[0]}):1:({time_range[1]})]"
        else:
            time_constraint = "[(last)]"

        # Spatial constraints
        lat_constraint = f"[({lat_range[0]}):1:({lat_range[1]})]"
        lon_constraint = f"[({lon_range[0]}):1:({lon_range[1]})]"

        # Build URL
        url = (
            f"{self.base_url}/griddap/{dataset_id}.json?"
            f"{var_str}{time_constraint}{lat_constraint}{lon_constraint}"
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException:
            logger.warning(f"ERDDAP request timed out for {dataset_id}")
            return None
        except httpx.HTTPStatusError as e:
            logger.warning(f"ERDDAP HTTP error for {dataset_id}: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"ERDDAP unexpected error for {dataset_id}: {e}")
            return None

    async def get_latest_value(
        self,
        dataset_id: str,
        variable: str,
        lat: float = IPSWICH_LAT,
        lon: float = IPSWICH_LON,
        search_radius: float = 0.1,
    ) -> Optional[float]:
        """Get the latest value for a single variable at a point.

        Uses a small bounding box around the point to find the nearest data.

        Args:
            dataset_id: ERDDAP dataset identifier
            variable: Variable name to fetch
            lat: Latitude of point
            lon: Longitude of point
            search_radius: Radius in degrees to search for data

        Returns:
            The value or None if not available
        """
        lat_range = (lat - search_radius, lat + search_radius)
        lon_range = (lon - search_radius, lon + search_radius)

        data = await self.query_griddap(
            dataset_id=dataset_id,
            variables=[variable],
            lat_range=lat_range,
            lon_range=lon_range,
        )

        if not data:
            return None

        try:
            # ERDDAP returns data in a table format
            table = data.get("table", {})
            rows = table.get("rows", [])

            if not rows:
                return None

            # Find the column index for our variable
            column_names = table.get("columnNames", [])
            if variable not in column_names:
                return None

            var_idx = column_names.index(variable)

            # Get values, filtering out NaN
            values = []
            for row in rows:
                val = row[var_idx]
                if val is not None and val == val:  # NaN check
                    values.append(val)

            if not values:
                return None

            # Return average of available values in the region
            return sum(values) / len(values)

        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error parsing ERDDAP response for {dataset_id}: {e}")
            return None


def kelvin_to_fahrenheit(kelvin: float) -> float:
    """Convert temperature from Kelvin to Fahrenheit."""
    return (kelvin - 273.15) * 9/5 + 32


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert temperature from Celsius to Fahrenheit."""
    return celsius * 9/5 + 32


def meters_to_feet(meters: float) -> float:
    """Convert length from meters to feet."""
    return meters * 3.28084


def degrees_to_compass(degrees: float) -> str:
    """Convert degrees (0-360) to compass direction."""
    directions = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"
    ]
    idx = round(degrees / 22.5) % 16
    return directions[idx]


def get_season(date: Optional[datetime] = None) -> str:
    """Get the current season for the Northern Hemisphere."""
    if date is None:
        date = datetime.now()

    month = date.month
    if month in (12, 1, 2):
        return "winter"
    elif month in (3, 4, 5):
        return "spring"
    elif month in (6, 7, 8):
        return "summer"
    else:
        return "autumn"
