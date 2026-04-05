"""Build static HTML for the football page."""

import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

from src.db import init_football_db
from src.football.api import COMPETITION_CODES
from src.football.service import get_all_matches, get_all_scorers, get_all_standings, refresh_data

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
BUILD_DIR = Path(os.environ.get("MONO_BUILD_DIR", PROJECT_DIR / "build")) / "football"
TEMPLATES_DIR = PROJECT_DIR / "templates"

COMPETITION_NAMES = {
    "PL": "Premier League",
    "PD": "La Liga",
    "BL1": "Bundesliga",
    "SA": "Serie A",
    "FL1": "Ligue 1",
    "CL": "Champions League",
}


def build():
    load_dotenv(PROJECT_DIR / ".env")
    init_football_db()

    api_key = os.getenv("FOOTBALL_API_KEY")
    if not api_key:
        logger.error(
            "FOOTBALL_API_KEY not set. Skipping football build (using cached data if available)."
        )
    else:
        logger.info("Fetching football data...")
        refresh_data(api_key)

    matches = get_all_matches()
    scorers = get_all_scorers()
    standings = get_all_standings()

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("football.html")

    html = template.render(
        competition_codes=COMPETITION_CODES,
        competition_names=COMPETITION_NAMES,
        matches=matches,
        scorers=scorers,
        standings=standings,
        active="football",
        build_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    (BUILD_DIR / "index.html").write_text(html)
    logger.info(f"Football page written to {BUILD_DIR / 'index.html'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    build()
