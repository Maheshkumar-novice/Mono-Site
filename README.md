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

<details>
<summary><strong>Morning Mobility</strong> — /stretch</summary>

Stretching routine with a built-in timer. Static HTML/CSS/JS.
</details>

<details>
<summary><strong>Workout Plan</strong> — /workout</summary>

Workout routine with a built-in timer. Static HTML/CSS/JS.
</details>

<details>
<summary><strong>Stats</strong> — /stats</summary>

Site analytics page powered by GoAccess. Shows total requests, unique visitors, bot hits, top pages, referring sites, OS breakdown, and bot breakdown. Built from Caddy access logs during the build process.
</details>

<details>
<summary><strong>Songs</strong> — /songs</summary>

Song deep-dive blog pages. Each song is a markdown file in `content/songs/` that gets converted to a styled HTML page. List page shows all songs, each links to a full deep dive covering themes, key lyrics, vocabulary, cultural context, and more.
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
```

## Claude Code Skills

Custom slash commands for Claude Code are in `.claude/skills/`.

- `/song-deep-dive` — Generate a blog-ready markdown deep dive for any English song. Covers themes, key lyrics, vocabulary, cultural context, and more. Save output to `content/songs/<slug>.md` and build with `./scripts/build.sh songs`.

## Lint

```bash
uv run ruff check src/     # Lint
uv run ruff format src/    # Format
uvx ty check src/          # Type check
```

Pre-commit hooks run `ruff check`, `ruff format`, and `ty check` on every commit. Setup:

```bash
uv run pre-commit install
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
6. Add a link in `landing/index.html` under Live Apps
7. Build: `./scripts/build.sh myapp`

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
