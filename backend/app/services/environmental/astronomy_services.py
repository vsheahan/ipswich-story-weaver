"""Astronomy services for planet visibility and meteor showers.

This module provides:
- MeteorShowerService: Static calendar of major meteor showers with peak dates
- PlanetaryService: Calculate rise/set times for visible planets
"""

import logging
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# Ipswich, MA coordinates for astronomical calculations
IPSWICH_LAT = 42.6792
IPSWICH_LON = -70.8417


@dataclass
class MeteorShowerInfo:
    """Information about a meteor shower."""
    name: str
    peak_start: date
    peak_end: date
    expected_rate: str  # e.g., "10-15 per hour"
    radiant: str  # constellation
    moon_interference: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class MeteorShowerContext:
    """Current meteor shower context for story generation."""
    active_shower: Optional[str] = None
    peak_tonight: bool = False
    expected_rate: Optional[str] = None
    radiant: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class PlanetInfo:
    """Information about a planet's visibility."""
    name: str
    rise_time: Optional[datetime] = None
    set_time: Optional[datetime] = None
    is_visible_tonight: bool = False
    best_viewing: Optional[str] = None  # "evening", "morning", "all night"
    constellation: Optional[str] = None


@dataclass
class PlanetaryContext:
    """Current planetary context for story generation."""
    visible_planets: list[str]
    evening_planets: list[str]
    morning_planets: list[str]
    notable_events: Optional[str] = None


# Major meteor showers with 2024-2026 peak dates
# Peak dates shift slightly year to year but these are typical windows
METEOR_SHOWERS_2025 = [
    MeteorShowerInfo(
        name="Quadrantids",
        peak_start=date(2025, 1, 3),
        peak_end=date(2025, 1, 4),
        expected_rate="60-120 per hour",
        radiant="Boötes",
        notes="Brief but intense peak; best after midnight"
    ),
    MeteorShowerInfo(
        name="Lyrids",
        peak_start=date(2025, 4, 21),
        peak_end=date(2025, 4, 23),
        expected_rate="10-20 per hour",
        radiant="Lyra",
        notes="Spring shower; occasional fireballs"
    ),
    MeteorShowerInfo(
        name="Eta Aquariids",
        peak_start=date(2025, 5, 5),
        peak_end=date(2025, 5, 7),
        expected_rate="20-40 per hour",
        radiant="Aquarius",
        notes="Halley's Comet debris; best before dawn"
    ),
    MeteorShowerInfo(
        name="Delta Aquariids",
        peak_start=date(2025, 7, 28),
        peak_end=date(2025, 7, 30),
        expected_rate="15-20 per hour",
        radiant="Aquarius",
        notes="Warm summer nights; overlaps with Perseids buildup"
    ),
    MeteorShowerInfo(
        name="Perseids",
        peak_start=date(2025, 8, 11),
        peak_end=date(2025, 8, 13),
        expected_rate="50-100 per hour",
        radiant="Perseus",
        notes="Most popular shower; reliable and warm viewing conditions"
    ),
    MeteorShowerInfo(
        name="Draconids",
        peak_start=date(2025, 10, 8),
        peak_end=date(2025, 10, 9),
        expected_rate="5-10 per hour",
        radiant="Draco",
        notes="Best in evening; occasional outbursts"
    ),
    MeteorShowerInfo(
        name="Orionids",
        peak_start=date(2025, 10, 20),
        peak_end=date(2025, 10, 22),
        expected_rate="15-20 per hour",
        radiant="Orion",
        notes="Halley's Comet debris; fast meteors"
    ),
    MeteorShowerInfo(
        name="Taurids",
        peak_start=date(2025, 11, 4),
        peak_end=date(2025, 11, 12),
        expected_rate="5-10 per hour",
        radiant="Taurus",
        notes="Slow, bright fireballs; long active period"
    ),
    MeteorShowerInfo(
        name="Leonids",
        peak_start=date(2025, 11, 17),
        peak_end=date(2025, 11, 18),
        expected_rate="10-15 per hour",
        radiant="Leo",
        notes="Historic storm shower; occasional outbursts"
    ),
    MeteorShowerInfo(
        name="Geminids",
        peak_start=date(2025, 12, 13),
        peak_end=date(2025, 12, 14),
        expected_rate="120-150 per hour",
        radiant="Gemini",
        notes="Year's best shower; bright, colorful meteors"
    ),
    MeteorShowerInfo(
        name="Ursids",
        peak_start=date(2025, 12, 21),
        peak_end=date(2025, 12, 23),
        expected_rate="5-10 per hour",
        radiant="Ursa Minor",
        notes="Solstice shower; underobserved"
    ),
]

