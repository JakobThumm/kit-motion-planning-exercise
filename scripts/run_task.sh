#!/usr/bin/env bash
# Plan a named task on the RUNNING move_group so it shows in RViz.
# Start ./docker/run_core.sh in one terminal first, then in another:
#   ./scripts/run_task.sh task_01_reach --planner RRTConnect
#
# Runs INSIDE the same container as move_group (via docker exec). ROS 2 actions
# are unreliable across separate containers, so we don't spawn a new one.
set -euo pipefail

if ! docker ps --format '{{.Names}}' | grep -qx kit_mp_core; then
    echo "The core container isn't running. Start it first:  ./docker/run_core.sh" >&2
    exit 1
fi

exec docker exec kit_mp_core /entrypoint.sh ros2 run kit_mp_task_api run_task "$@"
