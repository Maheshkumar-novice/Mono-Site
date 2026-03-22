"""Ergast API client for F1 data."""

import logging
import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.jolpi.ca/ergast/f1"


def _get(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}.json"
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json().get("MRData", {})
    except requests.RequestException as e:
        logger.error("Ergast API error for %s: %s", endpoint, e)
        return None


def get_driver_standings(season="current"):
    data = _get(f"{season}/driverStandings")
    if not data:
        return []
    tables = data.get("StandingsTable", {}).get("StandingsLists", [])
    return tables[0].get("DriverStandings", []) if tables else []


def get_constructor_standings(season="current"):
    data = _get(f"{season}/constructorStandings")
    if not data:
        return []
    tables = data.get("StandingsTable", {}).get("StandingsLists", [])
    return tables[0].get("ConstructorStandings", []) if tables else []


def get_schedule(season="current"):
    data = _get(f"{season}")
    if not data:
        return []
    return data.get("RaceTable", {}).get("Races", [])


def get_last_race_result(season="current"):
    data = _get(f"{season}/last/results")
    if not data:
        return None
    races = data.get("RaceTable", {}).get("Races", [])
    return races[0] if races else None


def get_recent_results(season="current", limit=3):
    data = _get(f"{season}/results", params={"limit": 1000})
    if not data:
        return []
    races = data.get("RaceTable", {}).get("Races", [])
    return races[-limit:] if races else []
