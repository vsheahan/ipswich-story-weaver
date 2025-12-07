"""
Comprehensive knowledge base for Ipswich, Massachusetts.

This module contains factual information about Ipswich geography, history,
ecology, and culture to ground story generation in authentic detail.
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Location:
    """A notable location in Ipswich."""
    name: str
    description: str
    category: str  # 'natural', 'historic', 'neighborhood', 'waterway'
    seasonal_notes: Dict[str, str]  # season -> observation


# =============================================================================
# GEOGRAPHIC RELATIONSHIPS - Critical for accurate storytelling
# =============================================================================
# This section describes what is NEAR what, and what is NOT near what.
# The AI must respect these spatial relationships.

GEOGRAPHIC_LAYOUT = """
## Ipswich Geographic Layout

### The River and Downtown
The Ipswich River flows EAST through town, passing under the Choate Bridge in downtown,
then continuing through salt marshes to Ipswich Bay. The river is near:
- Downtown/Market Street area (the river runs just south of downtown)
- The Riverwalk (follows the river from downtown toward the marshes)
- The Choate Bridge (the stone bridge downtown where Route 1A crosses)
- The marshes east of downtown

The river is NOT near:
- High Street (which is uphill/west of downtown, a residential historic area)
- Town Hill (which overlooks downtown from above)
- Linebrook (the rural western part of town)
- The beach areas (Great Neck, Little Neck, Crane Beach are on the coast, not the river)

### High Street
High Street runs roughly parallel to downtown but UPHILL/WEST of the river. It's a
quiet residential street with historic First Period houses. It connects to:
- Town Hill area (uphill from downtown)
- Meeting House Green (near First Church)
- South Main Street

