"""Service layer for fetching and storing football data."""

import json
import logging
import time
from datetime import datetime

from src.db import get_db, init_football_db
from src.football.api import FootballAPIClient, COMPETITION_CODES
from src.football.processor import normalize_match

logger = logging.getLogger(__name__)

RATE_LIMIT_SECONDS = 7


def _save(table, competition_code, data):
    with get_db("football.db") as conn:
        conn.execute(
            f"INSERT OR REPLACE INTO {table} (competition_code, data_json, updated_at) VALUES (?, ?, ?)",
            (competition_code, json.dumps(data), datetime.utcnow().isoformat()),
        )


def _load_all(table):
    with get_db("football.db") as conn:
        rows = conn.execute(f"SELECT competition_code, data_json FROM {table}").fetchall()
        return {row["competition_code"]: json.loads(row["data_json"]) for row in rows}


def refresh_data(api_key):
    """Fetch fresh data from football-data.org and store in SQLite."""
    init_football_db()
    client = FootballAPIClient(api_key)

    # Matches
    for code in COMPETITION_CODES:
        try:
            resp = client.fetch_recent_matches(code, hours=168)
            time.sleep(RATE_LIMIT_SECONDS)
            if resp:
                matches = resp.get("matches", [])
                comp_name = resp.get("competition", {}).get("name", code)
                normalized = [m for m in (normalize_match(m, code, comp_name) for m in matches) if m]
                _save("matches", code, normalized)
                logger.info(f"Matches {code}: {len(normalized)}")
        except Exception as e:
            logger.error(f"Matches {code} failed: {e}")

    # Scorers
    for code in COMPETITION_CODES:
        try:
            resp = client.fetch_top_scorers(code)
            if resp:
                _save("scorers", code, resp.get("scorers", []))
                logger.info(f"Scorers {code}: OK")
            time.sleep(RATE_LIMIT_SECONDS)
        except Exception as e:
            logger.error(f"Scorers {code} failed: {e}")

    # Standings
    for code in COMPETITION_CODES:
        try:
            resp = client.fetch_standings(code)
            if resp:
                standings_list = resp.get("standings", [])
                total = next((s for s in standings_list if s.get("type") == "TOTAL"), None)
                if total:
                    _save("standings", code, total.get("table", []))
                    logger.info(f"Standings {code}: OK")
            time.sleep(RATE_LIMIT_SECONDS)
        except Exception as e:
            logger.error(f"Standings {code} failed: {e}")


def get_all_matches():
    data = _load_all("matches")
    for code in data:
        data[code].sort(key=lambda m: m.get("utc_kickoff", ""), reverse=True)
    return data


def get_all_scorers():
    return _load_all("scorers")


def get_all_standings():
    return _load_all("standings")
