"""
Auto-discovers which companies use Greenhouse/Lever/Ashby by scanning the
apply URLs already present in Simplify's feeds. This replaces a hand-maintained
company list with one that grows/shrinks on its own as companies post jobs.
"""
import re
import requests
import config

HEADERS = {"User-Agent": "job-finder-bot/1.0"}

PATTERNS = {
    "greenhouse": re.compile(r"(?:job-boards|boards)\.greenhouse\.io/([a-zA-Z0-9\-]+)"),
    "lever": re.compile(r"jobs\.lever\.co/([a-zA-Z0-9\-]+)"),
    "ashby": re.compile(r"jobs\.ashbyhq\.com/([a-zA-Z0-9\-]+)"),
}


def _fetch_urls() -> list[str]:
    urls = []
    for feed in (config.SIMPLIFY_NEW_GRAD_URL, config.SIMPLIFY_INTERNSHIP_URL):
        try:
            data = requests.get(feed, headers=HEADERS, timeout=30).json()
            urls += [e.get("url", "") for e in data if e.get("active", True)]
        except requests.RequestException as e:
            print(f"[discover] failed to fetch {feed}: {e}")
    return urls


def discover_companies() -> dict:
    """Returns {'greenhouse': {...}, 'lever': {...}, 'ashby': {...}} of slugs."""
    blob = " ".join(_fetch_urls())
    found = {ats: set(pattern.findall(blob)) for ats, pattern in PATTERNS.items()}

    # merge with the manually curated seed lists so nothing is lost
    found["greenhouse"] |= set(config.GREENHOUSE_COMPANIES)
    found["lever"] |= set(config.LEVER_COMPANIES)
    found["ashby"] |= set(config.ASHBY_COMPANIES)

    for ats, companies in found.items():
        print(f"[discover] {ats}: {len(companies)} companies")

    return found