High Street does NOT:
- Run along the river (the Riverwalk does that)
- Have river views (it's on higher ground, inland)
- Connect to the marshes or coast

### The Coast vs The River
Ipswich has TWO distinct water areas:
1. THE RIVER (Ipswich River) - freshwater/tidal, runs through downtown
2. THE COAST (Ipswich Bay, Crane Beach, Great Neck, Little Neck) - ocean

The Great Marsh is between the two, where the river becomes tidal and meets the sea.

### Neighborhoods by Area
DOWNTOWN/CENTRAL: Market Street, Central Street, Lord Square, Choate Bridge, Riverwalk
UPHILL/WEST OF DOWNTOWN: High Street, Town Hill, South Main Street
RURAL WEST: Linebrook, Appleton Farms, Willowdale State Forest
COASTAL: Great Neck, Little Neck, Crane Beach, Castle Hill, Argilla Road
MARSH AREA: Jeffrey's Neck, Essex Road Corridor, Great Marsh

### Key Distances
- Downtown to Crane Beach: about 5 miles via Argilla Road
- Downtown to Linebrook: about 3 miles inland/west
- High Street to the river: about 0.3 miles (and uphill)
- Downtown to the open ocean: about 4 miles through the marsh
"""

# =============================================================================
# GEOGRAPHY - Neighborhoods and Areas
# =============================================================================

NEIGHBORHOODS = [
    Location(
        name="Downtown Ipswich",
        description="The historic heart of town, centered on the intersection of "
                    "Market Street and Central Street, with brick storefronts, "
                    "the 1634 Meetinghouse Green, and the graceful white spire "
                    "of the First Church rising above the rooftops.",
        category="neighborhood",
        seasonal_notes={
            "spring": "Window boxes along Market Street burst with early tulips and daffodils.",
            "summer": "The sidewalk cafes fill with visitors bound for Crane Beach.",
            "autumn": "The maples along South Main blaze crimson against the white clapboard.",
            "winter": "Wreaths adorn the colonial doorways, and wood smoke rises from old chimneys."
        }
    ),
    Location(
        name="The Riverwalk",
        description="A winding path along the Ipswich River from the town center "
                    "toward the salt marshes, passing beneath ancient willows and "
                    "offering views of the tidal estuary where freshwater meets the sea.",
        category="natural",
        seasonal_notes={
            "spring": "Alewives run upstream, their silver bodies flashing in the shallows.",
            "summer": "Kayakers glide past families picnicking on the grassy banks.",
            "autumn": "The willows turn gold and drop their leaves into the slow current.",
            "winter": "Ice edges form along the banks where the tide cannot reach."
        }
    ),
    Location(
        name="High Street",
        description="One of the finest concentrations of First Period houses in America, "
                    "where homes from the 1600s and 1700s stand with their massive chimneys, "
                    "diamond-paned windows, and weathered clapboards telling three centuries of stories.",
        category="historic",
        seasonal_notes={
            "spring": "Lilacs bloom in dooryard gardens planted generations ago.",
            "summer": "Tourists pause to photograph the Whipple House and the John Heard House.",
            "autumn": "The old houses seem to sink deeper into history as leaves fall around them.",
            "winter": "Snow softens the ancient rooflines and fills the cart paths of old."
        }
    ),
    Location(
        name="Town Hill",
        description="The rise of land behind the First Church where the earliest settlers "
                    "built their homes within sight of each other, now a quiet residential "
                    "area with views down to the river and across to Castle Hill.",
        category="neighborhood",
        seasonal_notes={
            "spring": "The old apple trees behind the houses cloud with pink blossoms.",
            "summer": "Children's voices carry from backyards at dusk.",
            "autumn": "The hilltop offers views of the marsh turning copper and gold.",
            "winter": "Sledders find gentle slopes between the old estates."
        }
    ),
    Location(
        name="Argilla Road",
        description="The long winding road to Crane Beach, passing salt marshes, "
                    "farmland, and the stone walls of old estates before arriving "
                    "at the barrier beach and dune system.",
        category="neighborhood",
        seasonal_notes={
            "spring": "The marshes green up with fresh spartina, egrets returning.",
            "summer": "Cars line up for beach parking on hot July mornings.",
            "autumn": "Farm stands sell the last of the corn and early pumpkins.",
            "winter": "The road is quiet, the beach empty save for dedicated walkers."
        }
    ),
    Location(
        name="Great Neck",
        description="A peninsula reaching into Ipswich Bay, dotted with summer cottages "
                    "and year-round homes, with views across to Plum Island and the "
                    "open Atlantic beyond.",
        category="neighborhood",
        seasonal_notes={
            "spring": "Ospreys return to their platform nests along the shore.",
            "summer": "Sailboats anchor in the lee of the neck for lazy afternoons.",
            "autumn": "Storm watchers gather to see the nor'easters roll in.",
            "winter": "The summer people are gone; only the hardy remain."
        }
    ),
    Location(
        name="Little Neck",
        description="A smaller peninsula adjacent to Great Neck, with narrow lanes "
                    "and cottages perched above rocky shores.",
        category="neighborhood",
        seasonal_notes={
            "spring": "The first beach roses push green shoots through sandy soil.",
            "summer": "Lobster pots bob offshore; the scent of salt hangs in the air.",
            "autumn": "The neighborhood grows quiet as summer residents close their houses.",
            "winter": "Waves crash against the seawall during winter storms."
        }
    ),
    Location(
        name="Jeffrey's Neck",
        description="A residential peninsula with views of the Essex River estuary "
                    "and the Great Marsh, named for an early settler.",
        category="neighborhood",
        seasonal_notes={
            "spring": "Shorebirds probe the mud flats as tides recede.",
            "summer": "Clammers wade the flats at low tide with their rakes and buckets.",
            "autumn": "The marsh grasses turn to burnished gold in slanting light.",
            "winter": "Ice floes drift on the outgoing tide."
        }
    ),
    Location(
        name="Linebrook",
        description="The rural western reaches of Ipswich, where farms and forests "
                    "stretch toward Topsfield, crossed by stone walls and quiet roads.",
        category="neighborhood",
        seasonal_notes={
            "spring": "Fields are plowed and planted; robins hunt the turned earth.",
            "summer": "Hay is cut and baled; the sweet smell drifts for miles.",
            "autumn": "Apple orchards bend with fruit; cider presses run.",
            "winter": "Cross-country skiers traverse the snowy fields."
        }
    ),
    Location(
        name="Heard's Village",
        description="A small cluster of historic buildings near the town center, "
                    "including workers' housing from the era of Ipswich's lace mills.",
        category="historic",
        seasonal_notes={
            "spring": "Crocuses push through the old brick walkways.",
            "summer": "Window boxes overflow with petunias and geraniums.",
            "autumn": "The brick glows warm in the afternoon sun.",
            "winter": "Icicles hang from the eaves of the old mill workers' homes."
        }
    ),
    Location(
        name="Lord Square",
        description="A small green at the heart of downtown where roads converge, "
                    "with the town's war memorials and benches beneath old elms.",
        category="neighborhood",
        seasonal_notes={
            "spring": "Flags are placed for Memorial Day; tulips ring the monuments.",
            "summer": "Farmers market vendors set up on Saturday mornings.",
            "autumn": "Fallen leaves gather against the base of the granite memorials.",
            "winter": "The Christmas tree rises at the square's center."
        }
    ),
    Location(
        name="Essex Road Corridor",
        description="The route connecting Ipswich to neighboring Essex, passing "
                    "through marsh and farmland, with antique shops and small businesses.",
        category="neighborhood",
        seasonal_notes={
            "spring": "Forsythia blazes yellow along old property lines.",
            "summer": "Roadside stands sell vegetables and fresh eggs.",
            "autumn": "The drive offers spectacular views of the changing marsh.",
            "winter": "The road is quiet, the antique shops keeping shorter hours."
        }
    ),
]

# =============================================================================
# GEOGRAPHY - Natural Features
# =============================================================================

NATURAL_FEATURES = [
    Location(
        name="Crane Beach",
        description="Over four miles of barrier beach with towering dunes, "
                    "white sand, and cold Atlantic waters. Part of the Crane Estate, "
                    "preserved by The Trustees of Reservations. The dunes rise sixty feet "
                    "and shelter rare plants and nesting piping plovers.",
        category="natural",
        seasonal_notes={
            "spring": "Piping plovers return to nest; sections are roped off for protection.",
            "summer": "Thousands come to swim and sun; the greenhead flies arrive in July.",
            "autumn": "The crowds thin; seals haul out on the sandbars.",
            "winter": "Storm surf reshapes the beach; hardy walkers have miles to themselves."
        }
    ),
    Location(
        name="Castle Hill and the Crane Estate",
        description="The grand estate of Chicago industrialist Richard T. Crane Jr., "
                    "with its Stuart-style Great House (1928) set atop a drumlin overlooking "
                    "the sea, surrounded by formal gardens and the famous Grand Allee "
                    "of grass descending to the salt marsh.",
        category="historic",
        seasonal_notes={
            "spring": "The rose garden is pruned and mulched; tours begin for the season.",
            "summer": "Concerts on the lawn draw crowds with picnic baskets.",
            "autumn": "The Grand Allee glows golden; the estate hosts harvest festivals.",
            "winter": "The Great House is decorated for the holidays; special tours run."
        }
    ),
    Location(
        name="The Great Marsh",
        description="One of the largest continuous salt marshes in New England, "
                    "stretching from Ipswich through Essex to Gloucester. A maze of "
                    "tidal creeks, spartina grass, and mud flats teeming with life, "
                    "protected as an Area of Critical Environmental Concern.",
        category="natural",
        seasonal_notes={
            "spring": "The marsh greens up; fiddler crabs emerge; herons stalk the creeks.",
            "summer": "The spartina grows tall; the air hums with insects and birds.",
            "autumn": "The marsh turns gold, then copper; migrating birds gather in thousands.",
            "winter": "Ice forms in the creeks; snow geese pass overhead."
        }
    ),
    Location(
        name="Plum Island Sound",
        description="The protected waters between Plum Island and the mainland, "
                    "fed by the Parker, Rowley, and Ipswich Rivers, rich with shellfish "
                    "and finfish, a nursery for the sea.",
        category="natural",
        seasonal_notes={
            "spring": "Striped bass begin their run; fishing boats return to the sound.",
            "summer": "Pleasure boats anchor in the calm waters; seals sun on sandbars.",
            "autumn": "Migrating waterfowl raft in vast numbers.",
            "winter": "Sea ducks dive for mussels in the cold, gray waters."
        }
    ),
    Location(
        name="The Ipswich River",
        description="Rising in the swamps of Wilmington and Burlington, flowing "
                    "thirty-five miles to the sea at Ipswich Bay. The river's estuary "
                    "is tidal for miles inland, where fresh and salt water mix.",
        category="waterway",
        seasonal_notes={
            "spring": "The river runs high with snowmelt; alewives surge upstream to spawn.",
            "summer": "Kayakers paddle the tidal reaches; herons fish the shallows.",
            "autumn": "The riverside trees flame with color reflected in still water.",
            "winter": "Ice edges the banks; the center runs dark and cold."
        }
    ),
    Location(
        name="Miles River",
        description="A tributary of the Ipswich River, winding through marsh and "
                    "farmland in the southwestern part of town.",
        category="waterway",
        seasonal_notes={
            "spring": "The floodplains fill; wood ducks nest in the riverside trees.",
            "summer": "Turtles sun on logs; dragonflies dart above the water.",
            "autumn": "Muskrats build their lodges for winter.",
            "winter": "The narrow stream freezes solid in hard cold snaps."
        }
    ),
    Location(
        name="Appleton Farms",
        description="One of the oldest continuously operating farms in America, "
                    "now part of The Trustees of Reservations. Over one thousand acres "
                    "of grasslands, pastures, hayfields, and forest trails where cattle "
                    "graze as they have for nearly four centuries.",
        category="natural",
        seasonal_notes={
            "spring": "Calves are born; the fields green up; wildflowers dot the meadows.",
            "summer": "Hay is cut; the farm store sells vegetables and grass-fed beef.",
            "autumn": "The harvest comes in; the grass turns tawny under October skies.",
            "winter": "Cross-country skiers glide across the snowy pastures."
        }
    ),
    Location(
        name="Willowdale State Forest",
        description="Over two thousand acres of forest, wetlands, and trails in "
                    "the interior of Ipswich, popular with hikers, mountain bikers, "
                    "and equestrians. Pine groves and hardwood stands surround "
                    "hidden ponds and cranberry bogs.",
        category="natural",
        seasonal_notes={
            "spring": "Lady slippers bloom; vernal pools fill with wood frog eggs.",
            "summer": "The forest offers cool shade; mosquitoes swarm the wetlands.",
            "autumn": "The hardwoods blaze; hunters take to the woods for deer season.",
            "winter": "Snow quiets the forest; animal tracks tell stories in the white."
        }
    ),
    Location(
        name="The Dune System",
        description="The barrier dunes at Crane Beach, formed over thousands of years, "
                    "home to rare plants like beach heather and dusty miller, "
                    "and critical nesting habitat for endangered piping plovers.",
        category="natural",
        seasonal_notes={
            "spring": "Beach grass pushes new shoots; plovers scrape their nests in sand.",
            "summer": "The dunes shimmer in heat; visitors stick to marked trails.",
            "autumn": "Storm tides reshape the dune faces; beach plum ripens.",
            "winter": "Nor'easters test the dunes' resilience."
        }
    ),
    Location(
        name="Wolf Hollow",
        description="A wolf sanctuary at 114 Essex Road, home to eight North American gray wolves "
                    "and one wolf-dog hybrid. Founded in 1988 by Paul C. Soffron to change "
                    "perceptions of wolves through education. Offers guided tours on weekends.",
        category="natural",
        seasonal_notes={
            "spring": "The wolves grow restless as days lengthen; their thick winter coats shed.",
            "summer": "Educational programs bring families to learn wolf biology and behavior.",
            "autumn": "The wolves' howls carry far on crisp nights as the pack grows vocal.",
            "winter": "Prime season for photography as earlier sunset provides dramatic lighting."
        }
    ),
    Location(
        name="Choate Island",
        description="The largest island in the Crane Wildlife Refuge, about 135 acres in the "
                    "Essex River Estuary. Formerly called Hog Island, accessible only by boat. "
                    "Features grasslands, spruce forest, and the Crane family burial site.",
        category="natural",
        seasonal_notes={
            "spring": "Ospreys return to nest on the island's platforms.",
            "summer": "Kayakers paddle from the Crane Wildlife Refuge dock to explore.",
            "autumn": "The island's grasses turn gold against the blue estuary.",
            "winter": "The island stands quiet, its paths empty of visitors."
        }
    ),
]

# =============================================================================
# IPSWICH RIVER - Enhanced Ecological Data
# =============================================================================

IPSWICH_RIVER_ECOLOGY = {
    "overview": {
        "length": "35-45 miles from Burlington/Wilmington headwaters to Ipswich Bay",
        "character": "Flows through town, under the Choate Bridge, then through salt marshes to the sea",
        "significance": "Interface between salt and fresh water at head of tide is an extremely rare ecosystem",
    },
    "seasonal_flow": {
        "spring": {
            "conditions": "Highest flows from snowmelt and spring rains",
            "peak_flow": "Can reach 700 cubic feet per second at South Middleton gauge",
            "paddling": "Excellent conditions for kayaking and canoeing",
        },
        "summer": {
            "conditions": "Severe flow reduction, often dropping 99% from spring peak",
            "concerns": "Upper third may run dry; dissolved oxygen can drop below state standards",
            "impact": "Potential fish kills, loss of aquatic life diversity",
        },
        "fall": {
            "conditions": "Gradual recovery with autumn rains",
            "recovery": "Water quality improves as evapotranspiration decreases",
        },
        "winter": {
            "conditions": "Low to moderate flows, ice formation in coldest periods",
            "groundwater": "Winter replenishment of aquifers",
        },
    },
    "fish_species": {
        "alewife": {
            "name": "Alewife (Alosa pseudoharengus)",
            "behavior": "Spawn in slow-moving water, prefer ponds/lakes, spawn at night",
            "timing": "Earlier migration than blueback, arrive late March",
        },
        "blueback_herring": {
            "name": "Blueback Herring (Alosa aestivalis)",
            "behavior": "Spawn in main stem rivers over rocks in fast water during daylight",
            "timing": "Late May through mid-June",
        },
        "american_eel": {
            "name": "American Eel (Anguilla rostrata)",
            "behavior": "Catadromous: hatch in salt water, live in freshwater",
            "description": "Smooth, slender, snake-like appearance",
        },
        "striped_bass": {
            "name": "Striped Bass (Morone saxatilis)",
            "behavior": "Follow herring runs into tidal portions in spring",
            "note": "May reports of fish up to 40 inches caught near herring runs",
        },
    },
    "dams_and_restoration": {
        "ipswich_mills_dam": {
            "status": "Removal being designed and permitted",
            "current_fish_ladder": "Limited effectiveness; American shad cannot navigate it",
            "monitoring": "Underwater video camera operates 24/7 during spring count season",
        },
        "howlett_brook_dam": {
            "status": "Fishway recently constructed",
            "benefit": "Allows herring to reach historic spawning ponds",
        },
        "restoration_funding": "$2.5 million NOAA funding for dam removal and habitat restoration",
    },
    "herring_runs": {
        "timing": "Late March through June, peaking in April-May",
        "volunteer_counts": "Conducted since 1999",
        "historical_note": "Runs dramatically reduced due to dams; restoration ongoing",
    },
}

# =============================================================================
# HISTORICAL FIGURES - Deep biographical knowledge
# =============================================================================

HISTORICAL_FIGURES = {
    "jenny_slew": {
        "name": "Jenny Slew",
        "dates": "c. 1719 - after 1765",
        "significance": "First enslaved person in Massachusetts to win freedom through jury trial",
        "story": """In January 1762, Jenny Slew—a free woman born to a white mother—was
kidnapped from her Ipswich home and illegally enslaved by John Whipple Jr. She fought back
through the courts. In November 1766, before an all-white male jury in Salem, she won her
freedom. Judge Oliver declared: 'This is a contest between liberty and property—both of
great consequence, but liberty of most importance of the two.' John Adams attended the
trial and took notes. Her victory inspired subsequent freedom suits that helped end
slavery in Massachusetts.""",
        "memorial": "Depicted on the EBSCO Riverwalk Mural receiving payment from Whipple",
    },
    "masconomet": {
        "name": "Masconomet (Sagamore of the Agawam)",
        "dates": "Unknown - March 6, 1658",
        "significance": "Last great leader of the Agawam people",
        "story": """Masconomet—whose Pawtucket name meant 'He who vanquished a black bear'—led
the Agawam people when English colonists arrived. His tribe had been decimated by plague,
losing 90% of their population. Fearing attacks from the Abenaki, he invited the English
to settle on tribal lands for mutual protection, selling land to John Winthrop Jr. for £20.
He spent winters at Wamesit (modern Lowell) and summers at Agawam. He died in 1658 and was
buried on Sagamore Hill with his gun and tomahawk. A stone monument now marks his grave.""",
        "location": "Sagamore Hill (now Hamilton)",
    },
    "anne_bradstreet": {
        "name": "Anne Bradstreet",
        "dates": "March 8, 1612 - September 16, 1672",
        "significance": "First published poet in England's North American colonies",
        "story": """Anne Bradstreet arrived in Salem aboard the Arbella in 1630, eventually
settling in Ipswich in the late 1630s with her husband Simon (later governor of Massachusetts).
Here, despite demanding domestic responsibilities and frontier hardships, she began writing
poetry in earnest. The town's educated residents—with their large libraries and love of the
written word—nurtured her talent. She knew John Winthrop Jr. and Nathaniel Ward. A bronze
plaque marks the site of her Ipswich home. Her husband became governor of Massachusetts.""",
        "location": "Downtown Ipswich (plaque marks home site)",
    },
    "arthur_wesley_dow": {
        "name": "Arthur Wesley Dow",
        "dates": "1857-1922",
        "significance": "Influential artist and educator who shaped American modernism",
        "story": """Born in Ipswich, Dow found endless inspiration in the flat coastal landscape
and subtly shifting light of the marshes. After studying in Paris and discovering Japanese
woodblock prints at the Boston Public Library, he remarked: 'One evening with Hokusai gave me
more light on composition and decorative effect than years of study of pictures.' He founded
the Ipswich Summer School of Art and later headed Columbia's art department. His students
included Georgia O'Keeffe and Charles Sheeler. The Ipswich Museum holds the largest
collection of his works.""",
        "location": "Ipswich Museum holds the Dow Collection",
    },
    "nathaniel_ward": {
        "name": "Nathaniel Ward",
        "dates": "c. 1578-1652",
        "significance": "Author of Massachusetts' first code of laws",
        "story": """A Cambridge-educated lawyer who became a Puritan minister, Ward was relieved
of his church duties in England for his beliefs. He immigrated in 1634 and served as Ipswich's
minister. His legal background led the General Court to select him to write 'The Body of
Liberties'—the first code of laws for the colonies. In 1647, he published 'The Simple Cobbler
of Aggawam' under a pseudonym, a satiric essay attacking religious tolerance and modes of
fashion. He returned to England and died there in 1652.""",
        "work": "The Body of Liberties (1641), The Simple Cobbler of Aggawam (1647)",
    },
    "john_winthrop_jr": {
        "name": "John Winthrop Jr.",
        "dates": "February 12, 1606 - April 6, 1676",
        "significance": "Founder of Ipswich, Fellow of the Royal Society",
        "story": """The son of Massachusetts' first governor arrived with 12 men in March 1633
to establish Agawam (later Ipswich). Sagamore Masconomet signed over the land for £20 and a
promise of protection from the Abenaki. Winthrop's wife Martha died here with their infant—
the first settlers buried in Ipswich. He later moved to Connecticut, becoming governor, and
obtained its royal charter. A physician, alchemist, and scientist, he was elected to the
Royal Society in 1663—bringing international scientific credibility to the colonies.""",
        "founded": "Ipswich (1633), Saybrook (1635), New London (1646)",
    },
    "reverend_john_wise": {
        "name": "Reverend John Wise",
        "dates": "1652-1725",
        "significance": "Early advocate for taxation with representation",
        "story": """In 1687, Wise led Ipswich citizens in protesting a tax imposed by Governor
Edmund Andros, arguing that as Englishmen, taxation without representation was unacceptable.
He was jailed for his defiance. When Andros was recalled to England, new sovereigns William
and Mary issued a new charter. Wise's writings later influenced the Declaration of
Independence. His rebellion earned Ipswich the title 'Birthplace of American Independence.'""",
        "legacy": "Ipswich called 'Birthplace of American Independence'",
    },
}

# =============================================================================
# LOCAL LEGENDS AND FOLKLORE
# =============================================================================

LOCAL_LEGENDS = {
    "harry_maine": {
        "name": "The Ghost of Harry Maine",
        "type": "Ghost legend",
        "story": """Harry Maine was a mooncusser—a land pirate who used false lights to lure
ships onto the rocks, then plundered the wrecks. Legend says he was chained to Ipswich Bar
as punishment, forced to shovel sand for eternity. During storms, locals say 'The Devil is
raising Old Harry.' His ghost still wanders the Plum Island dunes on stormy nights. One tale
tells of a man who dreamed of Harry's buried treasure three nights running—when he dug at
the spot, an army of black cats with eyes of fire appeared, and icy water filled the hole.
He escaped with only an iron bar, later fashioned into a door latch still in use in Ipswich.""",
        "locations": ["Ipswich Bar", "Plum Island dunes"],
    },
    "devils_footprint": {
        "name": "The Devil's Footprint",
        "type": "Religious legend",
        "story": """On the rocks at First Church on Meetinghouse Green, a faded mark is said
to be the Devil's footprint. During the Great Awakening, the preacher George Whitefield
wrestled with the Devil outside the church. When the Devil fled, he jumped down onto the
rocks, leaving his footprint—still visible today beneath a spray-painted circle.""",
        "location": "First Church, Meetinghouse Green",
    },
    "elizabeth_howe": {
        "name": "The Witch of Linebrook",
        "type": "Historical tragedy",
        "story": """Elizabeth Howe was a successful farmer's wife who lived in outer Linebrook.
In 1692, neighbors accused her of witchcraft after a decade of suspicions. Though 13 people
spoke in her defense—describing her as honest, faithful, and fair—24 accused her. She
declared her innocence to the end but was hanged on July 19, 1692, at Proctor's Ledge near
Salem, alongside Rebecca Nurse and four others. The EBSCO Mural depicts her arrest on
Linebrook Road.""",
        "location": "Linebrook Road",
    },
    "rachel_clinton": {
        "name": "The Survivor of Hog Island",
        "type": "Historical account",
        "story": """Rachel Clinton went from one of Ipswich's wealthiest families to a
'sullen beggar' by 1692. Suspected of witchcraft for years, she was arrested and held
in iron fetters for nine months. Unlike Elizabeth Howe, she survived—released when an
unknown person paid her jail fees. She lived out her days alone in a small hut on Hog
Island (now Choate Island), dying around 1695 with nothing.""",
        "location": "Choate Island (formerly Hog Island)",
    },
}

# =============================================================================
# LOCAL BUSINESSES AND LANDMARKS
# =============================================================================

LOCAL_BUSINESSES = {
    "clam_box": {
        "name": "The Clam Box",
        "address": "246 High Street",
        "type": "Restaurant",
        "established": 1935,
        "description": """Built in 1935, the Clam Box is an iconic piece of roadside architecture—
a tall, trapezoidal building designed to look like a giant fried clam takeout container with
its flaps tipped open. Originally painted silver with red trim. On busy summer weekends,
about 1,000 people dine here. Owned by the Aggelakis family since 1984. Celebrating its
90th anniversary in 2025.""",
    },
    "zumis_coffee": {
        "name": "Zumi's Coffee House",
        "address": "2 Market Street",
        "type": "Coffee shop",
        "description": """A cozy downtown coffee house at the heart of Ipswich's Market Street,
serving specialty coffee, espresso drinks, pastries, and light fare. A popular gathering
spot for locals before work and on weekend mornings.""",
    },
    "wolf_hill_garden_center": {
        "name": "Wolf Hill Garden Center",
        "address": "196 Linebrook Road",
        "type": "Garden center",
        "description": """Full-service garden center and nursery offering annuals, perennials,
shrubs, trees, and gardening supplies. Popular spring destination for local gardeners
preparing their beds.""",
    },
    "pomodori_pizzeria": {
        "name": "Pomodori Pizzeria",
        "address": "6 Central Street",
        "type": "Restaurant",
        "description": """Italian pizzeria in downtown Ipswich serving Neapolitan-style pizza,
pasta, salads, and Italian specialties. A family-friendly spot in the heart of downtown.""",
    },
    "riverview_pizza": {
        "name": "Riverview Pizza",
        "address": "25 Hammatt Street",
        "type": "Restaurant",
        "description": """Local pizza shop near downtown serving pizza, subs, and Greek food.
A casual, affordable spot popular with families and high school students.""",
    },
    "ticks_auto": {
        "name": "Tick's Auto Shop",
        "address": "61 Turnpike Road",
        "type": "Auto repair",
        "description": """Long-standing local auto repair shop serving Ipswich residents.
A trusted fixture in town for automotive service and repairs.""",
    },
    "1640_hart_house": {
        "name": "1640 Hart House",
        "address": "51 Linebrook Road",
        "type": "Restaurant",
        "established": "Building from 1678",
        "description": """Fine dining in a historic 1670s farmhouse. The oldest parts date to
1678-1680, built by Samuel Hart. Serves New American cuisine with fresh seafood, premium
steaks, and famous lobster rolls and clam chowder.""",
    },
    "true_north_ale": {
        "name": "True North Ale Company",
        "address": "116 County Road",
        "type": "Brewery",
        "established": 2017,
        "description": """15,000+ square foot brewery with taproom and patio. Voted Best
Brewery on North Shore for four consecutive years. BYOF (Bring Your Own Food) policy.
Big Pig BBQ on patio Wednesday-Sunday.""",
    },
    "little_wolf_coffee": {
        "name": "Little Wolf Coffee Roasters",
        "address": "129 High Street",
        "type": "Coffee shop",
        "description": "Specialty micro-batch coffee roaster. Open Mon-Fri 7am-3pm, Sat-Sun 8am-3pm.",
    },
    "fox_creek_tavern": {
        "name": "Fox Creek Tavern",
        "address": "141 High Street",
        "type": "Restaurant",
        "description": """Artisan comfort food in an upscale environment with cozy fireplace
and outdoor fire pit.""",
    },
    "russell_orchards": {
        "name": "Russell Orchards",
        "address": "143 Argilla Road",
        "type": "Farm & Winery",
        "established": 1920,
        "description": """120-acre fruit and vegetable farm with retail store in an 1800s barn,
scratch bakery, cider mill, winery with wine bar, and pick-your-own fields. Founded as
Goodale Orchards when Dr. Joseph Goodale planted the first trees. Famous for homemade
cider donuts from original family recipes. Wine bar serves 22 varieties produced on-site.""",
        "seasonal_activities": {
            "summer": "Pick-your-own strawberries, cherries, blueberries, raspberries",
            "fall": "Apple picking with hayrides, 'Make Your Own' apple pie events",
            "year_round": "Wine tastings, bakery, farm store",
        },
    },
    "marini_farm": {
        "name": "Marini Farm",
        "address": "259 Linebrook Road",
        "type": "Farm",
        "established": 1928,
        "description": """Third-generation farm with greenhouses, farm stand, and seasonal
activities. June: Strawberry Festival with 12 acres of strawberry production. Fall:
10-acre maze park with 8-acre interactive corn maze, pumpkin patch, hayrides.
Winter: Christmas trees and wreath decorating.""",
    },
    "wolf_hollow": {
        "name": "Wolf Hollow",
        "address": "114 Essex Road",
        "type": "Wolf Sanctuary",
        "established": 1988,
        "description": """Non-profit wolf sanctuary founded by Paul C. Soffron. Home to eight
animals: seven pure North American gray wolves and one wolf-dog hybrid. Offers educational
tours on Saturdays and Sundays (reservations required), school field trips, photography
sessions, and private tours. Mission: to change perceptions of wolves through education
and exposure, dispelling myths and raising awareness of wolves' key role in ecosystems.""",
    },
}

