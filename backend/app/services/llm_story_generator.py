"""
LLM-based story generator for Ipswich Story Weaver.

This generator uses Claude to produce contemplative, literary stories
in the tradition of classic New England nature writing.
"""

import logging
import re
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
from app.services.environmental.aggregator import (
    gather_environmental_context,
    format_environmental_context,
)

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
    opening_lines: str  # First 2-3 sentences
    key_phrases: List[str]  # Distinctive phrases to avoid


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
    banned_phrases: List[str] = None  # Explicit phrases to never use


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

CRITICAL - AVOID REPETITION (THIS IS EXTREMELY IMPORTANT):
- You will be given a list of BANNED PHRASES from recent stories. You MUST NOT use any of these phrases or close variations of them. This is a hard rule.
- Each day's story must feel completely fresh and distinct from previous days
- Vary your anchor locations: if yesterday featured High Street, today choose a different place (the Riverwalk, Crane Beach, Appleton Farms, Castle Hill, the Great Marsh, Willowdale, Town Hill, etc.)
- Vary your opening imagery and metaphors completely - no similar constructions to recent stories
- Vary the natural elements you emphasize (birds, trees, light, water, wind, etc.)
- If recent stories mentioned cardinals, DO NOT mention cardinals. If they mentioned frost patterns, DO NOT mention frost patterns. Find completely different imagery.

CRITICAL - VARY YOUR OPENING LINES:
Never start consecutive stories with similar patterns. Avoid these common traps:
- Starting with "The cold..." or any weather observation as the first words
- Starting with "The morning..." or time-of-day references
- Starting with "Along the..." or location references
- Starting with an animal call or bird sound (especially if recent stories did)
- Starting with weather phenomena like frost, ice, or snow (especially if recent stories did)
Instead, vary your entry points: start with an action, a human figure, a historical echo, a philosophical observation, light falling on architecture, a boat on the water, a conversation overheard. Each opening should be genuinely different from the last five stories.

CRITICAL - VARY TITLE STRUCTURE (MANDATORY):
STOP using "The [Noun] of [Noun]" pattern. This pattern is BANNED. Recent titles like "The Geometry of Safety", "The Weight of Return", "The Architecture of Quiet" all use this same tired structure.

You MUST use a completely different title structure. Choose from:
- Two-word evocative: "Cold Comfort", "December Light", "Low Tide", "Salt Wind"
- Gerund phrases: "Walking Home", "Crossing Over", "Waiting for Snow"
- Prepositional: "Before Dawn", "After the Storm", "Along the River"
- Place + Time: "Crane Beach Morning", "High Street Dusk"
- Simple nouns: "Stillness", "Homecoming", "Tidewater"
- Fragments: "What Remains", "Almost Winter", "Not Yet Spring"

DO NOT start the title with "The" followed by an abstract noun. This is a hard requirement.

CRITICAL - NO PERSONAL NAMES (ABSOLUTE RULE):
NEVER use any person's name from news stories. This includes:
- First names, last names, or full names
- Titles with names (Rev. John Smith, Dr. Jane Doe, Officer Mike Brown)
- ANY identifying name whatsoever

Instead, ALWAYS use generic role descriptions:
- "a longtime educator" not "John Smith"
- "a town official" not "Mary Jones"
- "the minister" or "the pastor" not "Rev. Adam Randazzo"
- "a local business owner" not "Sarah Thompson"
- "the fire chief" not "Chief Williams"

This is a HARD RULE with zero exceptions. Scan your output before finishing - if ANY proper name appears that came from a news story, you must remove it and replace with a role description."""


# =============================================================================
# USER PROMPT TEMPLATE
# =============================================================================

USER_PROMPT_TEMPLATE = """Write today's chapter for Ipswich, Massachusetts.

## Today's Date
{day_of_week}, {month_name} {date}