# Extended window for active shower detection (days before/after peak)
SHOWER_ACTIVITY_WINDOW = 3


class MeteorShowerService:
    """Service for meteor shower information."""

    def __init__(self):
        """Initialize with static shower calendar."""
        self.showers = METEOR_SHOWERS_2025

    def get_current_shower(self, target_date: Optional[date] = None) -> MeteorShowerContext:
        """Get meteor shower information for a given date.

        Args:
            target_date: Date to check. Defaults to today.

        Returns:
            MeteorShowerContext with any active shower info
        """
        if target_date is None:
            target_date = date.today()

        for shower in self.showers:
            # Check if we're within the extended activity window
            window_start = shower.peak_start - timedelta(days=SHOWER_ACTIVITY_WINDOW)
            window_end = shower.peak_end + timedelta(days=SHOWER_ACTIVITY_WINDOW)

            if window_start <= target_date <= window_end:
                # Check if this is peak night
                is_peak = shower.peak_start <= target_date <= shower.peak_end

                return MeteorShowerContext(
                    active_shower=shower.name,
                    peak_tonight=is_peak,
                    expected_rate=shower.expected_rate if is_peak else f"building to {shower.expected_rate}",
                    radiant=shower.radiant,
                    notes=shower.notes,
                )

        return MeteorShowerContext()

    def format_for_story(self, context: MeteorShowerContext) -> str:
        """Format meteor shower info for story context."""
        if not context.active_shower:
            return ""

        lines = ["## Meteor Shower"]
        if context.peak_tonight:
            lines.append(f"- **{context.active_shower} peak tonight!** ({context.expected_rate})")
        else:
            lines.append(f"- {context.active_shower} shower active ({context.expected_rate})")

        if context.radiant:
            lines.append(f"- Look toward {context.radiant}")

        if context.notes:
            lines.append(f"- {context.notes}")

        return "\n".join(lines)


class PlanetaryService:
    """Service for planetary visibility calculations.

    Uses simplified calculations based on typical visibility patterns.
    For production, consider using astronomy-engine package for precise calculations.
    """

    # Typical visibility patterns for 2025 (simplified)
    # In reality, this would use ephemeris calculations
    PLANET_VISIBILITY_2025 = {
        "Mercury": {
            "evening": [(1, 15, 2, 15), (5, 1, 5, 31), (8, 20, 9, 20), (12, 10, 12, 31)],
            "morning": [(3, 1, 3, 31), (7, 1, 7, 20), (10, 15, 11, 15)],
        },
        "Venus": {
            "evening": [(1, 1, 3, 20)],
            "morning": [(4, 15, 12, 31)],
        },
        "Mars": {
            "evening": [(1, 1, 6, 30)],
            "morning": [(9, 1, 12, 31)],
        },
        "Jupiter": {
            "evening": [(1, 1, 5, 15)],
            "all_night": [(10, 1, 12, 31)],
            "morning": [(7, 1, 9, 30)],
        },
        "Saturn": {
            "evening": [(1, 1, 2, 28)],
            "all_night": [(9, 1, 10, 31)],
            "morning": [(6, 1, 8, 31)],
        },
    }

    def _is_in_window(self, target_date: date, windows: list[tuple]) -> bool:
        """Check if date falls within any visibility window."""
        month = target_date.month
        day = target_date.day

        for start_month, start_day, end_month, end_day in windows:
            # Handle year wrap (e.g., Dec to Jan)
            if start_month <= end_month:
                if start_month <= month <= end_month:
                    if month == start_month and day < start_day:
                        continue
                    if month == end_month and day > end_day:
                        continue
                    return True
            else:
                # Window wraps around year end
                if month >= start_month or month <= end_month:
                    if month == start_month and day < start_day:
                        continue
                    if month == end_month and day > end_day:
                        continue
                    return True

        return False

    def get_visible_planets(self, target_date: Optional[date] = None) -> PlanetaryContext:
        """Get planetary visibility for a given date.

        Args:
            target_date: Date to check. Defaults to today.

        Returns:
            PlanetaryContext with visible planet information
        """
        if target_date is None:
            target_date = date.today()

        visible = []
        evening = []
        morning = []

        for planet, windows in self.PLANET_VISIBILITY_2025.items():
            # Check evening visibility
            if "evening" in windows and self._is_in_window(target_date, windows["evening"]):
                visible.append(planet)
                evening.append(planet)
            # Check morning visibility
            elif "morning" in windows and self._is_in_window(target_date, windows["morning"]):
                visible.append(planet)
                morning.append(planet)
            # Check all-night visibility
            elif "all_night" in windows and self._is_in_window(target_date, windows["all_night"]):
                visible.append(planet)
                evening.append(planet)
                morning.append(planet)

        # Generate notable events based on conjunctions or special alignments
        # This is simplified; real implementation would check ephemeris
        notable = None
        if len(evening) >= 3:
            notable = f"Planet parade: {', '.join(evening)} visible in evening sky"
        elif len(morning) >= 3:
            notable = f"Planet parade: {', '.join(morning)} visible before dawn"

        return PlanetaryContext(
            visible_planets=visible,
            evening_planets=evening,
            morning_planets=morning,
            notable_events=notable,
        )

    def format_for_story(self, context: PlanetaryContext) -> str:
        """Format planetary info for story context."""
        if not context.visible_planets:
            return ""

        lines = ["## Visible Planets Tonight"]

        if context.evening_planets:
            planets = ", ".join(context.evening_planets)
            lines.append(f"- Evening sky: {planets}")

        if context.morning_planets:
            planets = ", ".join(context.morning_planets)
            lines.append(f"- Before dawn: {planets}")

        if context.notable_events:
            lines.append(f"- {context.notable_events}")

        return "\n".join(lines)


