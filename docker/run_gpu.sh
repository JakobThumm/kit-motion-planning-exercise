#!/usr/bin/env bash
# ADVANCED track launcher: cuMotion planner container with GPU passthrough.
# Requires nvidia-container-toolkit (run ./scripts/verify_gpu.sh first).
set -e
cd "$(dirname "$0")"

xhost +local:docker >/dev/null 2>&1 || echo "warning: xhost not available"

docker compose build core        # gpu image is FROM kit-mp-core
docker compose build curobo
docker compose run --rm --service-ports curobo "$@"