CRITICAL DATE ACCURACY: Today is {month_name} {date}. If you mention any month in your story, it MUST be {month_name}. Never write a different month like "October" when it is actually December. You may choose not to mention the month at all, but if you do reference a month, use only the correct one: {month_name}.

## Season
{season}

## Weather
{weather_description}
{temp_info}

## Tide
{tide_state}{tide_height}

## Ocean Conditions
{ocean_conditions}

## Air Quality & Atmosphere
{atmosphere_conditions}

## Land & Vegetation
{land_conditions}

## Tonight's Sky
{astronomy_conditions}

## Local News to Weave In
{news_section}

## Ipswich Knowledge (Use as factual substrate)
{knowledge_context}

## Recent Stories (AVOID repeating these themes, locations, and phrases)
{recent_stories}

## BANNED PHRASES (DO NOT USE these or similar variations - this is mandatory)
{banned_phrases}

## BANNED TITLE PATTERNS (DO NOT use "The [Noun] of [Noun]" structure)
Recent titles used this pattern - you must use a DIFFERENT structure:
{recent_titles}

---

Write a short chapter (2-3 paragraphs, 200-350 words total) that:
1. Opens with a grounding in the physical world - the weather, the light, the feel of the day
2. Weaves in the local news naturally, as part of the town's daily rhythm
3. Connects the present moment to the deeper patterns of place - seasonal, ecological, historical
4. Closes with a sense of continuity - the day passing into evening, the ongoing life of the town

Respond with EXACTLY this format:
TITLE: [Your original poetic title here - DO NOT use the news headline as the title. Create your own evocative 2-5 word title like "December Light" or "Salt Wind Morning"]

BODY:
[The story text, with paragraphs separated by blank lines]

