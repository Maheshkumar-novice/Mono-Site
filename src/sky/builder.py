"""Build static HTML for the sky page."""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.sky.compute import compute_sky, get_night_hours, LOCATION_NAME

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
BUILD_DIR = Path(os.environ.get("MONO_BUILD_DIR", PROJECT_DIR / "build")) / "sky"
TEMPLATES_DIR = PROJECT_DIR / "templates"


def build():
    logger.info("Computing tonight's sky...")
    objects, moon, hour_labels = compute_sky()
    night_hours = get_night_hours()

    logger.info(f"Found {len(objects)} visible objects, moon: {moon['name']} ({moon['illumination']}%)")

    # Serialize positions data for JS
    positions_data = {}
    for obj in objects:
        positions_data[obj['name']] = obj.get('positions', [])

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("sky.html")

    html = template.render(
        objects=objects,
        moon=moon,
        hour_labels=hour_labels,
        positions_json=json.dumps(positions_data),
        location=LOCATION_NAME,
        window_start=night_hours[0].strftime('%I %p').lstrip('0'),
        window_end=night_hours[-1].strftime('%I %p').lstrip('0'),
        active="sky",
        build_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    (BUILD_DIR / "index.html").write_text(html)
    logger.info(f"Sky page written to {BUILD_DIR / 'index.html'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    build()
