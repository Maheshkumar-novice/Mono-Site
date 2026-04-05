"""Build static HTML for the F1 page."""

import logging
import os
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.db import init_f1_db
from src.f1.service import (
    get_constructor_standings,
    get_driver_standings,
    get_last_race,
    get_next_race,
    get_recent_results,
    get_schedule,
)

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
BUILD_DIR = Path(os.environ.get("MONO_BUILD_DIR", PROJECT_DIR / "build")) / "f1"
TEMPLATES_DIR = PROJECT_DIR / "templates"


def build():
    init_f1_db()

    logger.info("Fetching F1 data...")
    driver_standings = get_driver_standings() or []
    constructor_standings = get_constructor_standings() or []
    schedule = get_schedule() or []
    last_race = get_last_race()
    next_race = get_next_race()
    recent_results = get_recent_results() or []

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("f1.html")

    html = template.render(
        driver_standings=driver_standings,
        constructor_standings=constructor_standings,
        schedule=schedule,
        last_race=last_race,
        next_race=next_race,
        recent_results=recent_results,
        active="f1",
        build_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    (BUILD_DIR / "index.html").write_text(html)
    logger.info(f"F1 page written to {BUILD_DIR / 'index.html'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    build()
