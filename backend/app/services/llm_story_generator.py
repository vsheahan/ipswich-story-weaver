"""
LLM-based story generator for Ipswich Story Weaver.

This generator uses Claude to produce contemplative, literary stories
in the tradition of classic New England nature writing.
"""

import logging
from typing import Protocol, Tuple, List, Optional
import os
from dataclasses import dataclass

import httpx

from app.services.ipswich_knowledge import (
    build_knowledge_context,
    get_seasonal_wildlife,
    get_seasonal_character,
    NEIGHBORHOODS,
    NATURAL_FEATURES,
    HISTORICAL_FACTS,
)
from app.services.additional_sources import gather_additional_context

logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    """Simplified news item for story generation."""
    headline: str
    summary: str


@dataclass
class RecentStory:
    """Summary of a recent story for anti-repetition."""
    date: str
    title: str
    first_sentence: str


@dataclass
class StoryInput:
    """All inputs needed for story generation."""
    date: str
    day_of_week: str
    month_name: str
    season: str
    weather_condition: str
    weather_description: str
    temp_high: Optional[float]
    temp_low: Optional[float]
    tide_state: str
    tide_height: Optional[float]
    news_items: List[NewsItem]
    recent_stories: List[RecentStory] = None


# =============================================================================
# SYSTEM PROMPT - The core literary instructions
# =============================================================================

SYSTEM_PROMPT = """You are a storyteller weaving daily tales about Ipswich, Massachusetts. Your voice is inspired by the contemplative tradition of classic New England writers: Ralph Waldo Emerson, Henry David Thoreau, Sarah Orne Jewett, and Nathaniel Hawthorne.

Your narrative style:
- Contemplative and sensory-rich, grounded in natural observation
- Aware of the relationship between human community and landscape
- Gently philosophical without being preachy
- Minimalist but lyrical - every word should earn its place
- Evokes feeling through concrete detail, not abstraction
- Treats the land as a living presence, observing alongside the people

You must NEVER:
- Hallucinate locations or historical facts about Ipswich
- Place locations incorrectly (e.g., High Street is NOT near the river - it's uphill/west)
- Confuse the river (Ipswich River, runs through downtown) with the coast (Crane Beach, Great Neck)
- Use purple prose or overwrought language
- Parody or directly imitate the classic writers
- Be sentimental or saccharine
- Use clichés or generic nature writing tropes
- Include specific names of people from news stories (use descriptions like "a local resident" or "a town official" instead)
- Reference obituaries, deaths, or memorial services in the narrative
- Include any content about accidents, crimes, or tragedies involving named individuals
- Use exact numerical data in the narrative (no "35 degrees", "30 cubic feet per second", "9.2 feet")

TRANSLATE DATA INTO SENSORY EXPERIENCE:
Instead of exact numbers, convey what they FEEL like:
- Temperature: "bitter cold that stings exposed skin" not "28 degrees"
- River flow: "the river runs sluggish and low" not "30 cubic feet per second"
- Tide height: "the tide stands full in the creeks" not "9.5 feet"
- Wind: "a raw wind off the water" not "15 mph winds"
The data you're given is context for understanding conditions - transform it into embodied, sensory description that a walker would experience

CRITICAL GEOGRAPHIC ACCURACY:
- The Ipswich River flows through downtown, under the Choate Bridge
- High Street is UPHILL from downtown, away from the river - a quiet residential area
- The coast (Crane Beach, Great Neck) is separate from the river, miles away via Argilla Road
- The Great Marsh connects the river estuary to the sea
- Always respect the geographic relationships provided in the knowledge context

You write as if the land itself is observing the news alongside the people of Ipswich. Each chapter should feel like a meditation on the town's condition that day - a blending of present news with centuries of natural and historical context.

Your stories should feel like they could have been written while walking the Ipswich riverbanks, Crane Beach dunes, Appleton Farms grasslands, or Willowdale forests at dawn.

CRITICAL - AVOID REPETITION:
- Each day's story must feel fresh and distinct from previous days
- Vary your anchor locations: if yesterday featured High Street, today choose a different place (the Riverwalk, Crane Beach, Appleton Farms, Castle Hill, the Great Marsh, Willowdale, Town Hill, etc.)
- Vary your opening imagery and metaphors - never reuse phrases like "houses settling into foundations" or similar constructions from recent stories
- Vary the natural elements you emphasize (birds, trees, light, water, wind, etc.)
- You will be given summaries of recent stories to help you avoid repetition

CRITICAL - VARY YOUR OPENING LINES:
Never start consecutive stories with similar patterns. Avoid these common traps:
- Starting with "The cold..." or any weather observation as the first words
- Starting with "The morning..." or time-of-day references
- Starting with "Along the..." or location references
Instead, vary your entry points: start with an action, a sensory detail, a historical echo, a sound, a question, a person moving through space, light falling on something specific. Each opening should surprise.

CRITICAL - NO PERSONAL NAMES:
NEVER use any person's name from news stories. This is an absolute rule with no exceptions.
- Instead of "John Smith retires" write "a longtime educator retires"
- Instead of "Mary Jones announced" write "a town official announced"
- Instead of "Eric Oxford walks" write "the outgoing director walks"
- Use role descriptions: "a local fisherman", "the school principal", "a resident", "a town planner"
The stories should feel universal, not tied to specific individuals."""


