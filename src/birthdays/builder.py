"""Build static HTML for the birthdays page."""

import logging
import os
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.birthdays.models import get_all
from src.db import init_birthdays_db

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
BUILD_DIR = Path(os.environ.get("MONO_BUILD_DIR", PROJECT_DIR / "build")) / "birthdays"
TEMPLATES_DIR = PROJECT_DIR / "templates"


def build():
    init_birthdays_db()

    birthdays = get_all()
    logger.info(f"Found {len(birthdays)} birthdays")

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("birthdays.html")

    html = template.render(
        birthdays=birthdays,
        active="birthdays",
        build_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    (BUILD_DIR / "index.html").write_text(html)
    logger.info(f"Birthdays page written to {BUILD_DIR / 'index.html'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    build()