# =============================================================================
# IPSWICH PUBLIC SCHOOLS
# =============================================================================

IPSWICH_SCHOOLS = {
    "doyon_elementary": {
        "name": "Paul F. Doyon Memorial School",
        "address": "51 North Main Street",
        "type": "Elementary School",
        "grades": "Pre-K through 2",
        "description": """Named after Paul F. Doyon, a longtime Ipswich educator. Serves the
youngest students in the district. Located near downtown on North Main Street.""",
    },
    "winthrop_elementary": {
        "name": "Winthrop Elementary School",
        "address": "201 High Street",
        "type": "Elementary School",
        "grades": "3 through 5",
        "description": """Elementary school serving grades 3-5. Located on High Street in
the historic part of town. Named for the Winthrop family, early settlers of Massachusetts.""",
    },
    "ipswich_middle_school": {
        "name": "Ipswich Middle School",
        "address": "130 High Street",
        "type": "Middle School",
        "grades": "6 through 8",
        "description": """Middle school serving the town's 6th through 8th graders. Part of
the High Street school campus alongside the elementary and high schools.""",
    },
    "ipswich_high_school": {
        "name": "Ipswich High School",
        "address": "134 High Street",
        "type": "High School",
        "grades": "9 through 12",
        "mascot": "Tigers",
        "description": """Home of the Ipswich Tigers. Competitive athletic programs, particularly
in wrestling, soccer, and cross country. Students graduate with strong connections to the
community. The school's location on High Street makes it central to town life.""",
    },
}

