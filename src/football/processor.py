"""Data processing and normalization for football match data."""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def normalize_match(match_data, competition_code=None, competition_name=None):
    """Normalize raw API match data into a consistent format."""
    try:
        status = match_data.get("status", "SCHEDULED")
        home_team_data = match_data.get("homeTeam", {})
        away_team_data = match_data.get("awayTeam", {})

        home_team = {"name": home_team_data.get("name", "N/A"), "crest": home_team_data.get("crest", "")}
        away_team = {"name": away_team_data.get("name", "N/A"), "crest": away_team_data.get("crest", "")}

        utc_kickoff = match_data.get("utcDate", "")
        score_text = _format_score(match_data, status)

        score_data = match_data.get("score", {})
        full_time = score_data.get("fullTime", {})

        return {
            "status": status,
            "score_text": score_text,
            "score": {"full_time": {"home": full_time.get("home"), "away": full_time.get("away")}},
            "home_team": home_team,
            "away_team": away_team,
            "utc_kickoff": utc_kickoff,
            "date": _format_display_date(utc_kickoff) if utc_kickoff else "N/A",
            "display_date": _format_display_date(utc_kickoff) if utc_kickoff else "N/A",
            "competition_code": competition_code,
            "competition_name": competition_name,
        }
    except Exception as e:
        logger.warning(f"Error normalizing match: {e}")
        return None


def _format_score(match_data, status):
    if status == "FINISHED":
        ft = match_data.get("score", {}).get("fullTime", {})
        h, a = ft.get("home"), ft.get("away")
        if h is not None and a is not None:
            return f"{h}\u2013{a}"
        return "N/A"
    elif status in ("LIVE", "IN_PLAY"):
        return "LIVE"
    return "SCHEDULED"


def _format_display_date(utc_date_str):
    try:
        dt = datetime.fromisoformat(utc_date_str.replace("Z", "+00:00"))
        return dt.strftime("%a, %b %d")
    except Exception:
        return "N/A"
