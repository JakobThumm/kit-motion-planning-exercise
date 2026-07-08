#!/usr/bin/env bash
# Score your competition entry locally (CPU only). Run from the repo root on the host.
#   ./scripts/score_local.sh [GROUP_NAME] [REPS]
set -euo pipefail
cd "$(dirname "$0")/.."

GROUP="${1:-local}"
REPS="${2:-10}"
mkdir -p results

echo "Scoring group '${GROUP}' over ${REPS} runs (CPU core track)..."
docker compose -f docker/docker-compose.yml build core
docker compose -f docker/docker-compose.yml run --rm core \
    ros2 launch kit_mp_benchmark competition.launch.py \
        output:=/root/results/results.json group:="${GROUP}" reps:="${REPS}"

echo
echo "Result written to results/results.json"
echo "Score line above. To submit, see submission/README.md."
