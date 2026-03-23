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

Astronomy page showing the top 20 brightest stars and planets visible from Tamil Nadu. Features an interactive sky map, 24-hour time slider, moon phase indicator, and star details. Computed using Skyfield and the Hipparcos star catalog.
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
uv run python -m src.cli feed list
uv run python -m src.cli feed add <url>
uv run python -m src.cli feed remove <id>

uv run python -m src.cli birthday list
uv run python -m src.cli birthday add "Name" "MM-DD" --category Family
uv run python -m src.cli birthday delete <id>
```

## Preview

```bash
uv run python -m http.server -d build 8000
```
