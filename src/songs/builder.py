"""Build static HTML for the songs pages."""

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus
from urllib.request import urlopen
from zoneinfo import ZoneInfo

import markdown
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
BUILD_DIR = Path(os.environ.get("MONO_BUILD_DIR", PROJECT_DIR / "build")) / "songs"
TEMPLATES_DIR = PROJECT_DIR / "templates"
CONTENT_DIR = PROJECT_DIR / "content" / "songs"
ART_CACHE_FILE = PROJECT_DIR / "data" / "song_art.json"

ITUNES_API = "https://itunes.apple.com/search?media=music&limit=1&term="
ART_SIZE = "300x300"


def _load_art_cache():
    if ART_CACHE_FILE.exists():
        return json.loads(ART_CACHE_FILE.read_text())
    return {}


def _save_art_cache(cache):
    ART_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    ART_CACHE_FILE.write_text(json.dumps(cache, indent=2))


def _fetch_artwork(song_name, artist_name, cache):
    """Fetch album artwork URL from iTunes API, with caching."""
    cache_key = f"{song_name} — {artist_name}"
    if cache_key in cache:
        return cache[cache_key]

    try:
        query = quote_plus(f"{song_name} {artist_name}")
        url = f"{ITUNES_API}{query}&limit=5"
        with urlopen(url, timeout=10) as resp:  # noqa: S310
            data = json.loads(resp.read())
        results = data.get("results", [])
        # Prefer result matching the artist name
        artist_lower = artist_name.lower()
        match = next(
            (r for r in results if artist_lower in r.get("artistName", "").lower()),
            results[0] if results else None,
        )
        if match:
            art_url = match.get("artworkUrl100", "")
            art_url = art_url.replace("100x100bb", f"{ART_SIZE}bb")
            cache[cache_key] = art_url
            logger.info(f"Artwork fetched: {cache_key}")
            return art_url
    except Exception as e:
        logger.warning(f"Artwork fetch failed for {cache_key}: {e}")

    cache[cache_key] = ""
    return ""


def _extract_song_artist(title):
    """Extract song name and artist from H1 like '🎵 Song — Artist'."""
    cleaned = re.sub(r"^[🎵\s]+", "", title).strip()
    if " — " in cleaned:
        parts = cleaned.split(" — ", 1)
        return parts[0].strip(), parts[1].strip()
    return cleaned, ""


def _parse_song(md_path, art_cache):
    """Parse a song markdown file and return metadata + HTML content."""
    text = md_path.read_text()

    # Extract title from first H1
    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else md_path.stem.replace("-", " ").title()

    # Extract subtitle (first blockquote)
    subtitle_match = re.search(r"^>\s*\*?(.+?)\*?\s*$", text, re.MULTILINE)
    subtitle = subtitle_match.group(1).strip() if subtitle_match else ""

    # Fetch artwork
    song_name, artist_name = _extract_song_artist(title)
    artwork = _fetch_artwork(song_name, artist_name, art_cache) if artist_name else ""

    html_content = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "toc"],
    )

    return {
        "slug": md_path.stem,
        "title": title,
        "subtitle": subtitle,
        "artwork": artwork,
        "content": html_content,
    }


def build():
    if not CONTENT_DIR.exists():
        logger.info("No songs content directory found — skipping.")
        return

    md_files = sorted(CONTENT_DIR.glob("*.md"))
    if not md_files:
        logger.info("No song files found — skipping.")
        return

    art_cache = _load_art_cache()

    songs = []
    for md_path in md_files:
        song = _parse_song(md_path, art_cache)
        songs.append(song)
        logger.info(f"Parsed: {song['title']}")

    _save_art_cache(art_cache)

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

    # Build individual song pages
    song_template = env.get_template("song.html")
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    for song in songs:
        html = song_template.render(
            song=song,
            active="songs",
            build_time=datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M IST"),
        )
        (BUILD_DIR / f"{song['slug']}.html").write_text(html)

    # Build list page
    list_template = env.get_template("songs.html")
    html = list_template.render(
        songs=songs,
        active="songs",
        build_time=datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M IST"),
    )
    (BUILD_DIR / "index.html").write_text(html)
    logger.info(f"Songs: {len(songs)} pages written to {BUILD_DIR}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    build()