# =============================================================================
# THE EBSCO MURAL
# =============================================================================

EBSCO_MURAL = {
    "year": 2005,
    "artist": "Alan Pearsall",
    "size": "2,700 square feet",
    "location": "EBSCO Publishing building, Ipswich Riverwalk",
    "description": """The centerpiece of the Ipswich Riverwalk, this mural depicts several
hundred years of Ipswich history. Key scenes include: Elizabeth Howe being arrested for
witchcraft on Linebrook Road (she was hanged July 19, 1692); Jenny Slew receiving payment
of damages after winning her freedom suit; and Richard Saltonstall, who built the town's
first mill on this site and in 1645 denounced the kidnapping of two Africans as 'expressly
contrary to the law of God and the law of the country.' Many local people modeled for the
historical figures.""",
}

# =============================================================================
# WILLOWDALE STATE FOREST - Detailed Trail Information
# =============================================================================

WILLOWDALE_TRAILS = {
    "overview": {
        "size": "2,400 acres",
        "towns": ["Hamilton", "Topsfield", "Boxford"],
        "trail_miles": 40,
        "parking": ["259 Linebrook Road (Ipswich)", "280 Ipswich Road (Topsfield)"],
        "access": "Free, open sunrise to sunset year-round",
    },
    "areas": {
        "pine_swamp": {
            "description": "Northern section with the best singletrack mountain biking trails",
            "character": "Mix of rolling, smooth, and rooted single and doubletrack with climbs, descents, and switchbacks",
            "trail_markers": "Numbered markers at all main intersections",
        },
        "hood_pond": {
            "size": "100 acres",
            "activities": ["Canoeing", "Fishing"],
            "description": "Large pond in the western section where Ipswich, Boxford, and Topsfield meet",
            "trail": "Hood Pond Loop - 16.3 miles, moderately challenging, ~5.5 hours",
        },
        "bay_circuit_trail": {
            "description": "White-blazed trail running through Willowdale",
            "length": "7-8 miles through the forest",
            "character": "Mostly flat with a few hills, well-marked and easy to follow",
            "connections": "Links Bradley Palmer State Park (south) with Cleveland Farm State Forest (west)",
        },
    },
    "habitat": "Pine-oak-hickory upland, red maple swamp, hemlock stands, beaver marsh",
    "seasonal_activities": {
        "spring": "Excellent birding for breeding birds, wildflower viewing",
        "summer": "Hiking, mountain biking, canoeing/kayaking on Hood Pond",
        "fall": "Peak foliage viewing, continued hiking/biking (mud season restrictions March 1-April 30)",
        "winter": "Cross-country skiing on 40 miles of trails, snowshoeing",
    },
}