# =============================================================================
# USER PROMPT TEMPLATE
# =============================================================================

USER_PROMPT_TEMPLATE = """Write today's chapter for Ipswich, Massachusetts.

## Today's Date
{day_of_week}, {month_name} {date}

## Season
{season}

## Weather
{weather_description}
{temp_info}

## Tide
{tide_state}{tide_height}

## Local News to Weave In
{news_section}

## Ipswich Knowledge (Use as factual substrate)
{knowledge_context}

## Recent Stories (AVOID repeating these themes, locations, and phrases)
{recent_stories}

---

Write a short chapter (2-3 paragraphs, 200-350 words total) that:
1. Opens with a grounding in the physical world - the weather, the light, the feel of the day
2. Weaves in the local news naturally, as part of the town's daily rhythm
3. Connects the present moment to the deeper patterns of place - seasonal, ecological, historical
4. Closes with a sense of continuity - the day passing into evening, the ongoing life of the town

Respond with:
TITLE: [A poetic but not flowery title, 3-8 words]

BODY:
[The story text, with paragraphs separated by blank lines]"""


class LLMStoryGenerator:
    """
    Story generator that uses Claude to produce literary narratives
    about Ipswich, grounded in deep knowledge of the town.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 1024,
    ):
        """
        Initialize the LLM story generator.

        Args:
            api_key: Anthropic API key
            model: Model to use (default: claude-sonnet-4-20250514)
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.api_url = "https://api.anthropic.com/v1/messages"

    async def generate(
        self,
        story_input: StoryInput,
        ebird_api_key: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Generate a story chapter using the LLM.

        Args:
            story_input: All the context for today's story
            ebird_api_key: Optional eBird API key for bird sightings

        Returns:
            Tuple of (title, body)
        """
        # Build the knowledge context for this season
        knowledge_context = build_knowledge_context(story_input.season)

        # Gather additional live data (bird sightings, river conditions, etc.)
        try:
            additional_context = await gather_additional_context(ebird_api_key)
            if additional_context:
                knowledge_context += "\n\n" + additional_context
        except Exception as e:
            logger.warning(f"Failed to gather additional context: {e}")

        # Format temperature info
        temp_info = ""
        if story_input.temp_high or story_input.temp_low:
            temps = []
            if story_input.temp_high:
                temps.append(f"High: {story_input.temp_high}°F")
            if story_input.temp_low:
                temps.append(f"Low: {story_input.temp_low}°F")
            temp_info = " / ".join(temps)

        # Format tide height
        tide_height = ""
        if story_input.tide_height:
            tide_height = f" ({story_input.tide_height} ft)"

        # Format news section
        if story_input.news_items:
            news_lines = []
            for i, item in enumerate(story_input.news_items, 1):
                news_lines.append(f"{i}. **{item.headline}**")
                if item.summary:
                    news_lines.append(f"   {item.summary[:200]}")
            news_section = "\n".join(news_lines)
        else:
            news_section = "(No local news today - focus on the natural world and seasonal rhythms)"

        # Format recent stories section
        if story_input.recent_stories:
            recent_lines = []
            for story in story_input.recent_stories:
                recent_lines.append(f"- **{story.date}** \"{story.title}\": {story.first_sentence}")
            recent_stories_section = "\n".join(recent_lines)
        else:
            recent_stories_section = "(No recent stories - this is the first chapter)"

        # Build the user prompt
        user_prompt = USER_PROMPT_TEMPLATE.format(
            day_of_week=story_input.day_of_week,
            month_name=story_input.month_name,
            date=story_input.date,
            season=story_input.season,
            weather_description=f"{story_input.weather_condition}: {story_input.weather_description}",
            temp_info=temp_info,
            tide_state=story_input.tide_state,
            tide_height=tide_height,
            news_section=news_section,
            knowledge_context=knowledge_context,
            recent_stories=recent_stories_section,
        )

        # Call the API
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "max_tokens": self.max_tokens,
                        "system": SYSTEM_PROMPT,
                        "messages": [
                            {"role": "user", "content": user_prompt}
                        ],
                    },
                )
                response.raise_for_status()
                result = response.json()

                # Extract the text content
                content = result["content"][0]["text"]

                # Parse title and body
                return self._parse_response(content)

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling LLM API: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating story with LLM: {e}")
            raise

    def _parse_response(self, content: str) -> Tuple[str, str]:
        """Parse the LLM response into title and body."""
        lines = content.strip().split("\n")

        title = "A Day in Ipswich"
        body_lines = []
        in_body = False

        for line in lines:
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
            elif line.startswith("BODY:"):
                in_body = True
            elif in_body:
                body_lines.append(line)

        body = "\n".join(body_lines).strip()

        # Fallback if parsing failed
        if not body:
            # Try to use the whole content as body
            body = content.strip()
            if body.startswith("TITLE:"):
                # Remove title line
                body = "\n".join(body.split("\n")[1:]).strip()

        return title, body


class LLMStoryGeneratorWithFallback:
    """
    Story generator that tries LLM first, falls back to template-based.

    This wrapper ensures story generation always succeeds, even if
    the LLM API is unavailable or errors occur.
    """

    def __init__(
        self,
        api_key: Optional[str],
        fallback_generator,
        model: str = "claude-sonnet-4-20250514",
    ):
        """
        Initialize with optional LLM and required fallback.

        Args:
            api_key: Anthropic API key (None to use fallback only)
            fallback_generator: Generator to use if LLM fails
            model: Model to use for LLM
        """
        self.llm_generator = None
        if api_key:
            self.llm_generator = LLMStoryGenerator(api_key=api_key, model=model)
        self.fallback_generator = fallback_generator

    async def generate(self, context, recent_chapters=None) -> Tuple[str, str]:
        """
        Generate a story, trying LLM first then falling back.

        Args:
            context: StoryContext from the context builder
            recent_chapters: List of recent StoryChapter objects for anti-repetition

        Returns:
            Tuple of (title, body)
        """
        if self.llm_generator:
            try:
                # Build recent stories list for anti-repetition
                recent_stories = []
                if recent_chapters:
                    for ch in recent_chapters[:5]:  # Last 5 stories
                        # Get first sentence of the body
                        first_sentence = ch.body.split('.')[0] + '.' if ch.body else ""
                        recent_stories.append(RecentStory(
                            date=str(ch.chapter_date),
                            title=ch.title,
                            first_sentence=first_sentence[:150],
                        ))

                # Convert context to StoryInput
                story_input = StoryInput(
                    date=str(context.season.date),
                    day_of_week=context.season.day_of_week,
                    month_name=context.season.month_name,
                    season=context.season.season,
                    weather_condition=context.weather.condition or "Overcast",
                    weather_description=context.weather.condition_description or "",
                    temp_high=context.weather.temp_high,
                    temp_low=context.weather.temp_low,
                    tide_state=context.tide.state or "mid",
                    tide_height=context.tide.height,
                    news_items=[
                        NewsItem(headline=n.headline, summary=n.summary)
                        for n in (context.news_items or [])
                    ],
                    recent_stories=recent_stories,
                )

                # Get eBird API key from environment
                ebird_api_key = os.environ.get("EBIRD_API_KEY")

                title, body = await self.llm_generator.generate(
                    story_input,
                    ebird_api_key=ebird_api_key,
                )
                logger.info("Story generated successfully with LLM")
                return title, body

            except Exception as e:
                logger.warning(f"LLM generation failed, using fallback: {e}")

        # Use fallback generator
        logger.info("Using template-based fallback generator")
        return await self.fallback_generator.generate(context)
