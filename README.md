# Ipswich Story Weaver

A web application that generates daily fictionalized stories about Ipswich, Massachusetts, weaving together weather data, tidal patterns, seasonal rhythms, and local news from [The Local News](https://thelocalnews.news/category/ipswich/) into an evolving narrative about this historic coastal town.

## Overview

The Ipswich Story Weaver is a contemplative, civic narrative installation that makes Ipswich feel like it has a living, evolving story. Each day, a new "chapter" is generated based on:

- **Local weather data** - Temperature, conditions, and atmospheric mood
- **Tidal patterns** - The rhythm of Ipswich Bay's tides
- **Seasonal context** - Time of year, day length, and seasonal character
- **Local news** - Headlines and summaries from The Local News Ipswich category
- **Deep Ipswich knowledge** - Geography, history, ecology, and wildlife patterns

**Important:** This is a read-only public application. There is no user-generated content. All public endpoints are read-only. News content is limited to headlines, short summaries, and links back to the original source.

## Narrative Style

Stories are written in a **contemplative New England literary style** inspired by:

- **Ralph Waldo Emerson** - Transcendentalist observation of nature
- **Henry David Thoreau** - Patient attention to natural detail
- **Sarah Orne Jewett** - Regional realism and community life
- **Nathaniel Hawthorne** - Historical undertones and atmosphere

The tone is:
- Sensory-rich and grounded in natural observation
- Aware of the relationship between human community and landscape
- Gently philosophical without being preachy
- Minimalist but lyrical

Each chapter reads as if the land itself is observing the news alongside the people of Ipswich—a meditation on the town's condition that day, blending present news with centuries of natural and historical context.

## Ipswich Knowledge Base

The story engine draws from a comprehensive factual knowledge base including:

### Geography
- Downtown Ipswich, the Riverwalk, High Street, Town Hill
- Great Neck, Little Neck, Jeffrey's Neck peninsulas
- Argilla Road, Essex Road corridor, Linebrook farmland
- The Ipswich River, Miles River, Parker River system

### Natural Features
- **Crane Beach** - Four miles of barrier beach with towering dunes
- **Castle Hill & The Crane Estate** - The Great House and Grand Allee
- **The Great Marsh** - One of the largest continuous salt marshes in New England
- **Appleton Farms** - One of the oldest continuously operating farms in America
- **Willowdale State Forest** - 2,000+ acres of forest and wetlands
- **Plum Island Sound** - Protected waters rich with marine life

### History
- 1633 colonial settlement by John Winthrop the Younger
- First Period houses (pre-1725) - the greatest concentration in North America
- The Choate Bridge (1764) - oldest double-arched stone bridge in America still in use
- John Wise and colonial dissent against taxation without representation
- The lace industry and mill history
- Maritime heritage, clamming, and shellfish flats
- The Crane family's preservation legacy

### Ecology
- Seasonal wildlife patterns (alewife runs, piping plovers, migratory birds)
- Salt marsh cycles and coastal ecology
- Dune systems and beach habitat
- Tidal rhythms and their influence on daily life

**Important:** The story engine never hallucinates locations or historical facts. All geographic and historical references are drawn from this verified knowledge base.

## Tech Stack

### Backend
- **Python 3.11** with **FastAPI** for the API
- **PostgreSQL** with **SQLAlchemy** (async) for data persistence
- **Alembic** for database migrations
- **httpx** for external API calls (weather, LLM)
- **BeautifulSoup** for news scraping
- **Pydantic** for data validation
- **Anthropic Claude** for LLM-powered story generation

### Frontend
- **React 18** with **TypeScript**
- **Vite** as the build tool
- **Tailwind CSS** for styling
- **React Router** for navigation

### Infrastructure
- **Docker** and **Docker Compose** for local development
- Environment-based configuration

## Project Structure

```
ipswich/
├── backend/
│   ├── app/
│   │   ├── api/v1/           # API routes (story, news, admin)
│   │   ├── core/             # Config and database
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   │   ├── ipswich_knowledge.py  # Ipswich factual knowledge base
│   │   │   ├── llm_story_generator.py  # Claude-powered story generation
│   │   │   ├── story_engine.py  # Template fallback generator
│   │   │   └── ...
│   │   └── tests/            # Unit tests
│   ├── alembic/              # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/              # API client
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom hooks
│   │   └── pages/            # Page components
│   └── package.json
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- (Optional) Python 3.11+ for local backend development
- (Optional) Node.js 18+ for local frontend development

### Quick Start with Docker

1. **Clone and configure**
   ```bash
   cd ipswich
   cp .env.example .env
   # Edit .env with your API keys (especially ANTHROPIC_API_KEY for best results)
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Run database migrations**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

4. **Refresh news (first time)**
   ```bash
   curl -X POST http://localhost:8000/api/admin/refresh-news
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Development Mode

For hot-reloading during development:

```bash
# Start with development profile
docker-compose --profile dev up -d

# Frontend will be at http://localhost:5173
# Backend will be at http://localhost:8000
```

### Local Development (without Docker)

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp ../.env.example .env
# Edit .env with your database URL and API keys

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Configuration

Environment variables (`.env`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string (async) | Required |
| `DATABASE_URL_SYNC` | PostgreSQL connection string (sync, for migrations) | Required |
| `DEBUG` | Enable debug mode | `false` |
| `WEATHER_API_KEY` | OpenWeatherMap API key | Optional |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | Optional (recommended) |
| `LLM_MODEL` | Claude model to use | `claude-sonnet-4-20250514` |
| `USE_LLM_FOR_STORIES` | Enable LLM story generation | `true` |
| `ENABLE_MANUAL_GENERATION` | Allow manual story generation | `true` |

### Claude API Setup (Recommended)

For the best literary story generation:

1. Sign up at [Anthropic Console](https://console.anthropic.com/)
2. Create an API key
3. Add `ANTHROPIC_API_KEY=your_key` to your `.env` file

Without an API key, the system uses an enhanced template-based generator that still draws from the Ipswich knowledge base.

### Weather API Setup

To get real weather data for Ipswich:

1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your API key (free tier works fine)
3. Add `WEATHER_API_KEY=your_key` to your `.env` file

Without an API key, the system uses seasonal fallback weather data.

## API Endpoints

### Stories (Read-Only)

- `GET /api/story/latest` - Get the most recent story chapter
- `GET /api/story/date/{date}` - Get story for a specific date
- `GET /api/story/archive` - Paginated list of all chapters
- `GET /api/story/context/today` - Get today's context (weather, tides, season, news)

### News (Read-Only)

- `GET /api/news/recent` - Get recent Ipswich news items

### Admin (Internal Use)

- `POST /api/admin/refresh-news` - Refresh news from The Local News
- `POST /api/story/generate-today` - Generate today's story (dev mode only)

**Note:** There are no public POST endpoints that accept arbitrary user text.

## Story Engine

The story engine uses a two-tier architecture:

### LLM Generator (Primary)

When `ANTHROPIC_API_KEY` is configured, stories are generated using Claude with:

- A detailed system prompt establishing the New England literary voice
- Deep context about Ipswich geography, history, and ecology
- Current weather, tide state, and season information
- Recent local news to weave into the narrative

The LLM is instructed to:
- Open with grounding in the physical world
- Weave news naturally into the town's daily rhythm
- Connect present moments to deeper patterns of place
- Close with a sense of continuity

### Template Generator (Fallback)

Without an API key, or if the LLM fails, the template generator produces stories using:

- Season-specific opening templates grounded in real Ipswich locations
- Weather-influenced prose fragments with literary sensibility
- Tide state descriptions with ecological awareness
- Seasonal wildlife observations from the knowledge base
- Historical connections to specific landmarks
- Contemplative endings in the New England nature writing tradition

Both generators draw from the same Ipswich knowledge base, ensuring factual accuracy regardless of the generation method.

## News Scraping

The news service scrapes headlines and summaries from [The Local News Ipswich category](https://thelocalnews.news/category/ipswich/).

### How It Works

1. The scraper fetches the category page HTML
2. Parses article listings to extract:
   - Headline
   - Summary/excerpt
   - Article URL
   - Author (if available)
   - Published date (if available)
3. Stores/updates entries in the database using article URL as unique key
4. Only stores headlines and short summaries, never full article text

### Refreshing News

News should be refreshed periodically to keep stories current:

**Manual refresh:**
```bash
curl -X POST http://localhost:8000/api/admin/refresh-news
```

**Cron job (recommended for production):**
```bash
# Add to crontab - refresh every 6 hours
0 */6 * * * curl -X POST http://localhost:8000/api/admin/refresh-news
```

## Running Tests

```bash
# Backend tests
cd backend
pytest

# With coverage
pytest --cov=app

# Frontend tests (add Jest configuration)
cd frontend
npm test
```

## Scheduled Story Generation

For production, set up daily story generation:

### Cron Job

```bash
# Refresh news and generate story at 6 AM
0 6 * * * curl -X POST http://localhost:8000/api/admin/refresh-news && \
          curl -X POST http://localhost:8000/api/story/generate-today
```

## Sample Story Output

Here's an example of the literary style produced by the story engine:

> *The cold settled over the Great Marsh this morning, turning the spartina to silver and the tidal creeks to dark mirrors beneath a skin of ice. Frost etched patterns on the diamond-paned windows along High Street, those First Period houses holding their silence as they have for three centuries.*
>
> *Under a sky of extraordinary clarity, the town went about its rhythms, each familiar errand touched by uncommon light. At high tide, the marsh became a mirror reflecting sky, the land and water indistinguishable at their margins.*
>
> *Harbor seals pup on the outer sandbars in January. Near the Choate Bridge, where the oldest stone arches in America have carried travelers across the Ipswich River since 1764, history felt close enough to touch.*
>
> *The community took note: local business receives state preservation grant. In Ipswich, news has always moved at the pace of people meeting on sidewalks, pausing to talk.*
>
> *And so the day turned toward evening, the light slanting low across the marsh, the town settling into the rhythms that have sustained it for nearly four hundred years.*

## Data Attribution

- Weather data from [OpenWeatherMap](https://openweathermap.org/)
- Tide calculations based on NOAA data and lunar cycles
- Local news from [The Local News](https://thelocalnews.news/category/ipswich/) (headlines and summaries only, with links to original articles)
- Story generation powered by [Anthropic Claude](https://www.anthropic.com/)

## License

MIT License - see LICENSE file for details.

---

*Daily tales woven from weather, tides, and local news of Ipswich, Massachusetts—written in the contemplative tradition of New England nature writing.*
