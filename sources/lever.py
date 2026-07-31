"""
Direct polling of Lever's public postings API:
    GET https://api.lever.co/v0/postings/{company}?mode=json
Company slug is the one in jobs.lever.co/<company>.
"""
import requests
import config

HEADERS = {"User-Agent": "job-finder-bot/1.0"}
BASE = "https://api.lever.co/v0/postings/{company}"


def _normalize(company: str, entry: dict) -> dict:
    categories = entry.get("categories", {}) or {}
    location = categories.get("location", "Unknown") or "Unknown"
    return {
        "company": company,
        "title": entry.get("text", "Unknown"),
        "location": location,
        "remote": "remote" in location.lower(),
        "posted_date": "",  # Lever doesn't reliably expose a posted date
        "apply_url": entry.get("hostedUrl", ""),
        "source": "Lever",
        "description": (entry.get("descriptionPlain") or "")[:4000],
        "job_id": str(entry.get("id", "")),
    }


def fetch_company(company: str) -> list[dict]:
    try:
        resp = requests.get(
            BASE.format(company=company), params={"mode": "json"},
            headers=HEADERS, timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"[lever:{company}] failed: {e}")
        return []
    return [_normalize(company, job) for job in data]


def fetch_all(companies: list[str] | None = None) -> list[dict]:
    companies = companies or config.LEVER_COMPANIES
    jobs = []
    for company in companies:
        jobs.extend(fetch_company(company))
    return jobs