IMPORTANT: The title must be YOUR OWN creative title, NOT the news headline or any part of it."""


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
        airnow_api_key: Optional[str] = None,
    ) -> Tuple[str, str]:
        """
        Generate a story chapter using the LLM.

        Args:
            story_input: All the context for today's story
            ebird_api_key: Optional eBird API key for bird sightings
            airnow_api_key: Optional EPA AirNow API key for air quality

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

        # Gather environmental context (ocean, atmosphere, land, astronomy)
        ocean_conditions = ""
        atmosphere_conditions = ""
        land_conditions = ""
        astronomy_conditions = ""

        try:
            env_context = await gather_environmental_context(
                airnow_api_key=airnow_api_key,
            )

            # Format ocean conditions
            ocean_parts = []
            if env_context.waves and env_context.waves.significant_height_ft:
                ocean_parts.append(f"- Waves: {env_context.waves.description}")
            if env_context.sst and env_context.sst.temp_fahrenheit:
                ocean_parts.append(f"- Sea temperature: {env_context.sst.description}")
            if env_context.ocean_color and env_context.ocean_color.bloom_status != "normal":
                ocean_parts.append(f"- Ocean color: {env_context.ocean_color.description}")
            if env_context.hab and env_context.hab.status != "none":
                ocean_parts.append(f"- HAB status: {env_context.hab.description}")
            ocean_conditions = "\n".join(ocean_parts) if ocean_parts else "(No ocean data available)"

            # Format atmosphere conditions
            atmo_parts = []
            if env_context.air_quality and env_context.air_quality.overall_aqi:
                atmo_parts.append(f"- Air quality: {env_context.air_quality.description}")
                if env_context.air_quality.health_message:
                    atmo_parts.append(f"  {env_context.air_quality.health_message}")
            if env_context.smoke and env_context.smoke.present:
                atmo_parts.append(f"- Smoke: {env_context.smoke.description}")
            atmosphere_conditions = "\n".join(atmo_parts) if atmo_parts else "(Air quality good)"

            # Format land conditions
            land_parts = []
            if env_context.vegetation:
                land_parts.append(f"- Vegetation: {env_context.vegetation.status} - {env_context.vegetation.seasonal_note or ''}")
            if env_context.snow and env_context.snow.coverage != "none":
                land_parts.append(f"- Snow: {env_context.snow.description}")
            if env_context.drought and env_context.drought.severity != "none":
                land_parts.append(f"- Drought: {env_context.drought.description}")
            if env_context.coastal_erosion and env_context.coastal_erosion.high_risk_areas:
                land_parts.append(f"- Coastal change: {env_context.coastal_erosion.recent_changes}")
            land_conditions = "\n".join(land_parts) if land_parts else "(Conditions normal)"

            # Format astronomy conditions
            astro_parts = []
            if env_context.planets and env_context.planets.visible_planets:
                if env_context.planets.evening_planets:
                    astro_parts.append(f"- Evening sky: {', '.join(env_context.planets.evening_planets)} visible")
                if env_context.planets.morning_planets:
                    astro_parts.append(f"- Before dawn: {', '.join(env_context.planets.morning_planets)} visible")
            if env_context.meteor_shower and env_context.meteor_shower.active_shower:
                if env_context.meteor_shower.peak_tonight:
                    astro_parts.append(f"- **{env_context.meteor_shower.active_shower} meteor shower peaks tonight!** ({env_context.meteor_shower.expected_rate})")
                else:
                    astro_parts.append(f"- {env_context.meteor_shower.active_shower} meteor shower active ({env_context.meteor_shower.expected_rate})")
            astronomy_conditions = "\n".join(astro_parts) if astro_parts else "(Standard night sky)"

        except Exception as e:
            logger.warning(f"Failed to gather environmental context: {e}")
            ocean_conditions = "(Data unavailable)"
            atmosphere_conditions = "(Data unavailable)"
            land_conditions = "(Data unavailable)"
            astronomy_conditions = "(Data unavailable)"

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
                recent_lines.append(f"- **{story.date}** \"{story.title}\": {story.opening_lines}")
            recent_stories_section = "\n".join(recent_lines)
        else:
            recent_stories_section = "(No recent stories - this is the first chapter)"

        # Format banned phrases section
        if story_input.banned_phrases:
            banned_phrases_section = "\n".join(f"- \"{phrase}\"" for phrase in story_input.banned_phrases)
        else:
            banned_phrases_section = "(No banned phrases yet)"

        # Format recent titles section
        if story_input.recent_stories:
            recent_titles_section = "\n".join(f"- \"{story.title}\"" for story in story_input.recent_stories)
        else:
            recent_titles_section = "(No recent titles)"

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
            ocean_conditions=ocean_conditions,
            atmosphere_conditions=atmosphere_conditions,
            land_conditions=land_conditions,
            astronomy_conditions=astronomy_conditions,
            news_section=news_section,
            knowledge_context=knowledge_context,
            recent_stories=recent_stories_section,
            banned_phrases=banned_phrases_section,
            recent_titles=recent_titles_section,
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

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling LLM API: {e}")
            logger.error(f"Response body: {e.response.text}")
            raise
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling LLM API: {e}")
            raise
        except Exception as e:
            logger.error(f"Error generating story with LLM: {e}")
            raise

    def _parse_response(self, content: str) -> Tuple[str, str]:
        """Parse the LLM response into title and body."""
        logger.info(f"Parsing LLM response, first 500 chars: {content[:500]}")
        lines = content.strip().split("\n")

        title = "A Day in Ipswich"
        body_lines = []
        in_body = False

        for line in lines:
            # Handle variations: "TITLE:", "Title:", "**TITLE:**", etc.
            line_upper = line.upper().strip()
            if line_upper.startswith("TITLE:") or line_upper.startswith("**TITLE"):
                # Extract title, removing markdown and label
                title = line.split(":", 1)[-1].strip().strip("*").strip()
                logger.info(f"Parsed title: {title}")
            elif line_upper.startswith("BODY:") or line_upper.startswith("**BODY"):
                in_body = True
            elif in_body:
                body_lines.append(line)

        body = "\n".join(body_lines).strip()

        # Fallback if parsing failed
        if not body:
            # Try to use the whole content as body
            body = content.strip()
            if body.upper().startswith("TITLE:"):
                # Remove title line
                body = "\n".join(body.split("\n")[1:]).strip()

        logger.info(f"Final title: {title}, body length: {len(body)}")
        return title, body


