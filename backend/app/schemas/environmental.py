"""Pydantic schemas for environmental data.

These schemas are used for API responses and data validation.
"""

from typing import Optional

from pydantic import BaseModel, Field


# Ocean schemas
class WaveContextSchema(BaseModel):
    """Wave conditions schema for API responses."""

    significant_height_ft: Optional[float] = Field(
        None, description="Significant wave height in feet"
    )
    peak_period_seconds: Optional[float] = Field(
        None, description="Peak wave period in seconds"
    )
    direction: Optional[str] = Field(
        None, description="Wave direction (compass)"
    )
    energy_description: str = Field(
        "calm", description="Wave energy level: calm, light, moderate, rough, high"
    )
    description: str = Field(
        "Wave data unavailable", description="Human-readable wave description"
    )


class SeaSurfaceTempSchema(BaseModel):
    """Sea surface temperature schema for API responses."""

    temp_fahrenheit: Optional[float] = Field(
        None, description="SST in Fahrenheit"
    )
    anomaly: Optional[str] = Field(
        None, description="Temperature anomaly: warmer, cooler, normal"
    )
    description: str = Field(
        "SST data unavailable", description="Human-readable SST description"
    )


class OceanColorSchema(BaseModel):
    """Ocean color/chlorophyll schema for API responses."""

    chlorophyll_mg_m3: Optional[float] = Field(
        None, description="Chlorophyll concentration in mg/m³"
    )
    bloom_status: str = Field(
        "normal", description="Bloom status: normal, elevated, bloom"
    )
    description: str = Field(
        "Ocean color data unavailable", description="Human-readable description"
    )


class HABSchema(BaseModel):
    """Harmful algal bloom schema for API responses."""

    status: str = Field(
        "none", description="HAB status: none, watch, warning, advisory, closure"
    )
    species: Optional[str] = Field(
        None, description="HAB species of concern"
    )
    affected_area: Optional[str] = Field(
        None, description="Affected geographic area"
    )
    description: str = Field(
        "No HAB advisories", description="Human-readable HAB description"
    )


# Atmosphere schemas
class AirQualitySchema(BaseModel):
    """Air quality schema for API responses."""

    pm25_aqi: Optional[int] = Field(
        None, description="PM2.5 AQI value"
    )
    ozone_aqi: Optional[int] = Field(
        None, description="Ozone AQI value"
    )
    overall_aqi: Optional[int] = Field(
        None, description="Overall AQI (highest of pollutants)"
    )
    category: str = Field(
        "Good", description="EPA AQI category"
    )
    category_color: str = Field(
        "green", description="Category color for display"
    )
    health_message: Optional[str] = Field(
        None, description="Health advisory message"
    )
    description: str = Field(
        "Air quality data unavailable", description="Human-readable AQ description"
    )


class SmokeSchema(BaseModel):
    """Wildfire smoke schema for API responses."""

    present: bool = Field(
        False, description="Whether smoke is detected"
    )
    intensity: str = Field(
        "none", description="Smoke intensity: none, light, moderate, heavy"
    )
    source_direction: Optional[str] = Field(
        None, description="Direction of smoke source"
    )
    description: str = Field(
        "No smoke detected", description="Human-readable smoke description"
    )


# Land schemas
class VegetationSchema(BaseModel):
    """Vegetation/NDVI schema for API responses."""

    ndvi_value: Optional[float] = Field(
        None, description="NDVI value (0-1)"
    )
    status: str = Field(
        "normal", description="Vegetation status: dormant, greening, peak, senescent"
    )
    seasonal_note: Optional[str] = Field(
        None, description="Seasonal vegetation note"
    )


class SnowCoverSchema(BaseModel):
    """Snow cover schema for API responses."""

    depth_inches: Optional[float] = Field(
        None, description="Snow depth in inches"
    )
    water_equivalent_inches: Optional[float] = Field(
        None, description="Snow water equivalent in inches"
    )
    coverage: str = Field(
        "none", description="Coverage: none, patchy, continuous"
    )
    description: str = Field(
        "No snow cover", description="Human-readable snow description"
    )


