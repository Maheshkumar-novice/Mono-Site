#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=== Mono-Site Build ==="
echo "Started at $(date)"

# Build into temp directory, then swap atomically
BUILD_TMP="build_tmp_$$"
trap 'rm -rf "$BUILD_TMP"' ERR
rm -rf "$BUILD_TMP"
mkdir -p "$BUILD_TMP"

# Step 1: Copy landing page
echo "-> Copying landing page..."
cp landing/index.html landing/styles.css landing/script.js "$BUILD_TMP/"

# Step 2: Run Python builders (output to temp dir)
export MONO_BUILD_DIR="$PROJECT_DIR/$BUILD_TMP"

echo "-> Building feed..."
uv run python -m src.feed.builder

echo "-> Building football..."
uv run python -m src.football.builder

echo "-> Building F1..."
uv run python -m src.f1.builder

echo "-> Building birthdays..."
uv run python -m src.birthdays.builder

echo "-> Building sky..."
uv run python -m src.sky.builder

# Step 3: Copy static sites
echo "-> Copying static sites..."
cp -r static-sites/st "$BUILD_TMP/st"
cp -r static-sites/1d "$BUILD_TMP/1d"

# Step 4: Atomic swap
echo "-> Swapping build..."
rm -rf build_old
[ -d build ] && mv build build_old
mv "$BUILD_TMP" build
rm -rf build_old

echo "=== Build complete at $(date) ==="
