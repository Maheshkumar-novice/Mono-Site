"""Shared database helpers and schema initialization."""

import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def db_path(name):
    """Get the full path for a database file."""
    DATA_DIR.mkdir(exist_ok=True)
    return str(DATA_DIR / name)


@contextmanager
def get_db(name):
    """Context manager for database connections."""
    conn = sqlite3.connect(db_path(name))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_feed_db():
    """Initialize the feed database schema."""
    with get_db("feed.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                description TEXT,
                link TEXT,
                last_updated TIMESTAMP,
                deleted INTEGER DEFAULT 0
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_id INTEGER NOT NULL,
                guid TEXT NOT NULL,
                title TEXT,
                link TEXT,
                description TEXT,
                author TEXT,
                published TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feed_id) REFERENCES feeds(id) ON DELETE CASCADE,
                UNIQUE(feed_id, guid)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_feed_id ON articles(feed_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published DESC)")
        conn.commit()


def init_football_db():
    """Initialize the football database schema."""
    with get_db("football.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                competition_code TEXT PRIMARY KEY,
                data_json TEXT,
                updated_at TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scorers (
                competition_code TEXT PRIMARY KEY,
                data_json TEXT,
                updated_at TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS standings (
                competition_code TEXT PRIMARY KEY,
                data_json TEXT,
                updated_at TIMESTAMP
            )
        """)
        conn.commit()


def init_f1_db():
    """Initialize the F1 cache database schema."""
    with get_db("f1.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        """)
        conn.commit()


def init_birthdays_db():
    """Initialize the birthdays database schema."""
    with get_db("birthdays.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS birthday (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                category TEXT DEFAULT 'Other',
                notes TEXT
            )
        """)
        conn.commit()


def seed_default_feeds():
    """Add default feeds if the feed database is empty."""
    import feedparser

    default_feeds = [
        'https://jvns.ca/atom.xml',
        'https://simonwillison.net/atom/everything/',
        'https://lucumr.pocoo.org/feed.atom',
        'https://samwho.dev/rss.xml',
        'https://blog.miguelgrinberg.com/feed',
        'https://world.hey.com/dhh/feed.atom',
        'https://herman.bearblog.dev/feed/',
        'https://harper.blog/index.xml',
    ]

    with get_db("feed.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM feeds WHERE deleted = 0")
        count = cursor.fetchone()[0]

        if count > 0:
            return

        logger.info("Seeding default feeds...")
        for url in default_feeds:
            try:
                feed_data = feedparser.parse(url)
                title = feed_data.feed.get('title', 'Untitled Feed')
                description = feed_data.feed.get('description', feed_data.feed.get('subtitle', ''))
                link = feed_data.feed.get('link', '')
                cursor.execute(
                    "INSERT OR IGNORE INTO feeds (url, title, description, link) VALUES (?, ?, ?, ?)",
                    (url, title, description, link),
                )
                logger.info(f"Seeded feed: {title}")
            except Exception as e:
                logger.error(f"Failed to seed feed {url}: {e}")


def init_all():
    """Initialize all databases."""
    init_feed_db()
    init_football_db()
    init_f1_db()
    init_birthdays_db()
