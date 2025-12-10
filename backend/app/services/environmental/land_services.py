"""Land-based environmental services.

This module provides:
- DroughtMonitorService: US Drought Monitor data for Essex County
- SnowCoverService: NOAA SNODAS snow depth and coverage
- NDVIService: Vegetation greenness index from MODIS
- CoastalErosionService: MA CZM coastal change data (static)
"""

import logging
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import Optional

import httpx

from app.services.environmental.base import (
    IPSWICH_LAT,
    IPSWICH_LON,
    DEFAULT_TIMEOUT,
    get_season,
)

logger = logging.getLogger(__name__)

# Essex County, MA FIPS code
ESSEX_COUNTY_FIPS = "25009"


@dataclass
class DroughtContext:
    """Drought conditions for story generation."""
    severity: str = "none"  # "none", "D0", "D1", "D2", "D3", "D4"
    severity_name: str = "No drought"
    percent_area_affected: Optional[float] = None
    description: str = "No drought conditions in Essex County"


@dataclass
class SnowCoverContext:
    """Snow cover conditions for story generation."""
    depth_inches: Optional[float] = None
    water_equivalent_inches: Optional[float] = None
    coverage: str = "none"  # "none", "patchy", "continuous"
    description: str = "No snow cover"


@dataclass
class VegetationContext:
    """Vegetation index for story generation."""
    ndvi_value: Optional[float] = None
    status: str = "normal"  # "dormant", "early_green", "greening", "peak", "senescent", "dormant"
    seasonal_note: Optional[str] = None


@dataclass
class CoastalErosionContext:
    """Coastal erosion status for story generation."""
    status: str = "stable"  # "stable", "eroding", "accreting"
    high_risk_areas: list[str] = None
    recent_changes: Optional[str] = None

    def __post_init__(self):
        if self.high_risk_areas is None:
            self.high_risk_areas = []


# Drought severity descriptions
DROUGHT_LEVELS = {
    "None": ("none", "No drought", "Conditions are normal"),
    "D0": ("D0", "Abnormally Dry", "Short-term dryness may slow planting or growth"),
    "D1": ("D1", "Moderate Drought", "Some damage to crops; streams and wells low"),
    "D2": ("D2", "Severe Drought", "Crop losses likely; water shortages common"),
    "D3": ("D3", "Extreme Drought", "Major crop losses; widespread water restrictions"),
    "D4": ("D4", "Exceptional Drought", "Exceptional and widespread crop losses"),
}


class DroughtMonitorService:
    """Service for US Drought Monitor data.

    Uses the USDM REST API to fetch drought conditions for Essex County, MA.
    https://droughtmonitor.unl.edu/
    """

    BASE_URL = "https://usdmdataservices.unl.edu/api/CountyStatistics"

    async def get_drought_status(self, target_date: Optional[date] = None) -> DroughtContext:
        """Get current drought status for Essex County.

        Args:
            target_date: Date to check. Defaults to most recent available.

        Returns:
            DroughtContext with current conditions
        """
        if target_date is None:
            # USDM updates weekly on Thursdays; get most recent
            target_date = date.today()

        # Format date as YYYY-MM-DD
        date_str = target_date.strftime("%Y-%m-%d")

        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                response = await client.get(
                    f"{self.BASE_URL}/GetDroughtSeverityStatisticsByAreaPercent",
                    params={
                        "aoi": ESSEX_COUNTY_FIPS,
                        "startdate": date_str,
                        "enddate": date_str,
                        "statisticsType": "1",
                    },
                )
                response.raise_for_status()
                data = response.json()

                if not data:
                    return DroughtContext()

                # Parse the response - find the highest severity with coverage
                latest = data[-1] if isinstance(data, list) else data

                # Check severity levels from worst to best
                for level in ["D4", "D3", "D2", "D1", "D0"]:
                    pct = latest.get(level, 0)
                    if pct and float(pct) > 0:
                        severity, name, desc = DROUGHT_LEVELS[level]
                        return DroughtContext(
                            severity=severity,
                            severity_name=name,
                            percent_area_affected=float(pct),
                            description=f"{name}: {desc}. {pct:.1f}% of Essex County affected.",
                        )

                return DroughtContext()

        except httpx.TimeoutException:
            logger.warning("Drought Monitor request timed out")
            return DroughtContext()
        except httpx.HTTPStatusError as e:
            logger.warning(f"Drought Monitor HTTP error: {e.response.status_code}")
            return DroughtContext()
        except Exception as e:
            logger.error(f"Drought Monitor unexpected error: {e}")
            return DroughtContext()

    def format_for_story(self, context: DroughtContext) -> str:
        """Format drought info for story context."""
        if context.severity == "none":
            return ""

        lines = ["## Drought Conditions (US Drought Monitor)"]
        lines.append(f"- {context.severity_name}")
        lines.append(f"- {context.description}")

        return "\n".join(lines)


