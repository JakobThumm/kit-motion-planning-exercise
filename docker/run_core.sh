#!/usr/bin/env bash
# CORE track launcher: allow X11 from the container, then start MoveIt + RViz (CPU only).
set -e
cd "$(dirname "$0")"

# Allow the local Docker containers to draw on the host X server (for RViz).
xhost +local:docker >/dev/null 2>&1 || echo "warning: xhost not available (no GUI?)"

# Use a local image if present (a dev build or a previous pull); otherwise pull
# the prebuilt image from GHCR, and only build as a last resort. This avoids
# clobbering a local build with a stale published image.
[ -f .env ] && source .env
IMG="ghcr.io/jakobthumm/kit-mp-core:${KIT_MP_TAG:-latest}"
docker image inspect "$IMG" >/dev/null 2>&1 \
    || docker compose pull core 2>/dev/null \
    || docker compose build core
# Fixed container name so `run_task.sh` can `docker exec` into the SAME container
# (ROS 2 actions are unreliable across separate containers; same container is fine).
docker rm -f kit_mp_core >/dev/null 2>&1 || true
docker compose run --rm --name kit_mp_core --service-ports core "$@"

# With no extra args this runs the compose 'command' (core.launch.py).
# Examples:
#   ./run_core.sh                                   # RViz + MoveIt
#   ./run_core.sh bash                              # a shell in the container
#   ./run_core.sh ros2 launch kit_mp_bringup benchmark.launch.py
