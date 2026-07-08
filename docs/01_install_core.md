# Install — CORE track (no GPU)

Works on any Linux laptop with Docker. ~10 GB image, a few minutes to build.

## Prerequisites

- Docker Engine + `docker compose` (v2).
- An X server for RViz (default on Linux desktops). On Wayland, X apps work through
  XWayland.

## Build & run

```bash
git clone git@github.com:JakobThumm/kit-motion-planning-exercise.git
cd kit-motion-planning-exercise

# Build the CPU image (vendors the FR3 packages and builds the workspace).
cd docker
docker compose build core

# Launch MoveIt + RViz + mock controller.
./run_core.sh
```

If RViz cannot open a window:

```bash
xhost +local:docker      # allow the container to use your X server
```

## First plan (Exercise 1)

1. In RViz, find the **MotionPlanning** panel (left).
2. Under **Planning**, the group is `fr3_arm`.
3. Drag the orange interactive marker to a new goal, or use a random valid goal.
4. Pick a planner in the **OMPL** dropdown (start with `RRTConnect`).
5. Click **Plan**, then **Plan & Execute**. Watch the trajectory.

## Edit and iterate

Configs are mounted live from the host — edit and relaunch, no rebuild:

- Planner settings: [`ros2_ws/src/kit_mp_bringup/config/ompl_planning.yaml`](../ros2_ws/src/kit_mp_bringup/config/ompl_planning.yaml)
- Scene: pass `scene:=shelf` (or `cluttered_table`, `narrow_passage`, `empty`):
  ```bash
  ./run_core.sh ros2 launch kit_mp_bringup core.launch.py scene:=shelf
  ```

## Score a competition entry (CPU only)

```bash
cd ..            # repo root
./scripts/score_local.sh myteam
```

Next: [the OMPL playground](03_ompl_playground.md).
