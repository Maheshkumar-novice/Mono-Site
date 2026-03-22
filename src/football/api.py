"""API client for Football-Data.org."""

import logging
import time
from datetime import datetime, timedelta

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://api.football-data.org/v4"
COMPETITION_CODES = ["PL", "PD", "BL1", "SA", "FL1", "CL"]


class FootballAPIClient:
    def __init__(self, api_key):
        self.headers = {"X-Auth-Token": api_key}

    def _get(self, url, params=None, retry=True):
        try:
            resp = requests.get(url, headers=self.headers, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            logger.warning(f"Network error: {e}")
            if retry:
                time.sleep(2)
                return self._get(url, params, retry=False)
            return None
        except Exception as e:
            logger.error(f"API error: {e}")
            return None

    def fetch_recent_matches(self, competition_code, hours=168):
        now = datetime.utcnow()
        date_from = (now - timedelta(hours=hours)).strftime("%Y-%m-%d")
        date_to = now.strftime("%Y-%m-%d")
        url = f"{BASE_URL}/competitions/{competition_code}/matches"
        return self._get(url, params={"dateFrom": date_from, "dateTo": date_to})

    def fetch_top_scorers(self, competition_code, limit=10):
        url = f"{BASE_URL}/competitions/{competition_code}/scorers"
        return self._get(url, params={"limit": limit})

    def fetch_standings(self, competition_code):
        url = f"{BASE_URL}/competitions/{competition_code}/standings"
        return self._get(url)
