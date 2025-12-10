"""Environmental data sources for story generation.

This package provides services for fetching environmental data from various
sources including NOAA, EPA, NASA, and astronomical calculations.
"""

from app.services.environmental.aggregator import gather_environmental_context
from app.services.environmental.base import (
    ERDDAPClient,
    IPSWICH_LAT,
    IPSWICH_LON,
    IPSWICH_BBOX,
)

__all__ = [
    "gather_environmental_context",
    "ERDDAPClient",
    "IPSWICH_LAT",
    "IPSWICH_LON",
    "IPSWICH_BBOX",
]
