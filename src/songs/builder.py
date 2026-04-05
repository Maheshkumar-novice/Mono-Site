"""Build static HTML for the songs pages."""

import logging
import os
import re
from datetime import datetime
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
BUILD_DIR = Path(os.environ.get("MONO_BUILD_DIR", PROJECT_DIR / "build")) / "songs"
TEMPLATES_DIR = PROJECT_DIR / "templates"
CONTENT_DIR = PROJECT_DIR / "content" / "songs"


def _parse_song(md_path):
    """Parse a song markdown file and return metadata + HTML content."""
    text = md_path.read_text()

    # Extract title from first H1
    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else md_path.stem.replace("-", " ").title()

    # Extract subtitle (first blockquote)
    subtitle_match = re.search(r"^>\s*\*?(.+?)\*?\s*$", text, re.MULTILINE)
    subtitle = subtitle_match.group(1).strip() if subtitle_match else ""

    html_content = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "toc"],
    )

    return {
        "slug": md_path.stem,
        "title": title,
        "subtitle": subtitle,
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

    songs = []
    for md_path in md_files:
        song = _parse_song(md_path)
        songs.append(song)
        logger.info(f"Parsed: {song['title']}")

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

    # Build individual song pages
    song_template = env.get_template("song.html")
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    for song in songs:
        html = song_template.render(
            song=song,
            active="songs",
            build_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
        (BUILD_DIR / f"{song['slug']}.html").write_text(html)

    # Build list page
    list_template = env.get_template("songs.html")
    html = list_template.render(
        songs=songs,
        active="songs",
        build_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
    (BUILD_DIR / "index.html").write_text(html)
    logger.info(f"Songs: {len(songs)} pages written to {BUILD_DIR}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    build()