class SnowCoverService:
    """Service for NOAA SNODAS snow cover data.

    Uses NOAA NOHRSC (National Operational Hydrologic Remote Sensing Center)
    MapServer to query snow depth and snow water equivalent.
    """

    BASE_URL = "https://mapservices.weather.noaa.gov/raster/rest/services/snow/NOHRSC_Snow_Analysis/MapServer/identify"

    async def get_snow_cover(self) -> SnowCoverContext:
        """Get current snow cover for Ipswich area.

        Returns:
            SnowCoverContext with snow depth and coverage
        """
        try:
            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
                response = await client.get(
                    self.BASE_URL,
                    params={
                        "geometry": f"{IPSWICH_LON},{IPSWICH_LAT}",
                        "geometryType": "esriGeometryPoint",
                        "sr": "4326",
                        "layers": "all:0,1",  # Snow depth and SWE layers
                        "tolerance": "2",
                        "mapExtent": f"{IPSWICH_LON-0.1},{IPSWICH_LAT-0.1},{IPSWICH_LON+0.1},{IPSWICH_LAT+0.1}",
                        "imageDisplay": "100,100,96",
                        "returnGeometry": "false",
                        "f": "json",
                    },
                )
                response.raise_for_status()
                data = response.json()

                results = data.get("results", [])
                if not results:
                    return SnowCoverContext()

                depth_inches = None
                swe_inches = None

                for result in results:
                    layer_name = result.get("layerName", "").lower()
                    value = result.get("attributes", {}).get("Pixel Value")

                    if value and value != "NoData":
                        try:
                            val = float(value)
                            if "depth" in layer_name:
                                # Convert mm to inches
                                depth_inches = val / 25.4
                            elif "water" in layer_name or "swe" in layer_name:
                                # Convert mm to inches
                                swe_inches = val / 25.4
                        except (ValueError, TypeError):
                            continue

                # Determine coverage description
                if depth_inches is None or depth_inches < 0.1:
                    coverage = "none"
                    description = "No snow cover"
                elif depth_inches < 1:
                    coverage = "patchy"
                    description = f"Light patchy snow cover ({depth_inches:.1f} inches)"
                elif depth_inches < 6:
                    coverage = "continuous"
                    description = f"Snow cover of {depth_inches:.1f} inches"
                else:
                    coverage = "continuous"
                    description = f"Deep snow pack ({depth_inches:.1f} inches)"

                return SnowCoverContext(
                    depth_inches=depth_inches,
                    water_equivalent_inches=swe_inches,
                    coverage=coverage,
                    description=description,
                )

        except httpx.TimeoutException:
            logger.warning("Snow cover request timed out")
            return SnowCoverContext()
        except httpx.HTTPStatusError as e:
            logger.warning(f"Snow cover HTTP error: {e.response.status_code}")
            return SnowCoverContext()
        except Exception as e:
            logger.error(f"Snow cover unexpected error: {e}")
            return SnowCoverContext()

    def format_for_story(self, context: SnowCoverContext) -> str:
        """Format snow cover info for story context."""
        if context.coverage == "none":
            return ""

        lines = ["## Snow Cover (NOAA SNODAS)"]
        lines.append(f"- {context.description}")
        if context.water_equivalent_inches:
            lines.append(f"- Snow water equivalent: {context.water_equivalent_inches:.1f} inches")

        return "\n".join(lines)


