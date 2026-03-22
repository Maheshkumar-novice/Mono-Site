# Mono-Site

Monorepo for [maheshkumar.blog](https://maheshkumar.blog).

## Setup

```bash
uv sync
cp .env.example .env  # Add FOOTBALL_API_KEY
```

## Build

```bash
./scripts/build.sh
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
