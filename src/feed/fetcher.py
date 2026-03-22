"""Fetch articles from RSS/Atom feeds using feedparser."""

import logging
from datetime import datetime

import feedparser

from src.db import get_db

logger = logging.getLogger(__name__)


def fetch_all_feeds():
    """Fetch fresh articles for every active feed."""
    with get_db("feed.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, url, title FROM feeds WHERE deleted = 0")
        feeds = cursor.fetchall()

    for feed in feeds:
        feed_id, url, title = feed["id"], feed["url"], feed["title"]
        try:
            _fetch_feed(feed_id, url)
            logger.info(f"Fetched: {title}")
        except Exception as e:
            logger.error(f"Failed to fetch {title} ({url}): {e}")


def _fetch_feed(feed_id, feed_url):
    """Fetch and store articles for a single feed."""
    feed_data = feedparser.parse(feed_url)

    if feed_data.bozo and not feed_data.entries:
        logger.warning(f"Feed parse failed for {feed_url}")
        return

    # Parse all entries first — only delete old articles if we got new ones
    entries = []
    for entry in feed_data.entries:
        guid = entry.get("id", entry.get("link", ""))
        title = entry.get("title", "Untitled")
        link = entry.get("link", "")
        description = entry.get("description", entry.get("summary", ""))
        author = entry.get("author", "")

        published = None
        for field in ("published_parsed", "updated_parsed"):
            parsed = entry.get(field)
            if parsed:
                try:
                    published = datetime(*parsed[:6])
                except Exception:
                    pass
                break

        entries.append((feed_id, guid, title, link, description, author, published))

    if not entries:
        return

    with get_db("feed.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM articles WHERE feed_id = ?", (feed_id,))

        for entry in entries:
            cursor.execute(
                "INSERT INTO articles (feed_id, guid, title, link, description, author, published) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                entry,
            )

        cursor.execute(
            "UPDATE feeds SET last_updated = ? WHERE id = ?",
            (datetime.now(), feed_id),
        )
