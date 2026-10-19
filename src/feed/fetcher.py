"""Fetch articles from RSS/Atom feeds using feedparser."""

import contextlib
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import feedparser
import requests

from src.db import get_db

logger = logging.getLogger(__name__)

# feedparser has no time limit of its own, so a site that stops answering would hang the build.
TIMEOUT_SECONDS = 15
HEADERS = {"User-Agent": "maheshkumar.blog feed reader (+https://maheshkumar.blog/feed)"}
# Blogs are fetched in parallel, at most this many at a time. Each blog still gets one request.
MAX_PARALLEL = 20


def fetch_all_feeds():
    """Fetch fresh articles for every active feed."""
    with get_db("feed.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, url, title FROM feeds WHERE deleted = 0")
        feeds = cursor.fetchall()

    # Download in parallel, then save one feed at a time: SQLite handles one writer at a time.
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL) as pool:
        downloads = [pool.submit(_download, feed["id"], feed["url"]) for feed in feeds]

    for feed, download in zip(feeds, downloads, strict=True):
        url, title = feed["url"], feed["title"]
        try:
            entries = download.result()
            if entries:
                _save(feed["id"], entries)
            logger.info(f"Fetched: {title}")
        except Exception as e:
            logger.error(f"Failed to fetch {title} ({url}): {e}")


def _download(feed_id, feed_url):
    """Fetch and parse one feed. Returns its articles, ready to save."""
    resp = requests.get(feed_url, headers=HEADERS, timeout=TIMEOUT_SECONDS)
    resp.raise_for_status()
    # Passing the final address keeps relative links in the feed working.
    feed_data = feedparser.parse(
        resp.content, response_headers={**resp.headers, "content-location": resp.url}
    )

    if feed_data.bozo and not feed_data.entries:
        logger.warning(f"Feed parse failed for {feed_url}")
        return []

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
                with contextlib.suppress(Exception):
                    published = datetime(*parsed[:6])
                break

        entries.append((feed_id, guid, title, link, description, author, published))

    return entries


def _save(feed_id, entries):
    """Replace a feed's stored articles with freshly fetched ones."""
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
