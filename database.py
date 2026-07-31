"""
SQLite storage for every job ever seen. This is what makes deduplication and
'first seen' tracking possible across runs, and doubles as a historical
dataset over time (which companies hire when, how long postings stay open).
"""
import hashlib
import sqlite3
from datetime import datetime, timezone

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    fingerprint   TEXT PRIMARY KEY,
    company       TEXT NOT NULL,
    title         TEXT NOT NULL,
    location      TEXT,
    remote        INTEGER DEFAULT 0,
    posted_date   TEXT,
    first_seen    TEXT NOT NULL,
    last_seen     TEXT NOT NULL,
    score         INTEGER,
    apply_url     TEXT,
    sources       TEXT,
    status        TEXT DEFAULT 'New',
    notes         TEXT DEFAULT '',
    active        INTEGER DEFAULT 1,
    synced_to_sheet INTEGER DEFAULT 0
);
"""


def fingerprint(company: str, title: str, location: str) -> str:
    """A stable hash so the same job from two different sources collapses to
    one row, e.g. Greenhouse + Simplify both surfacing 'Stripe / SWE Intern'."""
    key = f"{company.strip().lower()}|{title.strip().lower()}|{location.strip().lower()}"
    return hashlib.sha256(key.encode()).hexdigest()[:24]


def connect(path: str = config.DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute(SCHEMA)
    conn.commit()
    return conn


def upsert_job(conn: sqlite3.Connection, job: dict, score: int) -> tuple[bool, str]:
    """Insert a new job or merge into an existing one (adds source, refreshes
    last_seen). Returns (is_new, fingerprint)."""
    fp = fingerprint(job["company"], job["title"], job.get("location", ""))
    now = datetime.now(timezone.utc).isoformat()

    row = conn.execute("SELECT sources FROM jobs WHERE fingerprint = ?", (fp,)).fetchone()

    if row is None:
        conn.execute(
            """INSERT INTO jobs
               (fingerprint, company, title, location, remote, posted_date,
                first_seen, last_seen, score, apply_url, sources, active)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,1)""",
            (
                fp, job["company"], job["title"], job.get("location", ""),
                int(job.get("remote", False)), job.get("posted_date", ""),
                now, now, score, job.get("apply_url", ""), job.get("source", ""),
            ),
        )
        conn.commit()
        return True, fp

    existing_sources = set(filter(None, (row[0] or "").split(", ")))
    existing_sources.add(job.get("source", ""))
    conn.execute(
        """UPDATE jobs SET last_seen = ?, sources = ?, active = 1 WHERE fingerprint = ?""",
        (now, ", ".join(sorted(existing_sources)), fp),
    )
    conn.commit()
    return False, fp


def get_unsynced(conn: sqlite3.Connection):
    return conn.execute(
        "SELECT * FROM jobs WHERE synced_to_sheet = 0 ORDER BY score DESC"
    ).fetchall()


def mark_synced(conn: sqlite3.Connection, fingerprints: list[str]):
    conn.executemany(
        "UPDATE jobs SET synced_to_sheet = 1 WHERE fingerprint = ?",
        [(fp,) for fp in fingerprints],
    )
    conn.commit()


def column_names(conn: sqlite3.Connection) -> list[str]:
    return [d[1] for d in conn.execute("PRAGMA table_info(jobs)").fetchall()]
