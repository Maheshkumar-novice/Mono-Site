"""Build static HTML for the feed page."""

import logging
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.db import init_feed_db, seed_default_feeds
from src.feed.fetcher import fetch_all_feeds
from src.feed.models import get_recent_articles

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
BUILD_DIR = PROJECT_DIR / "build" / "feed"
TEMPLATES_DIR = PROJECT_DIR / "templates"


def build():
    """Fetch feeds and generate static HTML."""

    init_feed_db()
    seed_default_feeds()

    logger.info("Fetching all feeds...")
    fetch_all_feeds()

    articles = get_recent_articles(days=3)
    logger.info(f"Found {len(articles)} articles from the last 3 days")

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("feed.html")

    html = template.render(
        articles=articles,
        active="feed",
        build_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    (BUILD_DIR / "index.html").write_text(html)
    logger.info(f"Feed page written to {BUILD_DIR / 'index.html'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    build()