class DroughtSchema(BaseModel):
    """Drought status schema for API responses."""

    severity: str = Field(
        "none", description="Drought severity: none, D0, D1, D2, D3, D4"
    )
    severity_name: str = Field(
        "No drought", description="Human-readable severity name"
    )
    percent_area_affected: Optional[float] = Field(
        None, description="Percentage of area affected"
    )
    description: str = Field(
        "No drought conditions", description="Human-readable drought description"
    )


class CoastalErosionSchema(BaseModel):
    """Coastal erosion schema for API responses."""

    status: str = Field(
        "stable", description="Overall status: stable, eroding, accreting"
    )
    high_risk_areas: list[str] = Field(
        default_factory=list, description="Areas with active erosion"
    )
    recent_changes: Optional[str] = Field(
        None, description="Description of recent changes"
    )


# Astronomy schemas
class PlanetarySchema(BaseModel):
    """Planetary visibility schema for API responses."""

    visible_planets: list[str] = Field(
        default_factory=list, description="List of visible planets"
    )
    evening_planets: list[str] = Field(
        default_factory=list, description="Planets visible in evening"
    )
    morning_planets: list[str] = Field(
        default_factory=list, description="Planets visible before dawn"
    )
    notable_events: Optional[str] = Field(
        None, description="Notable astronomical events"
    )


class MeteorShowerSchema(BaseModel):
    """Meteor shower schema for API responses."""

    active_shower: Optional[str] = Field(
        None, description="Name of active meteor shower"
    )
    peak_tonight: bool = Field(
        False, description="Whether tonight is peak"
    )
    expected_rate: Optional[str] = Field(
        None, description="Expected meteor rate per hour"
    )
    radiant: Optional[str] = Field(
        None, description="Radiant constellation"
    )
    notes: Optional[str] = Field(
        None, description="Viewing notes"
    )


# Aggregated schema
class EnvironmentalContextSchema(BaseModel):
    """Complete environmental context schema for API responses."""

    # Ocean
    waves: Optional[WaveContextSchema] = None
    sst: Optional[SeaSurfaceTempSchema] = None
    ocean_color: Optional[OceanColorSchema] = None
    hab: Optional[HABSchema] = None

    # Atmosphere
    air_quality: Optional[AirQualitySchema] = None
    smoke: Optional[SmokeSchema] = None

    # Land
    vegetation: Optional[VegetationSchema] = None
    snow: Optional[SnowCoverSchema] = None
    drought: Optional[DroughtSchema] = None
    coastal_erosion: Optional[CoastalErosionSchema] = None

    # Astronomy
    planets: Optional[PlanetarySchema] = None
    meteor_shower: Optional[MeteorShowerSchema] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


def environmental_context_to_schema(context) -> EnvironmentalContextSchema:
    """Convert an EnvironmentalContext dataclass to schema for API response.

    Args:
        context: EnvironmentalContext from aggregator

    Returns:
        EnvironmentalContextSchema for API response
    """
    def to_dict(obj):
        """Convert dataclass to dict, handling None."""
        if obj is None:
            return None
        if hasattr(obj, "__dataclass_fields__"):
            return {k: getattr(obj, k) for k in obj.__dataclass_fields__}
        return obj

    return EnvironmentalContextSchema(
        waves=WaveContextSchema(**to_dict(context.waves)) if context.waves else None,
        sst=SeaSurfaceTempSchema(**to_dict(context.sst)) if context.sst else None,
        ocean_color=OceanColorSchema(**to_dict(context.ocean_color)) if context.ocean_color else None,
        hab=HABSchema(**to_dict(context.hab)) if context.hab else None,
        air_quality=AirQualitySchema(**to_dict(context.air_quality)) if context.air_quality else None,
        smoke=SmokeSchema(**to_dict(context.smoke)) if context.smoke else None,
        vegetation=VegetationSchema(**to_dict(context.vegetation)) if context.vegetation else None,
        snow=SnowCoverSchema(**to_dict(context.snow)) if context.snow else None,
        drought=DroughtSchema(**to_dict(context.drought)) if context.drought else None,
        coastal_erosion=CoastalErosionSchema(**to_dict(context.coastal_erosion)) if context.coastal_erosion else None,
        planets=PlanetarySchema(**to_dict(context.planets)) if context.planets else None,
        meteor_shower=MeteorShowerSchema(**to_dict(context.meteor_shower)) if context.meteor_shower else None,
    )
