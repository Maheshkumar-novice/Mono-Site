"""Build static HTML for the F1 page."""

import logging
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from jinja2 import Environment, FileSystemLoader

from src.db import init_f1_db
from src.f1.service import (
    get_constructor_standings,
    get_driver_standings,
    get_last_race,
    get_next_race,
    get_recent_results,
    get_schedule,
)

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
BUILD_DIR = Path(os.environ.get("MONO_BUILD_DIR", PROJECT_DIR / "build")) / "f1"
TEMPLATES_DIR = PROJECT_DIR / "templates"

# The driver followed on the page, by Ergast driver ID. His team is read from the last
# race, so the highlight moves with him if he changes teams.
FOLLOWED_DRIVER = "max_verstappen"


def _points(value):
    """Ergast sends points as text, sometimes with a half: "221.0" -> "221", "12.5" -> "12.5"."""
    number = float(value)
    return str(int(number)) if number.is_integer() else str(number)


def _following(driver_standings, constructor_standings, last_race):
    """Where the followed driver and his team stand, for the card at the top.

    None until he has a standing.
    """
    driver = next(
        (d for d in driver_standings if d.get("Driver", {}).get("driverId") == FOLLOWED_DRIVER),
        None,
    )
    if not driver or not driver.get("Constructors"):
        return None
    # Each driver's team at the last race. The standings list every team a driver raced for
    # this season, in no set order, so they can't say which team is his now.
    results = (last_race or {}).get("Results", [])
    teams_now = {
        r["Driver"]["driverId"]: r["Constructor"]
        for r in results
        if r.get("Driver") and r.get("Constructor")
    }
    team = teams_now.get(FOLLOWED_DRIVER, driver["Constructors"][-1])
    team_drivers = [d for d, t in teams_now.items() if t["constructorId"] == team["constructorId"]]
    team_standing = next(
        (
            c
            for c in constructor_standings
            if c.get("Constructor", {}).get("constructorId") == team["constructorId"]
        ),
        None,
    )
    result = next(
        (r for r in results if r.get("Driver", {}).get("driverId") == FOLLOWED_DRIVER), None
    )
    finish = None
    if result:
        position = result.get("positionText", "")
        finish = f"P{position}" if position.isdigit() else result.get("status")
    return {
        "name": f"{driver['Driver']['givenName']} {driver['Driver']['familyName']}",
        "position": driver.get("position"),
        "points": _points(driver["points"]),
        "behind": _points(float(driver_standings[0]["points"]) - float(driver["points"])),
        "team_id": team["constructorId"],
        "team_name": team["name"],
        "team_drivers": team_drivers or [FOLLOWED_DRIVER],
        "team_position": team_standing.get("position") if team_standing else None,
        "team_points": _points(team_standing["points"]) if team_standing else None,
        "last_race": last_race.get("raceName") if result else None,
        "last_finish": finish,
    }


def build():
    init_f1_db()

    logger.info("Fetching F1 data...")
    driver_standings = get_driver_standings() or []
    constructor_standings = get_constructor_standings() or []
    schedule = get_schedule() or []
    last_race = get_last_race()
    next_race = get_next_race()
    recent_results = get_recent_results() or []

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("f1.html")

    html = template.render(
        driver_standings=driver_standings,
        constructor_standings=constructor_standings,
        schedule=schedule,
        last_race=last_race,
        next_race=next_race,
        recent_results=recent_results,
        followed_driver=FOLLOWED_DRIVER,
        following=_following(driver_standings, constructor_standings, last_race),
        active="f1",
        build_time=datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M IST"),
    )

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    (BUILD_DIR / "index.html").write_text(html)
    logger.info(f"F1 page written to {BUILD_DIR / 'index.html'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    build()