# =============================================================================
# FIRST PERIOD HOUSES - Specific historic buildings
# =============================================================================

FIRST_PERIOD_HOUSES = [
    {
        "name": "Captain John Whipple House",
        "address": "1 South Green / 53 South Main Street",
        "built": 1677,
        "description": """Built for Captain John Whipple, military officer and entrepreneur.
Left half built 1677, expanded 1680-1690, enlarged 1710 with lean-tos. Originally on
Saltonstall Street, moved over Choate Bridge in 1927. Now a museum, National Historic
Landmark, filled with original architectural detail and early furniture.""",
    },
    {
        "name": "Ross Tavern",
        "address": "52 Jeffreys Neck Road",
        "built": "c. 1690",
        "description": """Built c. 1690 in downtown Ipswich, moved to current location in 1940.
Features 17th-century fireplaces and 17th & 18th-century woodwork. The cyma molded
overhanging girt and dentils represent Ipswich's 'distinctly elegant regional school'
of architecture. Operated as an inn by Jeremiah Ross starting in 1809.""",
    },
    {
        "name": "Thomas Lord House",
        "address": "17 High Street",
        "built": 1658,
        "description": "Built by cordwainer Thomas Lord. One of the oldest houses on High Street.",
    },
    {
        "name": "Philip Call House",
        "address": "26 High Street",
        "built": 1659,
        "description": "Two-story timber-frame house built by cordwainer Philip Call.",
    },
    {
        "name": "Thomas Dennis House",
        "address": "7 County Street",
        "built": "1663-1750",
        "description": "Home of master joiner Thomas Dennis, known for his elaborate carved furniture.",
    },
    {
        "name": "Hart House",
        "address": "51 Linebrook Road",
        "built": "1678-1680",
        "description": "Oldest parts built 1678-1680 by Samuel Hart. Now the 1640 Hart House restaurant.",
    },
    {
        "name": "Giddings-Burnham House",
        "address": "43 Argilla Road",
        "built": "c. 1640/1680",
        "description": "Earliest section from mid-17th century by carpenter George Giddings.",
    },
]

# =============================================================================
# CHOATE BRIDGE - Historic landmark details
# =============================================================================

CHOATE_BRIDGE = {
    "built": 1764,
    "location": "Route 1A/Route 133 (South Main Street) over Ipswich River",
    "significance": "Oldest documented two-span masonry arch bridge in the United States",
    "specifications": {
        "total_length": "72 feet (22 m)",
        "arch_span": "30 feet 6 inches each",
        "material": "Roughly dressed granite",
        "original_width": "20 feet (1764)",
        "widened": "16 feet added in 1838 (single lane to two lanes)",
    },
    "named_for": "Colonel John Choate, who supervised construction at no charge to the town",
    "legend": "Colonel Choate was allegedly the first person to ride his horse over the bridge",
    "designations": ["National Register of Historic Places (1972)", "National Historic Civil Engineering Landmark"],
    "previous_bridges": "Timber bridges at this location since 1641, needing frequent repair",
}

# =============================================================================
# HISTORY - Expanded with research findings
# =============================================================================

HISTORICAL_FACTS = [
    {
        "topic": "Colonial Settlement",
        "content": "Ipswich was settled in 1633 by John Winthrop the Younger, "
                   "making it one of the oldest towns in Massachusetts. Named Agawam "
                   "by the native Agawam people, the English renamed it for Ipswich, "
                   "England. Within two decades, it was the second largest town in "
                   "the Massachusetts Bay Colony."
    },
    {
        "topic": "First Period Architecture",
        "content": "Ipswich contains the greatest concentration of First Period "
                   "(pre-1725) houses in North America. The Whipple House (c. 1655), "
                   "the John Heard House (1795), and dozens of others preserve the "
                   "building traditions of the first English settlers, with massive "
                   "oak frames, steep rooflines, and central chimneys."
    },
    {
        "topic": "The Choate Bridge",
        "content": "Built in 1764, the Choate Bridge is the oldest double-arched "
                   "stone bridge in America still in use. Its twin Roman arches of "
                   "local granite have carried travelers across the Ipswich River "
                   "for over 260 years, a testament to colonial engineering."
    },
    {
        "topic": "Witchcraft Accusations",
        "content": "In 1692, during the Salem witchcraft hysteria, several Ipswich "
                   "residents were accused of witchcraft. The town's magistrates "
                   "showed notable skepticism; no Ipswich resident was executed. "
                   "The Reverend John Wise of Ipswich became an early voice against "
                   "the trials' excesses."
    },
    {
        "topic": "John Wise and Colonial Dissent",
        "content": "The Reverend John Wise of Ipswich led the 1687 protest against "
                   "Governor Andros's taxation without representation, anticipating "
                   "the Revolution by nearly a century. Wise was briefly imprisoned "
                   "for his defiance. His later writings influenced the Declaration "
                   "of Independence."
    },
    {
        "topic": "The Lace Industry",
        "content": "From the 1820s through the early 1900s, Ipswich was a center "
                   "of lace manufacturing in America. Mills along the river produced "
                   "machine-made lace, employing hundreds of workers, many of them "
                   "immigrant women. The industry shaped the town's economy and "
                   "ethnic diversity for generations."
    },
    {
        "topic": "Maritime Heritage",
        "content": "Ipswich's economy was built on the sea. Fishing, shipbuilding, "
                   "and coastal trade flourished from the colonial era through the "
                   "nineteenth century. The clam flats and shellfish beds of the "
                   "Great Marsh have been harvested for centuries, and Ipswich clams "
                   "remain famous throughout New England."
    },
    {
        "topic": "The Crane Family",
        "content": "Richard T. Crane Jr., heir to the Chicago plumbing fortune, "
                   "purchased Castle Hill in 1910 and built the Great House in 1928. "
                   "His family donated the estate to The Trustees of Reservations "
                   "in 1945, preserving Crane Beach and Castle Hill for the public "
                   "in perpetuity."
    },
    {
        "topic": "Revolutionary War",
        "content": "Ipswich contributed men and supplies to the Revolutionary cause. "
                   "Local militiamen marched to Lexington and Concord in April 1775. "
                   "The town's seafaring tradition made it a target for British "
                   "naval patrols; residents watched anxiously for enemy sails."
    },
    {
        "topic": "Literary Connections",
        "content": "John Greenleaf Whittier, the Quaker poet of Amesbury, wrote "
                   "of Ipswich's beauty and history. Nathaniel Hawthorne visited "
                   "the town and drew on its colonial past. The landscape has inspired "
                   "writers for centuries with its blend of history and natural beauty."
    },
    {
        "topic": "Jenny Slew's Freedom Suit",
        "content": "In 1766, Jenny Slew became the first enslaved person in Massachusetts "
                   "to win freedom through a jury trial. Kidnapped from Ipswich in 1762, "
                   "she sued her enslaver John Whipple Jr. Judge Oliver declared: 'This is "
                   "a contest between liberty and property—but liberty of most importance.' "
                   "John Adams attended the trial. Her victory inspired subsequent freedom suits."
    },
    {
        "topic": "The Invention of Fried Clams",
        "content": "On July 3, 1916, Lawrence 'Chubby' Woodman and his wife Bessie "
                   "invented the fried clam at their Essex concession stand. A fisherman "
                   "named Tarr suggested they fry clams like their potato chips. They "
                   "experimented with batters, settling on evaporated milk and corn flour. "
                   "The Soffron Brothers later supplied Howard Johnson for 32 years."
    },
    {
        "topic": "The Hosiery Industry",
        "content": "In 1822, an English stocking machine was smuggled to Ipswich, buried "
                   "in a ship's cargo of loose salt to evade British export penalties. By the "
                   "turn of the 20th century, Ipswich Mills became the largest stocking mill "
                   "in the country, attracting waves of immigrants—Irish, French Canadian, "
                   "Polish, Greek. The mill buildings now house EBSCO Publishing."
    },
    {
        "topic": "The EBSCO Mural",
        "content": "In 2005, artist Alan Pearsall completed a 2,700 square-foot mural "
                   "on the EBSCO building depicting Ipswich history. It shows Elizabeth Howe's "
                   "arrest for witchcraft, Jenny Slew receiving payment after winning her freedom, "
                   "and Richard Saltonstall who in 1645 denounced slavery as 'contrary to the law "
                   "of God and the law of the country.'"
    },
    {
        "topic": "Birthplace of American Independence",
        "content": "In 1687, Reverend John Wise led Ipswich citizens in protesting "
                   "Governor Andros's tax, arguing that taxation without representation was "
                   "unacceptable. Wise was jailed but vindicated when Andros was recalled to "
                   "England. Wise's writings influenced the Declaration of Independence, "
                   "earning Ipswich the title 'Birthplace of American Independence.'"
    },
    {
        "topic": "The Agawam People",
        "content": "The Agawam tribe, led by Sagamore Masconomet, inhabited the region "
                   "when English colonists arrived. Decimated by plague (90% loss), they "
                   "invited the English to settle for mutual protection against the Abenaki. "
                   "Masconomet sold the land to John Winthrop Jr. for £20 in 1638. 'Agawam' "
                   "means 'low land' or 'marsh' in Algonquian."
    },
]

