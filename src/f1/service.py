"""Service layer for F1 data with SQLite caching."""

import json
import logging
import time
from datetime import datetime, timezone

from src.db import get_db, init_f1_db
from src.f1 import ergast_api

logger = logging.getLogger(__name__)

CACHE_TTL_STANDINGS = 3600   # 1 hour
CACHE_TTL_SCHEDULE = 3600    # 1 hour
CACHE_TTL_RESULTS = 86400    # 24 hours


def _get_cached(key, ttl):
    with get_db("f1.db") as conn:
        row = conn.execute("SELECT data, updated_at FROM cache WHERE key = ?", (key,)).fetchone()
    if row and (time.time() - row["updated_at"]) < ttl:
        return json.loads(row["data"])
    return None


def _set_cached(key, data):
    with get_db("f1.db") as conn:
        conn.execute(
            "INSERT OR REPLACE INTO cache (key, data, updated_at) VALUES (?, ?, ?)",
            (key, json.dumps(data), time.time()),
        )


def _cached_or_fetch(key, ttl, fetch_fn):
    cached = _get_cached(key, ttl)
    if cached is not None:
        return cached
    try:
        data = fetch_fn()
        if data is not None:
            _set_cached(key, data)
            return data
    except Exception as e:
        logger.error("Error fetching %s: %s", key, e)
    # Fall back to stale cache
    with get_db("f1.db") as conn:
        row = conn.execute("SELECT data FROM cache WHERE key = ?", (key,)).fetchone()
    if row:
        logger.info("Using stale cache for %s", key)
        return json.loads(row["data"])
    return None


def get_driver_standings():
    return _cached_or_fetch("driver_standings", CACHE_TTL_STANDINGS, ergast_api.get_driver_standings)


def get_constructor_standings():
    return _cached_or_fetch("constructor_standings", CACHE_TTL_STANDINGS, ergast_api.get_constructor_standings)


def get_schedule():
    return _cached_or_fetch("schedule", CACHE_TTL_SCHEDULE, ergast_api.get_schedule)


def get_last_race():
    return _cached_or_fetch("last_race", CACHE_TTL_RESULTS, ergast_api.get_last_race_result)


def get_recent_results():
    return _cached_or_fetch("recent_results", CACHE_TTL_RESULTS, ergast_api.get_recent_results)


def get_next_race():
    schedule = get_schedule()
    if not schedule:
        return None
    now = datetime.now(timezone.utc)
    for race in schedule:
        race_date_str = race.get("date", "")
        race_time_str = race.get("time", "00:00:00Z")
        try:
            race_dt = datetime.fromisoformat(f"{race_date_str}T{race_time_str}".replace("Z", "+00:00"))
            if race_dt > now:
                return race
        except (ValueError, TypeError):
            continue
    return None


def refresh_all():
    """Pre-fetch and cache all data."""
    init_f1_db()
    logger.info("Refreshing F1 data...")
    get_driver_standings()
    get_constructor_standings()
    get_schedule()
    get_recent_results()
    get_last_race()
    logger.info("F1 refresh complete.")
