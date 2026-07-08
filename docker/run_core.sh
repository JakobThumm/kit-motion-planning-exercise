#!/usr/bin/env bash
# CORE track launcher: allow X11 from the container, then start MoveIt + RViz (CPU only).
set -e
cd "$(dirname "$0")"

# Allow the local Docker containers to draw on the host X server (for RViz).
xhost +local:docker >/dev/null 2>&1 || echo "warning: xhost not available (no GUI?)"

docker compose build core
docker compose run --rm --service-ports core "$@"

# With no extra args this runs the compose 'command' (core.launch.py).
# Examples:
#   ./run_core.sh                                   # RViz + MoveIt
#   ./run_core.sh bash                              # a shell in the container
#   ./run_core.sh ros2 launch kit_mp_bringup benchmark.launch.py
