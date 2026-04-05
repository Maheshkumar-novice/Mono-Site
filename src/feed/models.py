"""Feed and article database operations."""

from datetime import datetime

from src.db import get_db


def get_all_feeds():
    """Get all active feeds."""
    with get_db("feed.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM feeds WHERE deleted = 0 ORDER BY title")
        return [dict(row) for row in cursor.fetchall()]


def get_feed(feed_id):
    """Get a feed by ID."""
    with get_db("feed.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM feeds WHERE id = ?", (feed_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def add_feed(url, title=None, description="", link=""):
    """Add a new feed URL."""
    with get_db("feed.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO feeds (url, title, description, link, last_updated) "
            "VALUES (?, ?, ?, ?, ?)",
            (url, title, description, link, datetime.now()),
        )
        return cursor.lastrowid


def remove_feed(feed_id):
    """Soft-delete a feed."""
    with get_db("feed.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE feeds SET deleted = 1 WHERE id = ?", (feed_id,))


def get_recent_articles(days=3):
    """Get all articles from the last N days across all feeds."""
    with get_db("feed.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT a.title, a.link, a.published, a.author, f.title as feed_title
            FROM articles a
            JOIN feeds f ON a.feed_id = f.id
            WHERE f.deleted = 0
              AND a.published >= datetime('now', ?)
            ORDER BY a.published DESC
            """,
            (f"-{days} days",),
        )
        return [dict(row) for row in cursor.fetchall()]
