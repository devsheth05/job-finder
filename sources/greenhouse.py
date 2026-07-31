"""
Direct polling of Greenhouse's public job-board API, one call per company:
    GET https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true
No API key needed -- this is the same data the public careers page renders
from. Company 'token' is the slug in boards.greenhouse.io/<token>.
"""
import requests
import config

HEADERS = {"User-Agent": "job-finder-bot/1.0"}
BASE = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs"


def _normalize(company_token: str, entry: dict) -> dict:
    location = (entry.get("location") or {}).get("name", "Unknown")
    return {
        "company": company_token,
        "title": entry.get("title", "Unknown"),
        "location": location,
        "remote": "remote" in location.lower(),
        "posted_date": (entry.get("updated_at") or "")[:10],
        "apply_url": entry.get("absolute_url", ""),
        "source": "Greenhouse",
        "description": entry.get("content", "") or "",
        "job_id": str(entry.get("id", "")),
    }


def fetch_company(token: str) -> list[dict]:
    try:
        resp = requests.get(
            BASE.format(token=token), params={"content": "true"},
            headers=HEADERS, timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"[greenhouse:{token}] failed: {e}")
        return []
    return [_normalize(token, job) for job in data.get("jobs", [])]


def fetch_all(companies: list[str] | None = None) -> list[dict]:
    companies = companies or config.GREENHOUSE_COMPANIES
    jobs = []
    for token in companies:
        jobs.extend(fetch_company(token))
    return jobs