# Try to import astronomy-engine for precise calculations
try:
    import astronomy

    class PrecisePlanetaryService(PlanetaryService):
        """Enhanced planetary service using astronomy-engine for precise calculations."""

        PLANETS = [
            ("Mercury", astronomy.Body.Mercury),
            ("Venus", astronomy.Body.Venus),
            ("Mars", astronomy.Body.Mars),
            ("Jupiter", astronomy.Body.Jupiter),
            ("Saturn", astronomy.Body.Saturn),
        ]

        def get_visible_planets(self, target_date: Optional[date] = None) -> PlanetaryContext:
            """Get planetary visibility using precise ephemeris calculations."""
            if target_date is None:
                target_date = date.today()

            # Create observer location
            observer = astronomy.Observer(IPSWICH_LAT, IPSWICH_LON, 0)

            # Get times for calculations
            dt = datetime.combine(target_date, datetime.min.time())
            time = astronomy.Time.Make(dt.year, dt.month, dt.day, 20, 0, 0)  # 8 PM local

            visible = []
            evening = []
            morning = []

            for name, body in self.PLANETS:
                try:
                    # Get rise and set times
                    rise = astronomy.SearchRiseSet(body, observer, astronomy.Direction.Rise, time, 1)
                    set_time = astronomy.SearchRiseSet(body, observer, astronomy.Direction.Set, time, 1)

                    # Check if planet is above horizon in evening (after sunset)
                    sunset = astronomy.SearchRiseSet(
                        astronomy.Body.Sun, observer, astronomy.Direction.Set, time, 1
                    )

                    if rise and set_time:
                        # Determine viewing window
                        if sunset and set_time.ut > sunset.ut:
                            visible.append(name)
                            evening.append(name)

                        # Check morning visibility
                        sunrise = astronomy.SearchRiseSet(
                            astronomy.Body.Sun, observer, astronomy.Direction.Rise, time, 1
                        )
                        if sunrise and rise.ut < sunrise.ut:
                            if name not in visible:
                                visible.append(name)
                            morning.append(name)

                except Exception as e:
                    logger.debug(f"Could not calculate position for {name}: {e}")
                    continue

            notable = None
            if len(evening) >= 3:
                notable = f"Planet parade: {', '.join(evening)} visible in evening sky"

            return PlanetaryContext(
                visible_planets=visible,
                evening_planets=evening,
                morning_planets=morning,
                notable_events=notable,
            )

    # Use precise service if astronomy-engine is available
    _PlanetaryServiceClass = PrecisePlanetaryService
    logger.info("Using astronomy-engine for precise planetary calculations")

except ImportError:
    # Fall back to simplified calculations
    _PlanetaryServiceClass = PlanetaryService
    logger.info("astronomy-engine not available; using simplified planetary calculations")


def get_planetary_service() -> PlanetaryService:
    """Get the best available planetary service."""
    return _PlanetaryServiceClass()
