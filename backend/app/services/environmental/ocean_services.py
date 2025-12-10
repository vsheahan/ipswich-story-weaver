"""Ocean-based environmental services.

This module provides:
- SeaSurfaceTempService: SST from NOAA CoastWatch ERDDAP
- OceanColorService: Chlorophyll concentration from ERDDAP
- WaveWatchService: Wave height, period, direction from WaveWatch III
- HABForecastService: Harmful algal bloom status
"""

import logging
import math
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import Optional

import httpx

from app.services.environmental.base import (
    ERDDAPClient,
    IPSWICH_LAT,
    IPSWICH_LON,
    IPSWICH_BBOX,
    DEFAULT_TIMEOUT,
    kelvin_to_fahrenheit,
    celsius_to_fahrenheit,
    meters_to_feet,
    degrees_to_compass,
    get_season,
)

logger = logging.getLogger(__name__)


@dataclass
class SeaSurfaceTempContext:
    """Sea surface temperature for story generation."""
    temp_fahrenheit: Optional[float] = None
    temp_celsius: Optional[float] = None
    anomaly: Optional[str] = None  # "warmer", "cooler", "normal"
    description: str = "Sea surface temperature data unavailable"


@dataclass
class OceanColorContext:
    """Ocean color/chlorophyll for story generation."""
    chlorophyll_mg_m3: Optional[float] = None
    bloom_status: str = "normal"  # "normal", "elevated", "bloom"
    description: str = "Ocean color data unavailable"


@dataclass
class WaveContext:
    """Wave conditions for story generation."""
    significant_height_ft: Optional[float] = None
    peak_period_seconds: Optional[float] = None
    direction: Optional[str] = None  # compass direction
    direction_degrees: Optional[float] = None
    energy_description: str = "calm"  # "calm", "light", "moderate", "rough", "high"
    description: str = "Wave data unavailable"


@dataclass
class HABContext:
    """Harmful algal bloom status for story generation."""
    status: str = "none"  # "none", "watch", "warning", "advisory", "closure"
    species: Optional[str] = None
    affected_area: Optional[str] = None
    description: str = "No harmful algal bloom advisories"


# Typical SST ranges for Ipswich Bay by month (Fahrenheit)
MONTHLY_SST_NORMALS = {
    1: 38, 2: 36, 3: 38, 4: 44, 5: 52, 6: 60,
    7: 66, 8: 68, 9: 64, 10: 56, 11: 48, 12: 42
}

# Chlorophyll thresholds (mg/m³)
CHLOROPHYLL_THRESHOLDS = {
    "low": 0.5,
    "normal": 2.0,
    "elevated": 5.0,
    "bloom": 10.0,
}


class SeaSurfaceTempService:
    """Service for sea surface temperature from NOAA CoastWatch.

    Uses the Multi-scale Ultra-high Resolution (MUR) SST dataset via ERDDAP.
    """

    # ERDDAP dataset for blended SST
    DATASET_ID = "jplMURSST41"
    VARIABLE = "analysed_sst"

    def __init__(self):
        """Initialize SST service with ERDDAP client."""
        self.erddap = ERDDAPClient(
            base_url="https://coastwatch.pfeg.noaa.gov/erddap",
            timeout=20.0
        )

    async def get_sst(self) -> SeaSurfaceTempContext:
        """Get current sea surface temperature for Ipswich Bay area.

        Returns:
            SeaSurfaceTempContext with temperature and anomaly
        """
        try:
            # Query ERDDAP for latest SST
            sst_celsius = await self.erddap.get_latest_value(
                dataset_id=self.DATASET_ID,
                variable=self.VARIABLE,
                lat=IPSWICH_LAT,
                lon=IPSWICH_LON,
                search_radius=0.15,  # ~10 mile radius
            )

            if sst_celsius is None:
                return SeaSurfaceTempContext()

            # Convert to Fahrenheit
            sst_fahrenheit = celsius_to_fahrenheit(sst_celsius)

            # Determine anomaly relative to climatology
            month = datetime.now().month
            normal_temp = MONTHLY_SST_NORMALS.get(month, 50)
            diff = sst_fahrenheit - normal_temp

            if diff > 3:
                anomaly = "warmer"
                anomaly_desc = f"{abs(diff):.1f}°F above normal"
            elif diff < -3:
                anomaly = "cooler"
                anomaly_desc = f"{abs(diff):.1f}°F below normal"
            else:
                anomaly = "normal"
                anomaly_desc = "near normal"

            description = f"Sea surface temperature: {sst_fahrenheit:.1f}°F ({anomaly_desc})"

            return SeaSurfaceTempContext(
                temp_fahrenheit=round(sst_fahrenheit, 1),
                temp_celsius=round(sst_celsius, 1),
                anomaly=anomaly,
                description=description,
            )

        except Exception as e:
            logger.error(f"SST service error: {e}")
            return SeaSurfaceTempContext()

    def format_for_story(self, context: SeaSurfaceTempContext) -> str:
        """Format SST info for story context."""
        if context.temp_fahrenheit is None:
            return ""

        lines = ["## Sea Surface Temperature (NOAA MUR SST)"]
        lines.append(f"- {context.description}")

        return "\n".join(lines)


