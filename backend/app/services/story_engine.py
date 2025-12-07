"""Story engine for generating daily Ipswich story chapters.

This module provides a pluggable interface for story generation.
The default implementation uses templates enhanced with deep Ipswich knowledge.
When an Anthropic API key is configured, it uses Claude for literary story generation
in the tradition of classic New England nature writing.
"""

import random
from datetime import date
from typing import Optional, Protocol

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.story import StoryChapter
from app.schemas.story import StoryContext, NewsContext
from app.services.ipswich_knowledge import (
    NEIGHBORHOODS,
    NATURAL_FEATURES,
    HISTORICAL_FACTS,
    get_seasonal_wildlife,
    get_seasonal_character,
)


class StoryGenerator(Protocol):
    """Protocol for story generation implementations."""

    async def generate(self, context: StoryContext) -> tuple[str, str]:
        """Generate a story chapter.

        Args:
            context: The complete story context including weather, tides,
                    season, and news items.

        Returns:
            A tuple of (title, body) for the story chapter.
        """
        ...


class TemplateStoryGenerator:
    """Story generator using templates enhanced with deep Ipswich knowledge.

    This generator produces contemplative, sensory-rich narratives grounded
    in actual Ipswich geography, history, and ecology. The style draws from
    the tradition of New England nature writing.
    """

    # Openings grounded in specific Ipswich locations and seasonal character
    SEASONAL_OPENINGS = {
        "Winter": [
            "The cold settled over the Great Marsh this morning, "
            "turning the spartina to silver and the tidal creeks to dark mirrors beneath a skin of ice.",
            "Frost etched patterns on the diamond-paned windows along High Street, "
            "those First Period houses holding their silence as they have for three centuries.",
            "Winter held Ipswich in its quiet grip. Along the Riverwalk, "
            "the willows stood bare, and the Ipswich River ran dark and slow toward the sea.",
            "A pewter sky hung over Castle Hill this morning, the Great House standing "
            "white against the gray, the Grand Allee a sweep of dormant grass descending to the frozen marsh.",
            "The bare branches of the elms at Lord Square traced their patient calligraphy "
            "against skies the color of old pewter.",
        ],
        "Spring": [
            "The first warmth crept through Ipswich, and at the Choate Bridge—that twin-arched "
            "stone passage built in 1764—the river ran high with snowmelt and the promise of alewives.",
            "Mud season arrived with its particular poetry. Along Argilla Road, "
            "the fields softened, and in the marshes, the first green shoots of spartina "
            "pushed through the winter brown.",
            "The marsh began its slow awakening. From Jeffrey's Neck to Great Neck, "
            "red-winged blackbirds staked their territories, their calls carrying across the flats.",
            "Spring rain pattered on the clapboards of the old houses along Turkey Shore Road, "
            "those weathered sentinels that have watched generations pass.",
            "At Appleton Farms, the oldest continuously operating farm in America, "
            "the pastures greened and the cattle moved slowly through morning mist.",
        ],
        "Summer": [
            "The sun hung generous over Crane Beach, blessing the dunes with golden light. "
            "The barrier beach stretched for miles, its white sand and cold Atlantic waters "
            "drawing thousands to this preserved shore.",
            "Heat shimmered above the pavement on Market Street, and down at the town landing, "
            "kayakers launched into the tidal river, bound for the maze of marsh creeks.",
            "Long summer light stretched across the tidal flats of Plum Island Sound, "
            "where the Parker, Rowley, and Ipswich Rivers give their waters to the sea.",
            "The afternoon sea breeze came in from Ipswich Bay, carrying the salt scent "
            "of the Great Marsh—that vast expanse of spartina and tidal creek that stretches "
            "from here to Gloucester.",
            "At Castle Hill, picnickers spread blankets on the lawn for the evening concert, "
            "the Stuart-style Great House rising behind them, a monument to a Chicago fortune "
            "spent in love of this coast.",
        ],
        "Autumn": [
            "The maples blazed their brief glory along County Road, and in Willowdale State Forest, "
            "the hardwoods burned crimson and gold against the dark evergreens.",
            "Autumn came to Ipswich carrying the scent of fallen leaves and wood smoke. "
            "Along High Street, the First Period houses seemed to settle deeper into history.",
            "The harvest moon rose over the Great Marsh, painting the spartina silver, "
            "and at Appleton Farms, the last hay was baled and stored.",
            "October wrapped the town in its familiar melancholy. The summer people had gone; "
            "the beaches were empty; Ipswich belonged again to those who stay.",
            "In Linebrook, the orchards bent with fruit, and the sweet smell of cider "
            "drifted across the farmland that has fed this town for centuries.",
        ],
    }

    # Weather fragments with New England literary sensibility
    WEATHER_FRAGMENTS = {
        "Clear": [
            "Under a sky of extraordinary clarity, the town went about its rhythms, "
            "each familiar errand touched by uncommon light.",
            "The air held that particular New England clarity that makes distances seem "
            "negotiable and time less urgent.",
        ],
        "Clouds": [
            "Clouds gathered like thoughts above the rooftops, promising nothing, "
            "withholding nothing.",
            "A canopy of gray settled over the town, softening the edges of things, "
            "inviting contemplation.",
        ],
        "Rain": [
            "The rain fell steady, drumming its ancient rhythm on the marshes, "
            "filling the creeks, darkening the old clapboards.",
            "Rain traced its patient calligraphy on the windows of the First Church, "
            "that white-spired sentinel watching over the green.",
        ],
        "Snow": [
            "Snow transformed familiar streets into something from a story older than memory, "
            "the town hushed beneath its white quilt.",
            "The snow fell thick over Ipswich, softening the rooflines of the ancient houses, "
            "filling the cart paths of old.",
        ],
        "Fog": [
            "Fog drifted in from Ipswich Bay, wrapping the town in the sea's own mystery, "
            "muffling sound, dissolving distances.",
            "The morning fog rose from the river like departed spirits, "
            "and the town emerged slowly, piece by piece, from the gray.",
        ],
    }

    # Tide fragments with ecological awareness
    TIDE_FRAGMENTS = {
        "high": [
            "At high tide, the marsh became a mirror reflecting sky, "
            "the land and water indistinguishable at their margins.",
            "The tide stood full in the creeks, and the boats at the town landing "
            "rode high on their painters, patient as the herons.",
        ],
        "low": [
            "The low tide revealed the marsh's secret geography—mudflats, channels, "
            "the patient architecture of fiddler crab burrows.",
            "With the tide out, clammers waded the flats off Jeffrey's Neck, "
            "raking the mud as generations have, harvesting the marsh's quiet bounty.",
        ],
        "rising": [
            "The tide crept in through the maze of creeks, filling channels, "
            "lifting eelgrass, returning the marsh to the sea's dominion.",
            "As the tide rose, the great blue herons retreated to higher ground, "
            "their patience infinite but their limits known.",
        ],
        "falling": [
            "As the tide ebbed, the marsh revealed itself—mudflats gleaming, "
            "creeks narrowing, the land asserting its temporary claim.",
            "The falling tide drew the water down the creeks toward the sound, "
            "and shorebirds arrived to probe the exposed flats.",
        ],
    }

    # Middle sections connecting to Ipswich history and character
    MIDDLE_SECTIONS = [
        "Near the Choate Bridge, where the oldest stone arches in America have carried "
        "travelers across the Ipswich River since 1764, history felt close enough to touch.",
        "Along the Riverwalk, where willows dip their branches toward the tidal estuary, "
        "the boundary between then and now seemed thin as morning mist.",
        "Somewhere on Turkey Shore Road, in one of those weathered houses that have stood "
        "since before the Revolution, someone was tending the ordinary work of living.",
        "The old houses kept their counsel, as they always had. These First Period homes, "
        "with their massive chimneys and diamond-paned windows, hold stories that outlast "
        "any single telling.",
        "In the village, life continued its familiar patterns—patterns worn deep "
        "by four centuries of occupation, as grooved as the cartwheels that once "
        "rolled over the Choate Bridge.",
        "At Heard's Village, where the mill workers once lived in the era of Ipswich lace, "
        "the brick buildings kept their own memories of looms and labor.",
    ]

    # Endings with the contemplative quality of New England nature writing
    ENDINGS = [
        "And so the day turned toward evening, the light slanting low across the marsh, "
        "the town settling into the rhythms that have sustained it for nearly four hundred years.",
        "Tomorrow would come as it always had, carrying its own weather and tides, "
        "its own small dramas and quiet continuities.",
        "The town rested, its story far from finished. The river flowed on toward the sea, "
        "as it had when the Agawam people walked these banks, as it would long after.",
        "In the gathering dark, lights came on in kitchen windows—small beacons of ordinary life "
        "in houses that have sheltered such lights for generations.",
        "Night came to Ipswich as it comes to all New England towns: slowly in summer, "
        "swiftly in winter, but always with that particular quality of ending that is also beginning.",
    ]

    # News integration with literary sensibility
    NEWS_TEMPLATES = [
        "The town turned its attention to {topic}—the daily news woven into the larger fabric "
        "of coastal life, another thread in the ongoing story.",
        "Word traveled through the village of {topic}, carried from porch to porch, "
        "shop to shop, in the unhurried way of small towns.",
        "Among the morning's concerns: {topic}. Such are the matters that occupy a town "
        "between the larger rhythms of tide and season.",
        "The community took note: {topic}. In Ipswich, news has always moved at the pace "
        "of people meeting on sidewalks, pausing to talk.",
    ]

    async def generate(self, context: StoryContext) -> tuple[str, str]:
        """Generate a story using templates and deep Ipswich knowledge."""
        parts = []
        season = context.season.season

        # Opening grounded in season and place
        season_openings = self.SEASONAL_OPENINGS.get(
            season, self.SEASONAL_OPENINGS["Summer"]
        )
        parts.append(random.choice(season_openings))

        # Weather influence
        weather_key = self._get_weather_key(context.weather.condition)
        weather_fragments = self.WEATHER_FRAGMENTS.get(weather_key, [])
        if weather_fragments:
            parts.append(random.choice(weather_fragments))

        # Tide state with ecological awareness
        tide_fragments = self.TIDE_FRAGMENTS.get(context.tide.state, [])
        if tide_fragments:
            parts.append(random.choice(tide_fragments))

        # Add seasonal wildlife observation
        wildlife = get_seasonal_wildlife(season)
        if wildlife:
            parts.append(random.choice(wildlife))

        # Middle section connecting to history
        parts.append(random.choice(self.MIDDLE_SECTIONS))

        # Weave in news items if present
        if context.news_items:
            news_section = self._weave_news(context.news_items)
            parts.append(news_section)

        # Contemplative ending
        parts.append(random.choice(self.ENDINGS))

        body = "\n\n".join(parts)
        title = self._generate_title(context)

        return title, body

    def _get_weather_key(self, condition: Optional[str]) -> str:
        """Map weather condition to a template key."""
        if not condition:
            return "Clear"

        condition_lower = condition.lower()
        mappings = {
            "clear": "Clear",
            "sunny": "Clear",
            "clouds": "Clouds",
            "overcast": "Clouds",
            "partly": "Clouds",
            "rain": "Rain",
            "drizzle": "Rain",
            "shower": "Rain",
            "snow": "Snow",
            "flurr": "Snow",
            "thunderstorm": "Rain",
            "fog": "Fog",
            "mist": "Fog",
            "haze": "Fog",
        }

        for key, value in mappings.items():
            if key in condition_lower:
                return value

        return "Clear"

    def _weave_news(self, news_items: list[NewsContext]) -> str:
        """Weave news items into a narrative fragment with literary grace."""
        if not news_items:
            return ""

        fragments = []

        for i, news in enumerate(news_items[:2]):  # Limit to 2 news items
            headline = news.headline.rstrip(".")

            if i == 0:
                template = random.choice(self.NEWS_TEMPLATES)
                fragments.append(template.format(topic=headline.lower()))
            else:
                secondary = [
                    f"There was also talk of {headline.lower()}—another strand in the day's weaving.",
                    f"And {headline.lower()}, a note in the ongoing conversation of community.",
                ]
                fragments.append(random.choice(secondary))

        return " ".join(fragments)

    def _generate_title(self, context: StoryContext) -> str:
        """Generate a title in keeping with the literary tone."""
        # Sometimes reference news
        if context.news_items and random.random() > 0.6:
            first_news = context.news_items[0]
            words = first_news.headline.split()[:5]
            if len(words) >= 3:
                return " ".join(words).rstrip(".,")

        # Ipswich-specific titles
        location_titles = [
            "From Castle Hill",
            "The Great Marsh at {tide}",
            "Along the Riverwalk",
            "High Street in {season}",
            "Crane Beach",
            "Where River Meets Sea",
            "Appleton Farms",
            "The Choate Bridge",
        ]

        seasonal_titles = [
            f"A {context.season.day_of_week} in {context.season.month_name}",
            f"{context.season.season} Light on the Marsh",
            f"{context.season.month_name} Morning",
            f"Under {context.season.season} Skies",
            f"The {context.tide.state.title()} Tide",
        ]

        all_titles = location_titles + seasonal_titles
        title = random.choice(all_titles)

        # Replace placeholders
        title = title.format(
            tide=context.tide.state,
            season=context.season.season
        )

        return title