class NDVIService:
    """Service for NDVI (Normalized Difference Vegetation Index) data.

    Uses NASA LP DAAC MODIS data to assess vegetation greenness.
    Since real-time NDVI requires substantial data processing, this service
    uses seasonal estimates with optional API enhancement.
    """

    # Typical NDVI ranges for coastal Massachusetts by season
    SEASONAL_NDVI = {
        "winter": (0.1, 0.25, "dormant", "Vegetation dormant; deciduous trees bare"),
        "spring": (0.3, 0.5, "greening", "Spring green-up underway; buds breaking"),
        "summer": (0.6, 0.8, "peak", "Peak greenness; full canopy"),
        "autumn": (0.3, 0.5, "senescent", "Autumn colors; leaves falling"),
    }

    # MODIS NDVI approximate values for late-season transitions
    MONTHLY_ADJUSTMENTS = {
        1: -0.1,  # January - deep winter
        2: -0.05,  # February - late winter
        3: 0.0,   # March - early spring
        4: 0.1,   # April - spring greening
        5: 0.15,  # May - rapid growth
        6: 0.1,   # June - approaching peak
        7: 0.0,   # July - peak
        8: -0.05, # August - late summer
        9: -0.1,  # September - early senescence
        10: -0.15, # October - fall colors
        11: -0.2,  # November - late autumn
        12: -0.1,  # December - early winter
    }

    def get_vegetation_status(self, target_date: Optional[date] = None) -> VegetationContext:
        """Get vegetation status estimate for Ipswich area.

        Args:
            target_date: Date to check. Defaults to today.

        Returns:
            VegetationContext with NDVI estimate and status
        """
        if target_date is None:
            target_date = date.today()

        season = get_season(datetime.combine(target_date, datetime.min.time()))
        base_min, base_max, status, note = self.SEASONAL_NDVI[season]

        # Apply monthly adjustment
        adjustment = self.MONTHLY_ADJUSTMENTS.get(target_date.month, 0)
        ndvi_estimate = ((base_min + base_max) / 2) + adjustment

        # Clamp to valid range
        ndvi_estimate = max(0.0, min(1.0, ndvi_estimate))

        # Refine status based on specific month
        month = target_date.month
        if month == 3:
            status = "early_green"
            note = "First signs of spring; earliest buds swelling"
        elif month == 4:
            status = "greening"
            note = "Spring green-up accelerating; marsh grass emerging"
        elif month == 5:
            status = "greening"
            note = "Rapid growth; woodland canopy filling in"
        elif month == 10:
            status = "senescent"
            note = "Peak fall color; maples and oaks turning"
        elif month == 11:
            status = "senescent"
            note = "Late autumn; most leaves fallen"

        return VegetationContext(
            ndvi_value=round(ndvi_estimate, 2),
            status=status,
            seasonal_note=note,
        )

    def format_for_story(self, context: VegetationContext) -> str:
        """Format vegetation info for story context."""
        lines = ["## Vegetation Status (NDVI estimate)"]
        lines.append(f"- Status: {context.status.replace('_', ' ').title()}")
        if context.ndvi_value:
            lines.append(f"- NDVI: {context.ndvi_value:.2f}")
        if context.seasonal_note:
            lines.append(f"- {context.seasonal_note}")

        return "\n".join(lines)


class CoastalErosionService:
    """Service for coastal erosion and accretion data.

    Uses static data from MA Coastal Zone Management MORIS system.
    This data changes slowly (updated after major storms) so static
    knowledge is appropriate.
    """

    # Known erosion hotspots around Ipswich (from MA CZM data)
    EROSION_HOTSPOTS = {
        "Plum Island": {
            "status": "eroding",
            "rate": "1-3 feet per year in some areas",
            "notes": "Southern end experiencing significant erosion; beach nourishment ongoing",
        },
        "Crane Beach": {
            "status": "stable",
            "rate": "minimal change",
            "notes": "Protected barrier beach with natural dune migration",
        },
        "Castle Neck": {
            "status": "dynamic",
            "rate": "seasonal changes",
            "notes": "Natural barrier system with seasonal overwash",
        },
        "Great Neck": {
            "status": "stable",
            "rate": "minimal change",
            "notes": "Rocky shoreline with minimal erosion",
        },
    }

    def get_erosion_status(self) -> CoastalErosionContext:
        """Get coastal erosion status for Ipswich area.

        Returns:
            CoastalErosionContext with erosion information
        """
        high_risk = [
            area for area, data in self.EROSION_HOTSPOTS.items()
            if data["status"] == "eroding"
        ]

        # Determine overall status
        if high_risk:
            status = "eroding"
            changes = f"Active erosion at {', '.join(high_risk)}"
        else:
            status = "stable"
            changes = "No significant recent changes"

        return CoastalErosionContext(
            status=status,
            high_risk_areas=high_risk,
            recent_changes=changes,
        )

    def format_for_story(self, context: CoastalErosionContext) -> str:
        """Format coastal erosion info for story context."""
        if context.status == "stable" and not context.high_risk_areas:
            return ""

        lines = ["## Coastal Change (MA CZM)"]
        if context.high_risk_areas:
            lines.append(f"- Areas with active erosion: {', '.join(context.high_risk_areas)}")
        if context.recent_changes:
            lines.append(f"- {context.recent_changes}")

        # Add specific notes for key areas
        for area in context.high_risk_areas:
            if area in self.EROSION_HOTSPOTS:
                info = self.EROSION_HOTSPOTS[area]
                lines.append(f"- {area}: {info['notes']}")

        return "\n".join(lines)
