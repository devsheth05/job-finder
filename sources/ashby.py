"""
Direct polling of Ashby's public job-board API:
    GET https://api.ashbyhq.com/posting-api/job-board/{company}
Company slug is the one in jobs.ashbyhq.com/<company>.
"""
import requests
import config

HEADERS = {"User-Agent": "job-finder-bot/1.0"}
BASE = "https://api.ashbyhq.com/posting-api/job-board/{company}"


def _normalize(company: str, entry: dict) -> dict:
    location = entry.get("location", "Unknown") or "Unknown"
    return {
        "company": company,
        "title": entry.get("title", "Unknown"),
        "location": location,
        "remote": bool(entry.get("isRemote", False)),
        "posted_date": (entry.get("publishedAt") or "")[:10],
        "apply_url": entry.get("jobUrl", ""),
        "source": "Ashby",
        "description": (entry.get("descriptionPlain") or "")[:4000],
        "job_id": str(entry.get("id", "")),
    }


def fetch_company(company: str) -> list[dict]:
    try:
        resp = requests.get(BASE.format(company=company), headers=HEADERS, timeout=20)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"[ashby:{company}] failed: {e}")
        return []
    return [_normalize(company, job) for job in data.get("jobs", [])]


def fetch_all(companies: list[str] | None = None) -> list[dict]:
    companies = companies or config.ASHBY_COMPANIES
    jobs = []
    for company in companies:
        jobs.extend(fetch_company(company))
    return jobs
