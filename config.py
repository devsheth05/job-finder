"""
Central configuration: what to search for, where, and how to score it.
Edit this file to tune the job hunt without touching the crawler logic.
"""

# ---------------------------------------------------------------------------
# SCORING KEYWORDS
# Matched (case-insensitive) against the job title (weighted higher) and
# description (weighted lower). Tune freely.
# ---------------------------------------------------------------------------

POSITIVE_KEYWORDS = {
    # role-level signals
    "new grad": 40, "university grad": 40, "campus": 35, "early career": 35,
    "entry level": 35, "entry-level": 35, "associate": 20,
    "software engineer i": 30, "swe i": 30, "software engineer 1": 30,
    # discipline
    "backend": 15, "back-end": 15, "frontend": 12, "front-end": 12,
    "full stack": 15, "full-stack": 15, "platform": 12, "infrastructure": 15,
    "distributed systems": 15, "cloud": 10, "ai": 10, "machine learning": 12,
    "ml engineer": 15,
}

NEGATIVE_KEYWORDS = {
    "senior": -100, "sr.": -100, "staff": -100, "principal": -100,
    "lead ": -80, "manager": -100, "director": -100, "architect": -60,
    "vp ": -100, "vice president": -100, "5+ years": -80, "7+ years": -100,
    "8+ years": -100, "10+ years": -100, "phd required": -40,
}

# Location tiers -> score bonus. Matched against the job's location string(s).
LOCATION_TIERS = {
    1: {  # +30
        "score": 30,
        "places": [
            "seattle", "bellevue", "redmond", "bay area", "san francisco",
            "san jose", "sunnyvale", "mountain view", "palo alto",
            "santa clara", "menlo park", "new york", "brooklyn", "nyc",
        ],
    },
    2: {  # +18
        "score": 18,
        "places": [
            "austin", "boston", "chicago", "los angeles", "irvine",
            "san diego", "denver",
        ],
    },
    "remote": {"score": 20, "places": ["remote"]},
}

SCORE_THRESHOLD = 10  # jobs below this score are dropped, not written to the sheet

STAR_BANDS = [(95, 5), (80, 4), (60, 3), (40, 2), (0, 1)]  # (min_score, stars)

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------

# 1) Simplify's New Grad repo already aggregates hundreds of ATS postings into
#    one structured JSON feed. We treat it as a first-class source.
SIMPLIFY_NEW_GRAD_URL = (
    "https://raw.githubusercontent.com/SimplifyJobs/New-Grad-Positions/"
    "dev/.github/scripts/listings.json"
)
# Same project also maintains a Summer Internship repo with the same format.
SIMPLIFY_INTERNSHIP_URL = (
    "https://raw.githubusercontent.com/SimplifyJobs/Summer2026-Internships/"
    "dev/.github/scripts/listings.json"
)

# 2) Direct ATS polling for a curated seed list of companies. This catches
#    postings the moment they go live, independent of Simplify's own refresh
#    cadence. Add/remove company slugs freely -- find a slug by opening a
#    company's careers page and reading the URL, e.g.
#      https://boards.greenhouse.io/stripe          -> "stripe"
#      https://jobs.lever.co/figma                  -> "figma"
#      https://jobs.ashbyhq.com/ramp                -> "ramp"
GREENHOUSE_COMPANIES = [
    "stripe", "airbnb", "coinbase", "robinhood", "doordash", "affirm",
    "figma", "databricks", "snowflake", "reddit", "asana", "gitlab",
    "cloudflare", "confluent", "instacart", "pinterest", "roblox",
    "brex", "discord", "notion",
]

LEVER_COMPANIES = [
    "netflix", "shopify", "palantir", "plaid", "rippling", "attentive",
    "gusto", "front", "buildbuzz", "loom",
]

ASHBY_COMPANIES = [
    "ramp", "linear", "vanta", "mercury", "openai", "anthropic", "deel",
    "assemblyai", "modal", "watershed",
]

# ---------------------------------------------------------------------------
# GOOGLE SHEETS
# ---------------------------------------------------------------------------

GOOGLE_SHEET_NAME = "Job Search Tracker"
GOOGLE_WORKSHEET_NAME = "Jobs"
SERVICE_ACCOUNT_FILE = "service_account.json"  # path to your downloaded key

SHEET_HEADERS = [
    "Company", "Title", "Location", "Remote", "Posted", "First Seen",
    "Score", "Stars", "Apply Link", "Source(s)", "Status", "Notes",
]

DB_PATH = "jobs.db"