class OceanColorService:
    """Service for ocean color and chlorophyll concentration.

    Uses Sentinel-3 OLCI satellite data via NOAA CoastWatch ERDDAP.
    """

    # ERDDAP dataset for Sentinel-3 OLCI chlorophyll (works well for our region)
    DATASET_ID = "noaacwNPPN20S3ASCIDINEOFDaily"
    VARIABLE = "chlor_a"

    def __init__(self):
        """Initialize ocean color service with ERDDAP client."""
        self.base_url = "https://coastwatch.noaa.gov/erddap"
        self.timeout = 20.0

    async def get_ocean_color(self) -> OceanColorContext:
        """Get current chlorophyll concentration for Ipswich Bay.

        Returns:
            OceanColorContext with chlorophyll level and bloom status
        """
        try:
            # Query ERDDAP directly with proper format
            # This dataset has altitude dimension at 0.0
            url = (
                f"{self.base_url}/griddap/{self.DATASET_ID}.json?"
                f"{self.VARIABLE}[(last)][(0.0)]"
                f"[({IPSWICH_LAT - 0.5}):({IPSWICH_LAT + 0.5})]"
                f"[({IPSWICH_LON - 0.5}):({IPSWICH_LON + 0.5})]"
            )

            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

            # Parse the response
            table = data.get("table", {})
            rows = table.get("rows", [])
            column_names = table.get("columnNames", [])

            if not rows or self.VARIABLE not in column_names:
                return await self._get_fallback_estimate()

            var_idx = column_names.index(self.VARIABLE)

            # Get valid (non-null) values
            values = [row[var_idx] for row in rows if row[var_idx] is not None]

            if not values:
                return await self._get_fallback_estimate()

            # Use median to avoid outliers
            values.sort()
            chlor_a = values[len(values) // 2]

            if chlor_a is None:
                # Try alternate dataset
                return await self._get_fallback_estimate()

            # Classify bloom status
            if chlor_a < CHLOROPHYLL_THRESHOLDS["normal"]:
                status = "normal"
                description = f"Normal ocean color (chlorophyll: {chlor_a:.2f} mg/m³)"
            elif chlor_a < CHLOROPHYLL_THRESHOLDS["elevated"]:
                status = "elevated"
                description = f"Elevated chlorophyll ({chlor_a:.2f} mg/m³) - increased phytoplankton"
            else:
                status = "bloom"
                description = f"Phytoplankton bloom detected ({chlor_a:.2f} mg/m³)"

            return OceanColorContext(
                chlorophyll_mg_m3=round(chlor_a, 2),
                bloom_status=status,
                description=description,
            )

        except Exception as e:
            logger.error(f"Ocean color service error: {e}")
            return await self._get_fallback_estimate()

    async def _get_fallback_estimate(self) -> OceanColorContext:
        """Provide seasonal estimate when real data unavailable."""
        season = get_season()

        # Typical seasonal patterns for Gulf of Maine
        seasonal_estimates = {
            "spring": (3.0, "elevated", "Spring bloom season - phytoplankton increasing"),
            "summer": (1.5, "normal", "Summer conditions - moderate productivity"),
            "autumn": (2.5, "elevated", "Fall bloom - secondary productivity peak"),
            "winter": (0.8, "normal", "Winter conditions - low productivity"),
        }

        chlor, status, desc = seasonal_estimates.get(
            season, (1.5, "normal", "Ocean color data unavailable")
        )

        return OceanColorContext(
            chlorophyll_mg_m3=chlor,
            bloom_status=status,
            description=f"{desc} (seasonal estimate)",
        )

    def format_for_story(self, context: OceanColorContext) -> str:
        """Format ocean color info for story context."""
        if context.bloom_status == "normal" and "unavailable" in context.description:
            return ""

        lines = ["## Ocean Color (NOAA VIIRS)"]
        lines.append(f"- {context.description}")

        return "\n".join(lines)


class WaveWatchService:
    """Service for wave data from NOAA WaveWatch III model.

    Uses the global WaveWatch III model output via ERDDAP.
    Note: WaveWatch III uses 0-360 longitude format and has a depth dimension.
    """

    # ERDDAP dataset for WaveWatch III global
    DATASET_ID = "NWW3_Global_Best"

    def __init__(self):
        """Initialize wave service."""
        self.base_url = "https://coastwatch.pfeg.noaa.gov/erddap"
        self.timeout = 20.0

    def _lon_to_360(self, lon: float) -> float:
        """Convert longitude from -180/180 to 0-360 format."""
        if lon < 0:
            return 360 + lon
        return lon

    async def _query_variable(self, variable: str) -> Optional[float]:
        """Query a single WaveWatch III variable."""
        # Convert Ipswich longitude to 0-360 format
        lon_360 = self._lon_to_360(IPSWICH_LON)  # -70.84 -> ~289.16

        # Build ERDDAP query with depth dimension at 0.0
        url = (
            f"{self.base_url}/griddap/{self.DATASET_ID}.json?"
            f"{variable}[(last)][(0.0)]"
            f"[({IPSWICH_LAT - 0.5}):({IPSWICH_LAT + 0.5})]"
            f"[({lon_360 - 0.5}):({lon_360 + 0.5})]"
        )

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

            table = data.get("table", {})
            rows = table.get("rows", [])
            column_names = table.get("columnNames", [])

            if not rows or variable not in column_names:
                return None

            var_idx = column_names.index(variable)

            # Get valid (non-null) values
            values = [row[var_idx] for row in rows if row[var_idx] is not None]

            if not values:
                return None

            # Return average of values in the area
            return sum(values) / len(values)

        except Exception as e:
            logger.warning(f"WaveWatch query error for {variable}: {e}")
            return None

    async def get_wave_conditions(self) -> WaveContext:
        """Get current wave conditions for Ipswich Bay.

        Returns:
            WaveContext with wave height, period, and direction
        """
        try:
            # WaveWatch III variables
            # Thgt = Total significant wave height (meters)
            # Tper = Peak period (seconds)
            # Tdir = Peak direction (degrees)

            # Query for significant wave height
            hs_meters = await self._query_variable("Thgt")

            # Query for peak period
            tp_seconds = await self._query_variable("Tper")

            # Query for direction
            dp_degrees = await self._query_variable("Tdir")

            if hs_meters is None:
                return WaveContext()

            # Convert height to feet
            hs_feet = meters_to_feet(hs_meters)

            # Convert direction to compass
            direction = degrees_to_compass(dp_degrees) if dp_degrees else None

            # Classify wave energy
            if hs_feet < 1:
                energy = "calm"
                energy_desc = "Calm seas"
            elif hs_feet < 3:
                energy = "light"
                energy_desc = "Light chop"
            elif hs_feet < 6:
                energy = "moderate"
                energy_desc = "Moderate swells"
            elif hs_feet < 10:
                energy = "rough"
                energy_desc = "Rough seas"
            else:
                energy = "high"
                energy_desc = "High seas"

            # Build description
            desc_parts = [f"{energy_desc} ({hs_feet:.1f} ft)"]
            if tp_seconds:
                desc_parts.append(f"{tp_seconds:.0f}s period")
            if direction:
                desc_parts.append(f"from {direction}")

            return WaveContext(
                significant_height_ft=round(hs_feet, 1),
                peak_period_seconds=round(tp_seconds, 1) if tp_seconds else None,
                direction=direction,
                direction_degrees=dp_degrees,
                energy_description=energy,
                description=" - ".join(desc_parts),
            )

        except Exception as e:
            logger.error(f"WaveWatch service error: {e}")
            return WaveContext()

    def format_for_story(self, context: WaveContext) -> str:
        """Format wave info for story context."""
        if context.significant_height_ft is None:
            return ""

        lines = ["## Wave Conditions (NOAA WaveWatch III)"]
        lines.append(f"- {context.description}")

        return "\n".join(lines)


class HABForecastService:
    """Service for Harmful Algal Bloom forecasts.

    Checks Massachusetts Division of Marine Fisheries and NOAA HAB forecasts.
    Since there's no direct API, this uses seasonal patterns and static data
    with optional web data enhancement.
    """

    # HAB-prone months for Massachusetts (typically late summer/fall)
    HAB_SEASON_MONTHS = [7, 8, 9, 10]

    # Known HAB species in Massachusetts waters
    HAB_SPECIES = {
        "alexandrium": "Alexandrium catenella (PSP - paralytic shellfish poisoning)",
        "pseudo-nitzschia": "Pseudo-nitzschia (ASP - amnesic shellfish poisoning)",
        "dinophysis": "Dinophysis (DSP - diarrhetic shellfish poisoning)",
    }

    # MA DMF shellfish status page (for reference)
    MA_DMF_URL = "https://www.mass.gov/info-details/shellfish-sanitation-and-management"

    async def get_hab_status(self) -> HABContext:
        """Get current HAB status for Massachusetts coastal waters.

        Returns:
            HABContext with bloom status and any advisories
        """
        month = datetime.now().month

        # Outside HAB season
        if month not in self.HAB_SEASON_MONTHS:
            return HABContext(
                status="none",
                description="Outside typical HAB season for Massachusetts waters",
            )

        # During HAB season, provide cautionary context
        # In a production system, this would scrape MA DMF or NOAA bulletins
        try:
            # Attempt to get real status (placeholder for web scraping)
            real_status = await self._check_ma_dmf_status()
            if real_status:
                return real_status
        except Exception as e:
            logger.debug(f"Could not fetch live HAB status: {e}")

        # Seasonal default during HAB-prone months
        return HABContext(
            status="watch",
            species="Alexandrium catenella",
            affected_area="Massachusetts Bay",
            description="HAB season active - check MA DMF for current shellfish advisories",
        )

    async def _check_ma_dmf_status(self) -> Optional[HABContext]:
        """Attempt to fetch real HAB status from MA DMF.

        This is a placeholder - actual implementation would parse the
        MA DMF website or their data feeds.
        """
        # For now, return None to use seasonal defaults
        # Future: implement web scraping of MA DMF shellfish closures
        return None

    def format_for_story(self, context: HABContext) -> str:
        """Format HAB info for story context."""
        if context.status == "none":
            return ""

        lines = ["## Harmful Algal Bloom Status"]
        lines.append(f"- Status: {context.status.upper()}")
        if context.species:
            lines.append(f"- Species of concern: {context.species}")
        lines.append(f"- {context.description}")

        return "\n".join(lines)
