# Distributing the container image

Students run a **prebuilt image**; they do not build the core image themselves.
Docker ships *images* (the static artifact), and each student's machine creates
*containers* from that image on demand via `docker compose`. Only the **CORE**
image is distributed.

## Requirements for students
- Docker + `docker compose` v2 on an **x86_64/amd64** Linux host (or WSL2).
  Apple Silicon is not supported (the stack is x86; emulation is impractical).
- The **repo** (`git clone`) for the compose file, scripts, and the editable
  configs that are mounted live into the container.

So each student needs two things: **the image** (pulled) and **the repo** (cloned).

## Student quickstart (pull, don't build)
```bash
git clone git@github.com:JakobThumm/kit-motion-planning-exercise.git
cd kit-motion-planning-exercise/docker
cp .env.example .env            # optionally pin KIT_MP_TAG to the course semester
docker compose pull core        # downloads the prebuilt CORE image from GHCR
cd ..
./docker/run_core.sh            # launches MoveIt + RViz (creates a container)
```
`docker compose` creates and removes containers for them; they only ever *pull*
the image. Their edits to `ompl_planning.yaml` / `student_solution.py` are mounted
over the image at runtime, so a prebuilt image does not block the exercise.

## Instructor: publish the image (once per semester)
```bash
export CR_PAT=<github PAT with write:packages>
./scripts/publish_image.sh 2026ss     # builds, tags, pushes ghcr.io/jakobthumm/kit-mp-core
```
Then, **one time**, make the GHCR package **public** (GitHub → your profile →
Packages → `kit-mp-core` → Package settings → change visibility). After that,
students pull without any login.

The compose `core` service points at `ghcr.io/jakobthumm/kit-mp-core:${KIT_MP_TAG}`
(default `latest`). Pin a semester with `KIT_MP_TAG=2026ss` in `.env`.

## The GPU / advanced track is built locally (not distributed)
The Isaac Sim / cuMotion image is `FROM nvcr.io/nvidia/isaac-sim`, which is under
NVIDIA's license and **must not be redistributed**. Students on the advanced track:
1. Pull the core image as above (the GPU image builds `FROM` it).
2. `docker login nvcr.io` with their own NGC key and build locally:
   ```bash
   docker compose build curobo      # FROM ghcr core image, adds cuMotion
   docker compose build isaac       # pulls Isaac Sim from NGC
   ```
See [02_install_gpu.md](02_install_gpu.md).

## Alternative: offline tarball
No registry access? Ship the image as a file instead:
```bash
# instructor
docker compose -f docker/docker-compose.yml build core
docker save ghcr.io/jakobthumm/kit-mp-core:latest | gzip > kit-mp-core.tar.gz
# host kit-mp-core.tar.gz on the university share; students:
gunzip -c kit-mp-core.tar.gz | docker load
```
Do **not** use `docker export` — that flattens a container and loses the image
metadata (ENTRYPOINT, env). Always `docker save` / `docker load` for images.
