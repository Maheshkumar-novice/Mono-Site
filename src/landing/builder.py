"""Build the home page: copy the landing files and list every static page on it.

Each folder in static-sites/ is a page. Two tags in its index.html <head> name it and
pick its home page section:

    <meta name="app-name" content="Calculator">
    <meta name="app-section" content="Fun">

The cards go where landing/index.html has a `<!-- static-apps: Section -->` marker, and
the addresses go where landing/sitemap.xml has `<!-- static-apps -->`. A page without the
tags is still published, but gets no card.
"""

import html
import logging
import os
import re
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
BUILD_DIR = Path(os.environ.get("MONO_BUILD_DIR", PROJECT_DIR / "build"))
LANDING_DIR = PROJECT_DIR / "landing"
STATIC_DIR = PROJECT_DIR / "static-sites"

SITE_URL = "https://maheshkumar.blog"
SECTIONS = ("Trackers", "Fun", "Personal", "Tools", "Reading")
LANDING_FILES = (
    "index.html",
    "styles.css",
    "script.js",
    "quotes.json",
    "robots.txt",
    "sitemap.xml",
    # Browsers ask for /favicon.ico on every page, so one file at the root covers the whole site.
    "favicon.ico",
)

CARD = """                <a href="/{slug}" class="live-app-card">
                    <span class="live-app-name">{name}</span>
                    <span class="live-app-arrow">&rarr;</span>
                </a>
"""


def _meta(page, name):
    match = re.search(rf'<meta\s+name="{name}"\s+content="([^"]*)"', page)
    return html.unescape(match.group(1)).strip() if match else None


def static_pages():
    """(folder, name, section) for each static page that names itself, sorted by name."""
    pages = []
    for folder in sorted(p for p in STATIC_DIR.iterdir() if (p / "index.html").is_file()):
        page = (folder / "index.html").read_text(errors="replace")
        name, section = _meta(page, "app-name"), _meta(page, "app-section")
        if not name or section not in SECTIONS:
            logger.warning(
                f"static-sites/{folder.name} needs app-name and app-section "
                f"({', '.join(SECTIONS)}) tags: published, but not on the home page"
            )
            continue
        pages.append((folder.name, name, section))
    return sorted(pages, key=lambda p: p[1].lower())


def _fill(text, marker, content, file_name):
    """Replace the marker's whole line with content."""
    pattern = rf"[ \t]*{re.escape(marker)}\n"
    if not re.search(pattern, text):
        raise SystemExit(f"{file_name} is missing the marker {marker}")
    return re.sub(pattern, lambda _: content, text)


def build():
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    for name in LANDING_FILES:
        shutil.copy(LANDING_DIR / name, BUILD_DIR / name)

    pages = static_pages()

    index = (LANDING_DIR / "index.html").read_text()
    for section in SECTIONS:
        cards = "".join(
            CARD.format(slug=html.escape(folder), name=html.escape(name))
            for folder, name, page_section in pages
            if page_section == section
        )
        index = _fill(index, f"<!-- static-apps: {section} -->", cards, "landing/index.html")
    (BUILD_DIR / "index.html").write_text(index)

    sitemap = (LANDING_DIR / "sitemap.xml").read_text()
    urls = "".join(
        f"  <url><loc>{SITE_URL}/{html.escape(folder)}</loc></url>\n" for folder, _, _ in pages
    )
    sitemap = _fill(sitemap, "<!-- static-apps -->", urls, "landing/sitemap.xml")
    (BUILD_DIR / "sitemap.xml").write_text(sitemap)

    logger.info(f"Home page written, listing {len(pages)} static pages")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    build()
