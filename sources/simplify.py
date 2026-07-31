"""
Pulls SimplifyJobs' community-maintained New-Grad / Internship repos.
These repos publish a structured JSON feed (not just a markdown table),
updated continuously by their own bots, so we consume it directly rather
than re-scraping GitHub's markdown.
"""
from datetime import datetime, timezone
import requests
import config

HEADERS = {"User-Agent": "job-finder-bot/1.0"}


def _fetch(url: str) -> list[dict]:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _normalize(entry: dict, label: str) -> dict:
    locations = entry.get("locations") or ["Unknown"]
    location_str = "; ".join(locations)
    remote = any("remote" in loc.lower() for loc in locations)

    posted_ts = entry.get("date_posted")
    posted_date = (
        datetime.fromtimestamp(posted_ts, tz=timezone.utc).strftime("%Y-%m-%d")
        if posted_ts else ""
    )

    return {
        "company": entry.get("company_name", "Unknown"),
        "title": entry.get("title", "Unknown"),
        "location": location_str,
        "remote": remote,
        "posted_date": posted_date,
        "apply_url": entry.get("url", ""),
        "source": f"Simplify-{label}",
        "description": entry.get("title", ""),  # repo doesn't expose full JD
        "job_id": entry.get("id", ""),
    }


def fetch_new_grad() -> list[dict]:
    try:
        raw = _fetch(config.SIMPLIFY_NEW_GRAD_URL)
    except requests.RequestException as e:
        print(f"[simplify] new-grad feed failed: {e}")
        return []
    return [_normalize(e, "NewGrad") for e in raw if e.get("active", True)]


def fetch_internships() -> list[dict]:
    try:
        raw = _fetch(config.SIMPLIFY_INTERNSHIP_URL)
    except requests.RequestException as e:
        print(f"[simplify] internship feed failed: {e}")
        return []
    return [_normalize(e, "Internship") for e in raw if e.get("active", True)]


def fetch_all() -> list[dict]:
    return fetch_new_grad() + fetch_internships()
