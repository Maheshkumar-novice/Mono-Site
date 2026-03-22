#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=== Mono-Site Build ==="
echo "Started at $(date)"

# Clean build directory
rm -rf build
mkdir -p build

# Step 1: Copy landing page
echo "-> Copying landing page..."
cp landing/index.html landing/styles.css landing/script.js build/

# Step 2: Run Python builders
echo "-> Building feed..."
uv run python -m src.feed.builder

echo "-> Building football..."
uv run python -m src.football.builder

echo "-> Building F1..."
uv run python -m src.f1.builder

echo "-> Building birthdays..."
uv run python -m src.birthdays.builder

# Step 3: Copy static sites
echo "-> Copying static sites..."
cp -r static-sites/st build/st
cp -r static-sites/1d build/1d

echo "=== Build complete at $(date) ==="
