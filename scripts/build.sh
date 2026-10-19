#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# One build at a time: if the previous build is still running, skip this turn.
# The lock is held on the project folder itself, so it needs no lock file and survives git pulls.
exec 9<"$PROJECT_DIR"
if ! flock -n 9; then
    echo "=== Skipped at $(date): the previous build is still running ==="
    exit 0
fi

# A step that runs longer than this many seconds is stopped.
STEP_TIMEOUT="${STEP_TIMEOUT:-300}"

# Components and their build commands
build_landing()  { echo "-> Landing...";   cp landing/index.html landing/styles.css landing/script.js landing/quotes.json landing/robots.txt landing/sitemap.xml "$TARGET/"; }
build_feed()     { echo "-> Feed...";      uv run python -m src.feed.builder; }
build_football() { echo "-> Football...";  uv run python -m src.football.builder; }
build_f1()       { echo "-> F1...";        uv run python -m src.f1.builder; }
build_birthdays(){ echo "-> Birthdays..."; uv run python -m src.birthdays.builder; }
build_sky()      { echo "-> Sky...";       uv run python -m src.sky.builder; }
build_st()       { echo "-> ST...";        cp -r static-sites/st "$TARGET/st"; }
build_1d()       { echo "-> 1D...";        cp -r static-sites/1d "$TARGET/1d"; }
build_ttt()      { echo "-> TTT...";       cp -r static-sites/ttt "$TARGET/ttt"; }
build_stretch()  { echo "-> Stretch...";   cp -r static-sites/stretch "$TARGET/stretch"; }
build_workout()  { echo "-> Workout...";   cp -r static-sites/workout "$TARGET/workout"; }
build_songs()    { echo "-> Songs...";    uv run python -m src.songs.builder; }
build_akshaya()  { echo "-> Akshaya...";   cp -r akshaya-build/akshaya "$TARGET/akshaya"; }
ALL_COMPONENTS="landing feed football f1 birthdays sky st 1d ttt stretch workout songs akshaya"

# Each step runs in its own shell under the time limit, so the build functions are exported to it.
export -f $(compgen -A function build_)

# Runs one component. Fails if the step fails or runs past the time limit.
run_step() {
    local status=0
    timeout -k 30 "$STEP_TIMEOUT" bash -c "build_$1" || status=$?
    if [ "$status" -eq 124 ]; then
        echo "!! $1 ran longer than ${STEP_TIMEOUT}s and was stopped"
    elif [ "$status" -ne 0 ]; then
        echo "!! $1 failed"
    fi
    return "$status"
}

# Puts back a failed component's page from the last good build, so one broken part
# doesn't hold back the rest of the site.
keep_old() {
    rm -rf "${TARGET:?}/$1"
    if [ "$1" = landing ]; then
        [ -d build ] && find build -maxdepth 1 -type f -exec cp {} "$TARGET/" \;
    elif [ -d "build/$1" ]; then
        cp -r "build/$1" "$TARGET/$1"
    fi
    echo "   kept $1 from the last build"
    return 0
}

echo "=== Mono-Site Build ==="
echo "Started at $(date)"

COMPONENTS="${*:-all}"
FAILED=""

if [ "$COMPONENTS" = "all" ]; then
    # Full build: temp dir + atomic swap
    # Clear anything left by a build that was stopped part-way. Safe, because of the lock above.
    rm -rf build_tmp_* build_old
    BUILD_TMP="build_tmp_$$"
    trap 'rm -rf "$BUILD_TMP"' EXIT
    mkdir -p "$BUILD_TMP"

    export TARGET="$BUILD_TMP"
    export MONO_BUILD_DIR="$PROJECT_DIR/$BUILD_TMP"

    for comp in $ALL_COMPONENTS; do
        if ! run_step "$comp"; then
            FAILED="$FAILED $comp"
            keep_old "$comp"
        fi
    done

    # Atomic swap
    echo "-> Swapping build..."
    [ -d build ] && mv build build_old
    mv "$BUILD_TMP" build
    rm -rf build_old
else
    # Partial build: write directly to build/
    mkdir -p build
    export TARGET="build"
    export MONO_BUILD_DIR="$PROJECT_DIR/build"

    for comp in $COMPONENTS; do
        if ! declare -f "build_$comp" > /dev/null 2>&1; then
            echo "Unknown component: $comp"
            echo "Available: $ALL_COMPONENTS"
            exit 1
        fi
        run_step "$comp" || FAILED="$FAILED $comp"
    done
fi

[ -n "$FAILED" ] && echo "!! Failed:$FAILED"
echo "=== Build complete at $(date) ==="

# Exit with an error when a part failed, so a manual run shows it.
[ -z "$FAILED" ]
