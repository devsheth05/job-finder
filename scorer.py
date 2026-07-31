"""Turns a normalized job dict into a numeric score + star rating."""
import config


def score_job(job: dict) -> int:
    text = f"{job.get('title', '')} {job.get('description', '')}".lower()
    location = job.get("location", "").lower()

    score = 0

    for kw, weight in config.POSITIVE_KEYWORDS.items():
        if kw in text:
            score += weight

    for kw, weight in config.NEGATIVE_KEYWORDS.items():
        if kw in text:
            score += weight  # weight is already negative

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