# =============================================================================
# CLAMMING CULTURE - The Ipswich Clam Industry
# =============================================================================

CLAMMING_CULTURE = {
    "overview": {
        "significance": "Ipswich is famous as the home of the 'Ipswich clam'",
        "industry_value": "$2.2 million (2018), nearly 1/3 of Massachusetts total",
        "what_makes_them_special": """The mud in salt marshes along the Ipswich, Eagle,
Essex, and Parker Rivers gives Ipswich clams their signature sweet, rich flavor with
less residual sediment. The unique combination of minerals, saltier water, and
fluctuating ocean currents creates the distinctive taste.""",
    },
    "clam_flats": {
        "locations": ["Ipswich River flats", "Eagle River", "Essex River", "Parker River"],
        "access": "Shellfish permits required from Town of Ipswich",
        "regulations": {
            "resident_permit": "$40/year plus $10 enhancement fee",
            "non_resident_ma_permit": "$150/year plus $10 enhancement fee",
            "one_day_non_resident": "$20",
            "tools": "Only clam forks approved by Shellfish Constable",
            "closed_days": "All areas closed Sundays during May-September",
        },
    },
    "clam_species": {
        "soft_shell": {
            "name": "Soft-Shell Clams (Mya arenaria)",
            "also_known_as": "Steamers, Ipswich Clams",
            "preparation": "Best steamed with melted butter",
            "threats": "European green crab predation (can eat 40 clams/day)",
        },
        "razor_clams": {
            "name": "Razor Clams (Ensis leei)",
            "description": "Long, thin bivalves resembling straight razors",
            "harvest": "Hand-scratched from sand flats",
        },
    },
    "history": {
        "colonial_era": "Clam flats harvested by colonists since the 1630s",
        "invention_of_fried_clam": {
            "date": "July 3, 1916",
            "inventors": "Lawrence 'Chubby' Woodman and wife Bessie",
            "location": "Essex, Massachusetts",
            "inspiration": "Fisherman named Tarr suggested frying clams like potato chips",
            "recipe": "Evaporated milk and corn flour batter",
        },
        "howard_johnson_connection": """The Soffron Brothers were exclusive suppliers
to Howard Johnson restaurants for 32 years. Thomas Soffron invented a patented device
to tenderize tough surf clam meat for clam strips.""",
    },
}

# =============================================================================
# ECOLOGY AND WILDLIFE
# =============================================================================

WILDLIFE_BY_SEASON = {
    "spring": [
        "Alewives run up the Ipswich River to spawn, their silver bodies flashing in the shallows.",
        "Piping plovers return to Crane Beach to nest in the sand.",
        "Ospreys rebuild their platform nests on poles along the marsh.",
        "Great blue herons stalk the marsh creeks for killifish.",
        "Wood frogs call from vernal pools in Willowdale State Forest.",
        "Tree swallows arrive to nest in boxes along the farm fields.",
        "Horseshoe crabs crawl onto beaches to lay their eggs under full moons.",
        "Migrating warblers pause in the forest understory.",
        "Red-winged blackbirds stake out territories in the phragmites.",
        "Striped bass begin their northward migration through the sound.",
    ],
    "summer": [
        "Greenhead flies emerge from the salt marsh to plague beachgoers in July.",
        "Terns dive for sand eels in the waters off Crane Beach.",
        "Harbor seals haul out on sandbars at low tide.",
        "Fireflies blink in the fields at dusk.",
        "Snowy egrets and great egrets fish the marsh at dawn.",
        "Monarch butterflies pass through on their way south.",
        "Horseshoe crab shells litter the tide line after spawning.",
        "Bluefish chase baitfish into the shallows, churning the water.",
        "Barn swallows raise second broods in the farm buildings.",
        "Diamondback terrapins nest in sandy areas near the marsh.",
    ],
    "autumn": [
        "Migrating hawks kettle over the dunes on northwest winds.",
        "Thousands of tree swallows gather in the marsh before heading south.",
        "White-tailed deer rut in the forest; bucks spar at dawn.",
        "Gray seals return to the outer beaches from Canadian waters.",
        "Sea ducks arrive from the north: eiders, scoters, long-tailed ducks.",
        "Snow geese pass overhead in wavering lines.",
        "Monarch butterflies pause on their long journey to Mexico.",
        "Muskrats busy themselves building winter lodges.",
        "Cranberries float crimson in the harvested bogs.",
        "Late-season stripers make a final push through the sound.",
    ],
    "winter": [
        "Harbor seals pup on the outer sandbars in January.",
        "Snowy owls sometimes visit from the Arctic, hunting the dunes.",
        "Sea ducks raft in the thousands on Plum Island Sound.",
        "Great horned owls begin their courtship hooting in the forest.",
        "Deer gather in yards where snow is shallow.",
        "Red foxes leave their tracks in the snow across the marsh.",
        "Black-capped chickadees flock to backyard feeders.",
        "Bald eagles patrol the open water, looking for weak fish.",
        "Harbor porpoises sometimes chase herring close to shore.",
        "Coyotes howl at night, their voices carrying over the frozen landscape.",
    ],
}

# =============================================================================
# BIRDS BY SEASON - Specific to Essex County / North Shore
# =============================================================================

