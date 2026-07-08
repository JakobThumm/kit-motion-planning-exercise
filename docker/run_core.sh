#!/usr/bin/env bash
# CORE track launcher: allow X11 from the container, then start MoveIt + RViz (CPU only).
set -e
cd "$(dirname "$0")"

# Allow the local Docker containers to draw on the host X server (for RViz).
xhost +local:docker >/dev/null 2>&1 || echo "warning: xhost not available (no GUI?)"

# Prefer the prebuilt image from GHCR; fall back to a local build if unavailable.
docker compose pull core 2>/dev/null || docker compose build core
# Fixed container name so `run_task.sh` can `docker exec` into the SAME container
# (ROS 2 actions are unreliable across separate containers; same container is fine).
docker rm -f kit_mp_core >/dev/null 2>&1 || true
docker compose run --rm --name kit_mp_core --service-ports core "$@"

# With no extra args this runs the compose 'command' (core.launch.py).
# Examples:
#   ./run_core.sh                                   # RViz + MoveIt
#   ./run_core.sh bash                              # a shell in the container
#   ./run_core.sh ros2 launch kit_mp_bringup benchmark.launch.py
