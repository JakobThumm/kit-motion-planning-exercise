#!/usr/bin/env bash
# Instructor: build and publish the CORE image to GitHub Container Registry (GHCR).
# Only the CORE image is redistributable — do NOT push the GPU/Isaac image
# (it contains NVIDIA-licensed layers). Students build the GPU layer themselves.
#
# Usage:
#   export CR_PAT=<github PAT with write:packages>
#   ./scripts/publish_image.sh 2026ss      # tag (default: latest)
set -euo pipefail
cd "$(dirname "$0")/.."

REGISTRY="ghcr.io/jakobthumm"
IMAGE="kit-mp-core"
TAG="${1:-latest}"
REF="${REGISTRY}/${IMAGE}:${TAG}"

echo "Building ${REF} ..."
KIT_MP_TAG="${TAG}" docker compose -f docker/docker-compose.yml build core

echo "Logging in to ghcr.io ..."
if [ -z "${CR_PAT:-}" ]; then
    echo "Set CR_PAT to a GitHub Personal Access Token with 'write:packages'." >&2
    exit 1
fi
echo "${CR_PAT}" | docker login ghcr.io -u JakobThumm --password-stdin

echo "Pushing ${REF} ..."
docker push "${REF}"

# Also move :latest when publishing a semester tag, so the default pulls the newest.
if [ "${TAG}" != "latest" ]; then
    docker tag "${REF}" "${REGISTRY}/${IMAGE}:latest"
    docker push "${REGISTRY}/${IMAGE}:latest"
fi

echo
echo "Published ${REF}"
echo "Make the package PUBLIC once (GitHub -> Packages -> ${IMAGE} -> Package settings)"
echo "so students can pull without logging in:"
echo "    docker pull ${REF}"
