# Mono-Site

Monorepo for [maheshkumar.blog](https://maheshkumar.blog).

## Projects

<details>
<summary><strong>Feed</strong> — /feed</summary>

RSS feed aggregator. Fetches articles from 8+ tech blogs (jvns.ca, simonwillison.net, etc.), filters to the last 3 days, and renders a simple article list. Feeds managed via CLI.
</details>

<details>
<summary><strong>Football</strong> — /football</summary>

Tracks 6 European football leagues — Premier League, La Liga, Bundesliga, Serie A, Ligue 1, and Champions League. Shows recent matches, top scorers, and standings. Data from football-data.org API with rate-limited fetching.
</details>

<details>
<summary><strong>F1</strong> — /f1</summary>

Formula 1 tracker showing driver and constructor standings, last race results, next race info, and the full season schedule. Data from the Ergast API with local SQLite caching.
</details>

<details>
<summary><strong>Tonight's Sky</strong> — /sky</summary>

Astronomy page showing the top 20 brightest stars and planets visible from Tamil Nadu. Features an interactive sky map, 24-hour time slider, moon phase indicator, and star details. Computed using Skyfield and the Hipparcos star catalog. [Detailed explanation →](src/sky/README.md)
</details>

<details>
<summary><strong>Quotes</strong> — /quotes</summary>

Curated collection of stoic and existentialist quotes from Marcus Aurelius, Seneca, Nietzsche, Frankl, and Sartre. Daily featured quote that changes each build. Filter by author. Managed via CLI.
</details>

<details>
<summary><strong>Weather</strong> — /weather</summary>

Live weather using Open-Meteo API. Auto-detects location via browser geolocation, falls back to Tamil Nadu. Shows current conditions, 24-hour hourly forecast, 7-day outlook, sunrise/sunset. Fully client-side, no API key needed.
</details>

<details>
<summary><strong>Tic Tac Toe</strong> — /ttt</summary>

Configurable Tic Tac Toe with board sizes from 3×3 to 7×7. Play against AI (minimax with alpha-beta pruning for small boards, heuristic for large) or another person. Score tracking across games. Pure HTML/CSS/JS. [Detailed explanation →](static-sites/ttt/README.md)
</details>

<details>
<summary><strong>Birthdays</strong> — /birthdays</summary>

Birthday tracker sorted by upcoming dates. Shows days until, age on next birthday, and categories. Protected by basic auth. Entries managed via CLI.
</details>

<details>
<summary><strong>One Direction</strong> — /1d</summary>

Fan tribute scrapbook with member profiles, gallery, timeline, discography, and a Liam Payne memorial. Static HTML/CSS/JS with background video.
</details>

<details>
<summary><strong>Stranger Things</strong> — /st</summary>

Comic book-style tribute to the TV series. Features interactive Wall of Lights, Upside Down toggle, and character panels. Static HTML/CSS/JS.
</details>

## Setup

```bash
uv sync
cp .env.example .env  # Add FOOTBALL_API_KEY
```

## Build

```bash
./scripts/build.sh              # Full build (atomic swap)
./scripts/build.sh feed sky     # Build specific components
```

## CLI

```bash
# Feeds
uv run python -m src.cli feed list
uv run python -m src.cli feed add <url>
uv run python -m src.cli feed remove <id>

# Birthdays
uv run python -m src.cli birthday list
uv run python -m src.cli birthday add "Name" "MM-DD" --category Family
uv run python -m src.cli birthday delete <id>

# Quotes
uv run python -m src.cli quote list
uv run python -m src.cli quote add "Quote text" "Author" --source "Book"
uv run python -m src.cli quote remove <index>
```

## Preview

```bash
uv run python -m http.server -d build 8000
```

## Adding a New App

Two types of apps can be added:

### Static app (pure HTML/CSS/JS)

1. Create `static-sites/myapp/index.html`
2. Add to `scripts/build.sh`:
   ```bash
   build_myapp() { echo "-> MyApp..."; cp -r static-sites/myapp "$TARGET/myapp"; }
   ```
3. Add `myapp` to the `ALL_COMPONENTS` list in `build.sh`
4. Add a link in `landing/index.html` under Live Apps
5. Build: `./scripts/build.sh myapp`

### Dynamic app (Python builder)

1. Create `src/myapp/__init__.py` and `src/myapp/builder.py`
2. The builder should:
   - Read data from an API, SQLite, or JSON file
   - Render a Jinja2 template from `templates/myapp.html`
   - Write output to `BUILD_DIR / "index.html"` using `MONO_BUILD_DIR` env var
3. Create `templates/myapp.html` extending `base.html`
4. Add to `scripts/build.sh`:
   ```bash
   build_myapp() { echo "-> MyApp..."; uv run python -m src.myapp.builder; }
   ```
5. Add `myapp` to the `ALL_COMPONENTS` list in `build.sh`
6. Add nav link in `templates/base.html`
7. Add a link in `landing/index.html` under Live Apps
8. Build: `./scripts/build.sh myapp`

### Builder template

```python
"""Build static HTML for myapp."""

import logging
import os
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
BUILD_DIR = Path(os.environ.get("MONO_BUILD_DIR", PROJECT_DIR / "build")) / "myapp"
TEMPLATES_DIR = PROJECT_DIR / "templates"


def build():
    # Fetch or compute your data here
    data = {}

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("myapp.html")

    html = template.render(
        data=data,
        active="myapp",
        build_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    (BUILD_DIR / "index.html").write_text(html)
    logger.info(f"MyApp page written to {BUILD_DIR / 'index.html'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    build()
```