BIRDS_BY_SEASON = {
    "spring": {
        "returning_migrants": [
            "Osprey return in late March, rebuilding nests on channel markers and platforms",
            "Tree swallows arrive early, competing for nest boxes at Appleton Farms",
            "Baltimore orioles appear when the apple trees bloom, weaving pendulous nests",
            "Ruby-throated hummingbirds return to feeders and beach plum blossoms",
            "Barn swallows sweep into the farm buildings of Linebrook",
            "Chimney swifts return to roost in old chimneys downtown",
        ],
        "shorebirds": [
            "Piping plovers establish territories at Crane Beach by late April",
            "Least terns begin their noisy colonies on the sandy upper beach",
            "American oystercatchers probe the mudflats with their orange bills",
            "Semipalmated plovers and sandpipers pause during northward migration",
            "Greater and lesser yellowlegs feed in the marsh pools",
        ],
        "warblers": [
            "Yellow warblers sing from the willows along the Riverwalk",
            "Yellow-rumped warblers pass through in waves during May",
            "Common yellowthroats call 'witchity-witchity' from the marsh edges",
            "Pine warblers trill from Willowdale's pine groves",
        ],
        "year_round_notes": "Great blue herons return to rookeries; red-tailed hawks circle over Appleton Farms",
    },
    "summer": {
        "nesting": [
            "Piping plover chicks run like cotton balls on the beach",
            "Least tern parents dive-bomb anyone who approaches their nests",
            "Osprey feed their growing young on fish from the sound",
            "Saltmarsh sparrows nest secretly in the cordgrass",
            "Willets stand sentinel on marsh hummocks, crying loudly at intruders",
        ],
        "herons_egrets": [
            "Great egrets stalk the marsh creeks in elegant white",
            "Snowy egrets shuffle their yellow feet to stir up prey",
            "Black-crowned night herons emerge at dusk to hunt",
            "Green herons crouch motionless along the riverbanks",
            "Glossy ibis probe the mudflats with curved bills",
        ],
        "beach_birds": [
            "Common and least terns plunge for sand eels offshore",
            "Laughing gulls fill the summer air with their calls",
            "Double-crested cormorants dry their wings on channel markers",
        ],
        "year_round_notes": "Purple martins gather in pre-migration roosts; nighthawks appear over downtown at dusk",
    },
    "autumn": {
        "hawk_migration": [
            "Sharp-shinned hawks stream over the dunes on northwest winds",
            "Cooper's hawks hunt the bird feeders of residential neighborhoods",
            "Broad-winged hawks kettle by the thousands in mid-September",
            "Merlins dash through flocks of shorebirds at the beach",
            "Northern harriers quarter low over the marsh, tilting side to side",
            "Peregrine falcons pause at Crane Beach during migration",
        ],
        "waterfowl_arriving": [
            "Green-winged teal gather in marsh pools",
            "Northern pintails arrive with their elegant long tails",
            "American black ducks increase as northern birds move south",
            "Buffleheads and goldeneyes appear on the river by November",
        ],
        "sparrows": [
            "White-throated sparrows return with their plaintive 'Old Sam Peabody' song",
            "Song sparrows sing from every thicket",
            "Savannah sparrows feed in the marsh before heading south",
            "Nelson's sparrows skulk in the spartina during migration",
        ],
        "year_round_notes": "Tree swallows gather by the tens of thousands over the marsh before departing; monarch butterflies share their flyway",
    },
    "winter": {
        "sea_ducks": [
            "Common eiders raft in huge flocks off Crane Beach",
            "White-winged, surf, and black scoters dive beyond the breakers",
            "Long-tailed ducks call their yodeling song from the sound",
            "Buffleheads bob like corks in the sheltered coves",
            "Red-breasted mergansers fish the tidal creeks",
            "Common goldeneyes whistle overhead with each wingbeat",
        ],
        "raptors": [
            "Snowy owls sometimes appear on the dunes, visitors from the Arctic",
            "Short-eared owls hunt the marsh at dusk, mothlike and silent",
            "Rough-legged hawks hover over the open fields",
            "Bald eagles patrol the open water where waterfowl concentrate",
            "Great horned owls begin courtship hooting in January",
        ],
        "winter_finches": [
            "Some years bring irruptions of pine siskins and redpolls from the north",
            "Purple finches visit feeders alongside house finches",
            "American goldfinches in drab winter plumage flock to thistle feeders",
            "Dark-eyed juncos scratch under feeders throughout the season",
        ],
        "specialties": [
            "Harlequin ducks sometimes appear on the rocky jetties",
            "King eiders occasionally mix with common eider flocks",
            "Barrow's goldeneye is a rare prize among the commons",
            "Iceland and glaucous gulls visit from the north",
        ],
        "year_round_notes": "Harbor seals pup on sandbars; great black-backed gulls dominate the beaches",
    },
}

# =============================================================================
# ASTRONOMY BY SEASON - Night sky from Ipswich latitude (42.7°N)
# =============================================================================

ASTRONOMY_BY_SEASON = {
    "spring": {
        "constellations": [
            "Leo the Lion dominates the southern sky, with bright Regulus marking his heart",
            "The Big Dipper stands high overhead, its pointer stars leading to Polaris",
            "Virgo rises in the east, her bright star Spica heralding warmer nights",
            "Boötes the Herdsman follows with orange Arcturus, the brightest star of spring",
        ],
        "planets_events": [
            "The spring equinox brings equal day and night around March 20",
            "The Lyrid meteor shower peaks in late April",
            "Venus often shines as the evening star in western twilight",
        ],
        "moon_notes": "The full moon nearest the equinox is the Worm Moon or Sap Moon",
        "viewing_notes": "Spring nights can be hazy, but the lengthening evenings offer more stargazing time after dinner",
    },
    "summer": {
        "constellations": [
            "The Summer Triangle rises: Vega in Lyra, Deneb in Cygnus, Altair in Aquila",
            "Scorpius crawls low along the southern horizon, red Antares its heart",
            "The Milky Way arches overhead on moonless nights, from Sagittarius to Cassiopeia",
            "Cygnus the Swan flies along the river of stars",
        ],
        "planets_events": [
            "The summer solstice brings the longest day around June 21",
            "The Perseid meteor shower peaks in mid-August, often the year's best",
            "Noctilucent clouds sometimes glow blue in the north after sunset",
            "Jupiter and Saturn often dominate the summer evening sky",
        ],
        "moon_notes": "The full Strawberry Moon in June; the Sturgeon Moon in August",
        "viewing_notes": "Warm nights make beach stargazing pleasant; the marsh provides dark skies away from town lights",
    },
    "autumn": {
        "constellations": [
            "The Great Square of Pegasus marks the autumn sky",
            "Andromeda stretches from Pegasus, her galaxy visible as a fuzzy patch to dark-adapted eyes",
            "Cassiopeia's W shape wheels higher in the north",
            "The Pleiades rise in the east, the Seven Sisters heralding winter",
            "Fomalhaut shines lonely and bright in the southern sky",
        ],
        "planets_events": [
            "The autumn equinox brings equal day and night around September 22",
            "The Orionid meteors peak in late October",
            "The Leonid meteors peak in mid-November",
            "Mars, when in opposition, blazes red among the stars",
        ],
        "moon_notes": "The Harvest Moon rises near sunset for several nights; the Hunter's Moon follows in October",
        "viewing_notes": "Crisp autumn nights offer excellent seeing; the earlier darkness invites stargazing before bed",
    },
    "winter": {
        "constellations": [
            "Orion the Hunter strides across the southern sky, unmistakable with his belt of three stars",
            "Sirius, the brightest star, blazes below Orion in Canis Major",
            "The Winter Hexagon connects six bright stars: Sirius, Procyon, Pollux, Capella, Aldebaran, Rigel",
            "Taurus the Bull faces Orion, red Aldebaran his eye, the Pleiades on his shoulder",
            "Gemini's twins Castor and Pollux stand high in the east",
            "Auriga the Charioteer rides near the zenith, bright Capella his beacon",
        ],
        "planets_events": [
            "The winter solstice brings the longest night around December 21",
            "The Geminid meteor shower in mid-December rivals the Perseids",
            "The Quadrantid meteors peak in early January",
            "Venus often appears as the morning star before dawn",
        ],
        "moon_notes": "The Cold Moon or Long Night Moon; the Wolf Moon in January",
        "viewing_notes": "Winter offers the clearest, steadiest skies, though cold limits viewing time; Orion is visible all night",
    },
}

# =============================================================================
# MARINE LIFE BY SEASON
# =============================================================================