class StoryEngine:
    """Main story engine that coordinates story generation and persistence."""

    def __init__(
        self,
        db: AsyncSession,
        generator: Optional[StoryGenerator] = None,
    ):
        """Initialize the story engine.

        Args:
            db: Async database session
            generator: Optional custom story generator. If not provided,
                      uses TemplateStoryGenerator.
        """
        self.db = db
        self.generator = generator or TemplateStoryGenerator()

    async def generate_story_for_date(
        self,
        context: StoryContext,
        target_date: date,
        force_regenerate: bool = False,
    ) -> StoryChapter:
        """Generate and store a story chapter for a specific date.

        Args:
            context: The complete story context
            target_date: The date for this chapter
            force_regenerate: If True, regenerate even if chapter exists

        Returns:
            The created or updated StoryChapter
        """
        # Check for existing chapter
        existing = await self._get_existing_chapter(target_date)
        if existing and not force_regenerate:
            return existing

        # Fetch recent chapters for anti-repetition
        recent_chapters = await self._get_recent_chapters(limit=5)

        # Generate the story (pass recent chapters if generator supports it)
        if hasattr(self.generator, 'generate') and 'recent_chapters' in str(self.generator.generate.__code__.co_varnames):
            title, body = await self.generator.generate(context, recent_chapters=recent_chapters)
        else:
            title, body = await self.generator.generate(context)

        # Create weather summary
        weather_summary = context.weather.summary

        # Get news item IDs
        used_news_item_ids = (
            [n.id for n in context.news_items] if context.news_items else None
        )

        if existing and force_regenerate:
            # Update existing chapter
            existing.title = title
            existing.body = body
            existing.weather_summary = weather_summary
            existing.tide_state = context.tide.state
            existing.season = context.season.season
            existing.month_name = context.season.month_name
            existing.day_of_week = context.season.day_of_week
            existing.used_news_item_ids = used_news_item_ids
            existing.generation_context = context.model_dump(mode="json")
            await self.db.flush()
            return existing

        # Create new chapter
        chapter = StoryChapter(
            chapter_date=target_date,
            title=title,
            body=body,
            weather_summary=weather_summary,
            tide_state=context.tide.state,
            season=context.season.season,
            month_name=context.season.month_name,
            day_of_week=context.season.day_of_week,
            used_news_item_ids=used_news_item_ids,
            generation_context=context.model_dump(mode="json"),
        )

        self.db.add(chapter)
        await self.db.flush()
        return chapter

    async def _get_existing_chapter(
        self, target_date: date
    ) -> Optional[StoryChapter]:
        """Check if a chapter already exists for this date."""
        result = await self.db.execute(
            select(StoryChapter).where(StoryChapter.chapter_date == target_date)
        )
        return result.scalar_one_or_none()

    async def _get_recent_chapters(self, limit: int = 5) -> list[StoryChapter]:
        """Get recent chapters for anti-repetition context."""
        result = await self.db.execute(
            select(StoryChapter)
            .order_by(desc(StoryChapter.chapter_date))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_chapter_by_date(
        self, target_date: date
    ) -> Optional[StoryChapter]:
        """Get a chapter by date."""
        return await self._get_existing_chapter(target_date)

    async def get_latest_chapter(self) -> Optional[StoryChapter]:
        """Get the most recent chapter."""
        result = await self.db.execute(
            select(StoryChapter).order_by(desc(StoryChapter.chapter_date)).limit(1)
        )
        return result.scalar_one_or_none()
