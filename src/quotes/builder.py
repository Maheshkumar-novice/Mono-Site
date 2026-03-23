"""Build static HTML for the quotes page."""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
BUILD_DIR = Path(os.environ.get("MONO_BUILD_DIR", PROJECT_DIR / "build")) / "quotes"
TEMPLATES_DIR = PROJECT_DIR / "templates"
QUOTES_FILE = PROJECT_DIR / "data" / "quotes.json"


def load_quotes():
    if not QUOTES_FILE.exists():
        return []
    with open(QUOTES_FILE) as f:
        return json.load(f)


def get_daily_quote(quotes):
    """Pick a quote based on the day of the year. Changes daily."""
    if not quotes:
        return None
    day = datetime.now().timetuple().tm_yday
    return quotes[day % len(quotes)]


def build():
    quotes = load_quotes()
    daily = get_daily_quote(quotes)

    # Group by author
    by_author = {}
    for q in quotes:
        author = q.get("author", "Unknown")
        by_author.setdefault(author, []).append(q)

    logger.info(f"Found {len(quotes)} quotes from {len(by_author)} authors")

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("quotes.html")

    html = template.render(
        daily=daily,
        quotes=quotes,
        by_author=by_author,
        active="quotes",
        build_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    (BUILD_DIR / "index.html").write_text(html)
    logger.info(f"Quotes page written to {BUILD_DIR / 'index.html'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    build()