MARINE_LIFE_BY_SEASON = {
    "spring": [
        "Alewives and river herring run up the Ipswich River to spawn in ancestral ponds",
        "Striped bass arrive from the south, following the warming water",
        "Horseshoe crabs crawl onto beaches under May and June full moons to spawn",
        "Lobsters move inshore as waters warm",
        "Winter flounder spawn in the estuary before heading to deeper water",
    ],
    "summer": [
        "Bluefish slash through schools of menhaden, driving them to the surface",
        "Harbor seals haul out on sandbars at low tide",
        "Moon jellyfish pulse through the warm shallows",
        "Blue crabs reach the northern edge of their range in warm years",
        "Squid move inshore to spawn, attracting striped bass",
        "Sand eels swarm, feeding terns and whales alike",
    ],
    "autumn": [
        "False albacore chase bait along the beaches in September",
        "Striped bass make their fall run, feeding heavily before heading south",
        "Gray seals return from Canadian waters, hauling out on outer bars",
        "Sea scallops are harvested from the deeper waters",
        "Cod move inshore as waters cool",
    ],
    "winter": [
        "Harbor seals pup on remote sandbars in January and February",
        "Gray seals dominate the outer beaches, their numbers growing each year",
        "Harp seals occasionally wander south in cold winters",
        "Cod fishing peaks in the cold months",
        "Sea ducks dive for mussels and crabs in the frigid water",
        "Right whales sometimes pass offshore during their migration",
    ],
}

# =============================================================================
# SEASONAL CHARACTERISTICS
# =============================================================================

SEASONAL_CHARACTER = {
    "spring": {
        "feel": "A time of patience and hope along the coast. The land thaws slowly; "
                "the sea remains cold. The marsh greens up before the upland trees leaf out. "
                "Mornings can be raw with fog, but the lengthening days carry promise.",
        "light": "The light grows stronger but remains soft, filtered through maritime haze.",
        "sounds": "Red-winged blackbirds call from the cattails; peepers chorus at night.",
        "smells": "The thawing earth, salt from the marshes, and the first lawn mowings.",
    },
    "summer": {
        "feel": "The season of abundance and crowds. Long days, warm nights, the beach full "
                "of families. The marsh hums with life. Thunderstorms build over the inland "
                "hills and sweep toward the coast. The greenhead flies test everyone's patience.",
        "light": "The summer light is bright and hot, softened by afternoon sea breezes.",
        "sounds": "Children at the beach, boat engines, the evening chorus of insects.",
        "smells": "Sunscreen, salt air, beach roses, and fried clams.",
    },
    "autumn": {
        "feel": "The turning time. The crowds depart; the locals reclaim their town. "
                "The light slants lower, the shadows lengthen, the marsh turns to gold. "
                "There is a bittersweet quality to the days, a sense of gathering in.",
        "light": "The autumn light is golden and clear, the blue sky deep.",
        "sounds": "Migrating geese honk overhead; wind rustles the dry marsh grass.",
        "smells": "Fallen leaves, wood smoke, the salt marsh at low tide.",
    },
    "winter": {
        "feel": "A time of stark beauty and quiet. The summer people are gone; "
                "the town belongs to those who stay. The beach is empty, the marsh frozen. "
                "Nor'easters bring drama; calm days bring a deep, cold peace.",
        "light": "The winter light is low and pale, the shadows long.",
        "sounds": "Wind in bare branches, surf on the winter beach, ice cracking at tide change.",
        "smells": "Wood smoke, cold salt air, snow.",
    },
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_locations_by_category(category: str) -> List[Location]:
    """Return all locations of a given category."""
    all_locations = NEIGHBORHOODS + NATURAL_FEATURES
    return [loc for loc in all_locations if loc.category == category]


def get_location_by_name(name: str) -> Location | None:
    """Find a location by name (case-insensitive partial match)."""
    all_locations = NEIGHBORHOODS + NATURAL_FEATURES
    name_lower = name.lower()
    for loc in all_locations:
        if name_lower in loc.name.lower():
            return loc
    return None


def get_seasonal_wildlife(season: str) -> List[str]:
    """Return wildlife observations for a given season."""
    return WILDLIFE_BY_SEASON.get(season.lower(), [])


def get_seasonal_character(season: str) -> Dict[str, str]:
    """Return the character/feel of a given season."""
    return SEASONAL_CHARACTER.get(season.lower(), {})


def get_random_historical_fact() -> Dict[str, str]:
    """Return a random historical fact."""
    import random
    return random.choice(HISTORICAL_FACTS)


def get_historical_facts_by_topic(topic: str) -> List[Dict[str, str]]:
    """Return historical facts matching a topic keyword."""
    topic_lower = topic.lower()
    return [f for f in HISTORICAL_FACTS if topic_lower in f["topic"].lower()]


def build_knowledge_context(season: str) -> str:
    """
    Build a comprehensive knowledge context string for story generation.

    This provides the LLM with deep background on Ipswich for a given season.
    """
    all_locations = NEIGHBORHOODS + NATURAL_FEATURES
    seasonal_char = get_seasonal_character(season)
    wildlife = get_seasonal_wildlife(season)

    context_parts = []

    # CRITICAL: Geographic layout first - this prevents spatial errors
    context_parts.append(GEOGRAPHIC_LAYOUT)

    # Seasonal feel
    context_parts.append(f"## The Season\n{seasonal_char.get('feel', '')}")
    context_parts.append(f"Light: {seasonal_char.get('light', '')}")
    context_parts.append(f"Sounds: {seasonal_char.get('sounds', '')}")
    context_parts.append(f"Scents: {seasonal_char.get('smells', '')}")

    # Key locations with seasonal notes
    context_parts.append("\n## Notable Places")
    for loc in all_locations[:12]:  # Increased limit for richer context
        seasonal_note = loc.seasonal_notes.get(season.lower(), "")
        context_parts.append(f"- **{loc.name}**: {loc.description[:200]}... "
                           f"In {season}: {seasonal_note}")

    # Wildlife
    context_parts.append("\n## Wildlife This Season")
    for observation in wildlife[:5]:
        context_parts.append(f"- {observation}")

    # Birds - detailed by category
    season_lower = season.lower()
    if season_lower in BIRDS_BY_SEASON:
        birds = BIRDS_BY_SEASON[season_lower]
        context_parts.append("\n## Birds This Season")
        # Pick a few from each category
        for category, items in birds.items():
            if isinstance(items, list) and items:
                context_parts.append(f"- {items[0]}")  # First item from each category
        if "year_round_notes" in birds:
            context_parts.append(f"- {birds['year_round_notes']}")

    # Marine life
    if season_lower in MARINE_LIFE_BY_SEASON:
        context_parts.append("\n## Marine Life This Season")
        for observation in MARINE_LIFE_BY_SEASON[season_lower][:3]:
            context_parts.append(f"- {observation}")

    # Astronomy
    if season_lower in ASTRONOMY_BY_SEASON:
        astro = ASTRONOMY_BY_SEASON[season_lower]
        context_parts.append("\n## Night Sky This Season")
        for constellation in astro.get("constellations", [])[:2]:
            context_parts.append(f"- {constellation}")
        if "moon_notes" in astro:
            context_parts.append(f"- {astro['moon_notes']}")
        if "viewing_notes" in astro:
            context_parts.append(f"- {astro['viewing_notes']}")

    # Ipswich River conditions
    if season_lower in IPSWICH_RIVER_ECOLOGY.get("seasonal_flow", {}):
        river = IPSWICH_RIVER_ECOLOGY["seasonal_flow"][season_lower]
        context_parts.append(f"\n## Ipswich River This Season")
        context_parts.append(f"- Conditions: {river.get('conditions', '')}")
        if "paddling" in river:
            context_parts.append(f"- {river['paddling']}")

    # Local landmarks and businesses (rotating selection)
    context_parts.append("\n## Local Landmarks")
    import random
    businesses = list(LOCAL_BUSINESSES.values())
    random.shuffle(businesses)
    for biz in businesses[:3]:
        context_parts.append(f"- **{biz['name']}** ({biz.get('address', '')}): {biz.get('description', '')[:100]}...")

    # Historical threads (expanded)
    context_parts.append("\n## Historical Threads")
    random.shuffle(HISTORICAL_FACTS)
    for fact in HISTORICAL_FACTS[:5]:
        context_parts.append(f"- **{fact['topic']}**: {fact['content'][:150]}...")

    # Add a historical figure or legend for narrative richness
    figures = list(HISTORICAL_FIGURES.values())
    random.shuffle(figures)
    if figures:
        fig = figures[0]
        context_parts.append(f"\n## Historical Figure: {fig['name']}")
        context_parts.append(f"{fig.get('story', '')[:300]}...")

    # Add a local legend occasionally
    legends = list(LOCAL_LEGENDS.values())
    random.shuffle(legends)
    if legends and random.random() > 0.5:  # 50% chance to include a legend
        leg = legends[0]
        context_parts.append(f"\n## Local Legend: {leg['name']}")
        context_parts.append(f"{leg.get('story', '')[:250]}...")

    return "\n".join(context_parts)
