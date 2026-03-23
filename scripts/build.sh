#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Components and their build commands
build_landing()  { echo "-> Landing...";   cp landing/index.html landing/styles.css landing/script.js "$TARGET/"; }
build_feed()     { echo "-> Feed...";      uv run python -m src.feed.builder; }
build_football() { echo "-> Football...";  uv run python -m src.football.builder; }
build_f1()       { echo "-> F1...";        uv run python -m src.f1.builder; }
build_birthdays(){ echo "-> Birthdays..."; uv run python -m src.birthdays.builder; }
build_sky()      { echo "-> Sky...";       uv run python -m src.sky.builder; }
build_st()       { echo "-> ST...";        cp -r static-sites/st "$TARGET/st"; }
build_1d()       { echo "-> 1D...";        cp -r static-sites/1d "$TARGET/1d"; }

ALL_COMPONENTS="landing feed football f1 birthdays sky st 1d"

echo "=== Mono-Site Build ==="
echo "Started at $(date)"

COMPONENTS="${*:-all}"

if [ "$COMPONENTS" = "all" ]; then
    # Full build: temp dir + atomic swap
    BUILD_TMP="build_tmp_$$"
    trap 'rm -rf "$BUILD_TMP"' ERR
    rm -rf "$BUILD_TMP"
    mkdir -p "$BUILD_TMP"

    TARGET="$BUILD_TMP"
    export MONO_BUILD_DIR="$PROJECT_DIR/$BUILD_TMP"

    for comp in $ALL_COMPONENTS; do
        "build_$comp"
    done

    # Atomic swap
    echo "-> Swapping build..."
    rm -rf build_old
    [ -d build ] && mv build build_old
    mv "$BUILD_TMP" build
    rm -rf build_old
else
    # Partial build: write directly to build/
    mkdir -p build
    TARGET="build"
    export MONO_BUILD_DIR="$PROJECT_DIR/build"

    for comp in $COMPONENTS; do
        if declare -f "build_$comp" > /dev/null 2>&1; then
            "build_$comp"
        else
            echo "Unknown component: $comp"
            echo "Available: $ALL_COMPONENTS"
            exit 1
        fi
    done
fi

echo "=== Build complete at $(date) ==="
