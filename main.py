"""
Entry point. Runs all sources, scores + dedupes results, writes new jobs to
the DB, and syncs anything not-yet-synced to Google Sheets.

Usage:
    python main.py              # full run, syncs to Google Sheets
    python main.py --no-sheets  # local test run, skips Sheets (prints instead)
"""
import argparse
import sys
from datetime import datetime, timezone

import config
import database
import scorer
from sources import simplify, greenhouse, lever, ashby, discover

def gather_all_jobs() -> list[dict]:
    jobs = []
    print("Fetching Simplify feeds (New Grad + Internships)...")
    jobs += simplify.fetch_all()
    print(f"  -> {len(jobs)} so far")

    print("Discovering companies from Simplify's own listings...")
    discovered = discover.discover_companies()

    print("Polling Greenhouse boards...")
    jobs += greenhouse.fetch_all(sorted(discovered["greenhouse"]))
    print(f"  -> {len(jobs)} so far")

    print("Polling Lever boards...")
    jobs += lever.fetch_all(sorted(discovered["lever"]))
    print(f"  -> {len(jobs)} so far")

    print("Polling Ashby boards...")
    jobs += ashby.fetch_all(sorted(discovered["ashby"]))
    print(f"  -> {len(jobs)} so far")

    return jobs

def build_sheet_row(record, sources_str: str) -> list:
    stars_str = "★" * scorer.stars(record["score"])
    return [
        record["company"], record["title"], record["location"],
        "Yes" if record["remote"] else "No", record["posted_date"] or "",
        record["first_seen"][:10], record["score"], stars_str,
        record["apply_url"], sources_str, record["status"] or "New",
        record["notes"] or "",
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-sheets", action="store_true", help="skip Google Sheets sync")
    args = parser.parse_args()

    conn = database.connect()
    raw_jobs = gather_all_jobs()
    print(f"\nFetched {len(raw_jobs)} raw postings across all sources.")

    new_count, seen_count, dropped_count = 0, 0, 0
    for job in raw_jobs:
        score = scorer.score_job(job)
        if not scorer.passes_threshold(score):
            dropped_count += 1
            continue
        is_new, _ = database.upsert_job(conn, job, score)
        new_count += is_new
        seen_count += not is_new

    print(f"New: {new_count} | Already tracked: {seen_count} | Below score threshold: {dropped_count}")

    unsynced = database.get_unsynced(conn)
    if not unsynced:
        print("Nothing new to sync.")
        return

    cols = database.column_names(conn)
    records = [dict(zip(cols, row)) for row in unsynced]

    if args.no_sheets:
        print(f"\n[--no-sheets] Would sync {len(records)} rows:")
        for r in records[:20]:
            print(f"  {'★'*scorer.stars(r['score'])} {r['company']} - {r['title']} ({r['location']}) [{r['score']}]")
        if len(records) > 20:
            print(f"  ... and {len(records) - 20} more")
        return

    import sheets_sync
    ws = sheets_sync.get_worksheet()
    rows = [build_sheet_row(r, r["sources"]) for r in records]
    sheets_sync.append_jobs(ws, rows)
    database.mark_synced(conn, [r["fingerprint"] for r in records])

    print(f"\nSynced {len(rows)} new jobs to Google Sheet '{config.GOOGLE_SHEET_NAME}'.")
    top = sorted(records, key=lambda r: r["score"], reverse=True)[:5]
    if top:
        print("\nTop matches this run:")
        for r in top:
            print(f"  {'★'*scorer.stars(r['score'])} {r['company']} - {r['title']} ({r['location']})")

    print(f"\nDone at {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    sys.exit(main())