def extract_key_phrases(text: str) -> List[str]:
    """
    Extract distinctive opening phrases and imagery from story text.
    These will be explicitly banned in future stories.
    """
    if not text:
        return []

    phrases = []

    # Get the first 2-3 sentences for opening pattern detection
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    # Extract distinctive opening patterns (first 6-8 words of each early sentence)
    for sentence in sentences[:3]:
        words = sentence.split()
        if len(words) >= 4:
            # Get opening phrase (first 4-6 words)
            opening = ' '.join(words[:min(6, len(words))])
            # Clean up and add if substantive
            opening = opening.strip('.,;:')
            if len(opening) > 15:  # Skip very short phrases
                phrases.append(opening)

    # Look for distinctive imagery patterns throughout the text
    imagery_patterns = [
        r"[A-Z][a-z]+'s?\s+(?:sharp\s+)?(?:call|cry|song)\s+\w+",  # "A cardinal's sharp call..."
        r"[Ff]rost\s+(?:etches?|traces?|paints?|covers?)\s+\w+",  # "Frost etches..."
        r"[Ii]ce\s+(?:forms?|edges?|crystals?)\s+\w+",  # "Ice forms..."
        r"[Ss]now\s+(?:falls?|blankets?|covers?|softens?)\s+\w+",  # "Snow falls..."
        r"[Ww]ind\s+(?:carries?|brings?|whispers?)\s+\w+",  # "Wind carries..."
        r"[Ll]ight\s+(?:falls?|slants?|filters?)\s+\w+",  # "Light falls..."
        r"[Ss]hadows?\s+(?:stretch|fall|lengthen)\s+\w+",  # "Shadows stretch..."
    ]

    for pattern in imagery_patterns:
        matches = re.findall(pattern, text)
        phrases.extend(matches[:2])  # Max 2 matches per pattern

    # Deduplicate while preserving order
    seen = set()
    unique_phrases = []
    for p in phrases:
        p_lower = p.lower()
        if p_lower not in seen:
            seen.add(p_lower)
            unique_phrases.append(p)

    return unique_phrases[:10]  # Max 10 phrases per story


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
                all_banned_phrases = []

                if recent_chapters:
                    for ch in recent_chapters[:5]:  # Last 5 stories
                        # Get first 2-3 sentences for opening context
                        sentences = re.split(r'(?<=[.!?])\s+', ch.body.strip()) if ch.body else []
                        opening_lines = ' '.join(sentences[:3])[:300] if sentences else ""

                        # Extract key phrases from full body
                        key_phrases = extract_key_phrases(ch.body) if ch.body else []
                        all_banned_phrases.extend(key_phrases)

                        recent_stories.append(RecentStory(
                            date=str(ch.chapter_date),
                            title=ch.title,
                            opening_lines=opening_lines,
                            key_phrases=key_phrases,
                        ))

                # Deduplicate banned phrases
                unique_banned = list(dict.fromkeys(all_banned_phrases))

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
                    banned_phrases=unique_banned,
                )

                # Get API keys from environment
                ebird_api_key = os.environ.get("EBIRD_API_KEY")
                airnow_api_key = os.environ.get("AIRNOW_API_KEY")

                title, body = await self.llm_generator.generate(
                    story_input,
                    ebird_api_key=ebird_api_key,
                    airnow_api_key=airnow_api_key,
                )
                logger.info("Story generated successfully with LLM")
                return title, body

            except Exception as e:
                logger.error(f"LLM generation failed, using fallback: {e}", exc_info=True)

        # Use fallback generator
        logger.info("Using template-based fallback generator")
        return await self.fallback_generator.generate(context)
