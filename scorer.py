"""Turns a normalized job dict into a numeric score + star rating."""
import config


def score_job(job: dict) -> int:
    title = job.get("title", "").lower()
    location = job.get("location", "").lower()

    # Hard exclude non-technical functions, checked on title only
    if any(kw in title for kw in config.HARD_EXCLUDE_TITLE_KEYWORDS):
        return -1000

    score = 0

    # Positive/negative keywords matched on TITLE only -- avoids false
    # positives from generic company boilerplate in the description
    for kw, weight in config.POSITIVE_KEYWORDS.items():
        if kw in title:
            score += weight

    for kw, weight in config.NEGATIVE_KEYWORDS.items():
        if kw in title:
            score += weight

    if job.get("remote"):
        score += config.LOCATION_TIERS["remote"]["score"]

    for tier_key in (1, 2):
        tier = config.LOCATION_TIERS[tier_key]
        if any(place in location for place in tier["places"]):
            score += tier["score"]
            break

    return score


def stars(score: int) -> int:
    for minimum, star_count in config.STAR_BANDS:
        if score >= minimum:
            return star_count
    return 1


def passes_threshold(score: int) -> bool:
    return score >= config.SCORE_THRESHOLD
