"""Build static HTML for the stats page."""

import json
import logging
import os
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
BUILD_DIR = Path(os.environ.get("MONO_BUILD_DIR", PROJECT_DIR / "build")) / "stats"
TEMPLATES_DIR = PROJECT_DIR / "templates"
CACHE_FILE = PROJECT_DIR / "data" / "stats.json"

ACCESS_LOG = "/var/log/caddy/access.log"
ASSET_EXTENSIONS = {".json", ".css", ".js", ".png", ".jpg", ".svg", ".ico", ".woff", ".woff2", ".ttf"}


def _run_goaccess():
    """Run goaccess and return parsed JSON, or None on failure."""
    try:
        result = subprocess.run(
            ["goaccess", ACCESS_LOG, "--log-format=CADDY", "-o", "json"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        logger.warning(f"goaccess failed: {e}")
    return None


def _normalize_path(path):
    """Strip trailing slash for merging duplicates."""
    if path != "/" and path.endswith("/"):
        return path.rstrip("/")
    return path


def _is_page(path):
    """Filter out asset requests."""
    return not any(path.endswith(ext) for ext in ASSET_EXTENSIONS)


def _parse_stats(data):
    """Extract and clean stats from goaccess JSON."""
    general = data.get("general", {})

    # Merge duplicate paths
    page_map = defaultdict(lambda: {"hits": 0, "visitors": 0})
    for entry in data.get("requests", {}).get("data", []):
        path = entry.get("data", "")
        if not _is_page(path):
            continue
        key = _normalize_path(path)
        page_map[key]["hits"] += entry.get("hits", {}).get("count", 0)
        page_map[key]["visitors"] += entry.get("visitors", {}).get("count", 0)

    top_pages = sorted(
        [{"path": k, **v} for k, v in page_map.items()],
        key=lambda x: x["hits"], reverse=True,
    )[:10]

    # Bot metrics
    bot_hits = 0
    for entry in data.get("browsers", {}).get("data", []):
        agent = entry.get("data", "").lower()
        if "bot" in agent or "crawl" in agent or "spider" in agent:
            bot_hits += entry.get("hits", {}).get("count", 0)

    # Referring sites
    referrers = []
    for entry in data.get("referring_sites", {}).get("data", []):
        site = entry.get("data", "")
        if site:
            referrers.append({
                "site": site,
                "hits": entry.get("hits", {}).get("count", 0),
                "visitors": entry.get("visitors", {}).get("count", 0),
            })

    return {
        "total_requests": general.get("total_requests", 0),
        "unique_visitors": general.get("unique_visitors", 0),
        "bot_hits": bot_hits,
        "top_pages": top_pages,
        "referrers": referrers[:10],
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def build():
    raw = _run_goaccess()

    if raw:
        stats = _parse_stats(raw)
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        CACHE_FILE.write_text(json.dumps(stats, indent=2))
        logger.info("Stats parsed from goaccess.")
    elif CACHE_FILE.exists():
        stats = json.loads(CACHE_FILE.read_text())
        logger.info("Using cached stats.")
    else:
        logger.warning("No stats available — skipping stats build.")
        return

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("stats.html")

    html = template.render(
        stats=stats,
        active="stats",
        build_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    (BUILD_DIR / "index.html").write_text(html)
    logger.info(f"Stats page written to {BUILD_DIR / 'index.html'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    build()
