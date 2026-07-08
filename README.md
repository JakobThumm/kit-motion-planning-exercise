# KIT Motion Planning Exercise

Interactive exercise on **motion planning for manipulation** with a Franka Research 3 (FR3)
arm. You will explore motion-planning algorithms, tune their hyperparameters, swap scenes,
benchmark algorithms against each other, and enter a competition. **The three groups that
produce the fastest valid trajectory get to run it on a real Franka Research 3 robot.**

Stack: **ROS 2 Jazzy · MoveIt 2 · OMPL · Isaac Sim · cuRobo (cuMotion)**.

---

## Two tracks

The exercise is split so that everyone can do the core work on a laptop, and GPU owners can
go further.

| Track | Needs | What you do |
|---|---|---|
| **CORE** (required) | Any laptop, Docker. **No GPU.** | OMPL planners in MoveIt 2, RViz, mock controller. Switch algorithms, tune hyperparameters, swap scenes, benchmark, and score competition entries. |
| **ADVANCED** (optional) | NVIDIA GPU (driver 580+), `nvidia-container-toolkit`. | High-fidelity execution in Isaac Sim and GPU planning with cuRobo/cuMotion. Compare OMPL vs a GPU planner. |

You can win the competition on the **CORE** track alone. The metric is CPU-only reproducible.

---

## Quickstart (CORE track, ~5 min after the image is built)

```bash
# 1. Build the CPU image and vendor the FR3 packages
cd docker
docker compose build core

# 2. Launch MoveIt + RViz + mock controller
./run_core.sh        # allows X11, then: docker compose run --rm core ros2 launch kit_mp_bringup core.launch.py
```

In RViz: set a goal with the **MotionPlanning** panel, pick a planner in the **OMPL** dropdown,
and hit **Plan & Execute**. Then start editing
[`ros2_ws/src/kit_mp_bringup/config/ompl_planning.yaml`](ros2_ws/src/kit_mp_bringup/config/ompl_planning.yaml).

Score a competition entry locally (still CPU-only):

```bash
./scripts/score_local.sh          # runs the fixed competition task and writes results.json
```

---

## Where things live

- **Docker & compose** — [`docker/`](docker/)
- **Launch, RViz, and the planner configs you edit** — [`ros2_ws/src/kit_mp_bringup/`](ros2_ws/src/kit_mp_bringup/)
- **The `ompl_planning.yaml` playground** — [`ros2_ws/src/kit_mp_bringup/config/ompl_planning.yaml`](ros2_ws/src/kit_mp_bringup/config/ompl_planning.yaml)
- **Scenes you can swap** — [`ros2_ws/src/kit_mp_scenes/`](ros2_ws/src/kit_mp_scenes/)
- **The task API you edit (`student_solution.py`)** — [`ros2_ws/src/kit_mp_task_api/`](ros2_ws/src/kit_mp_task_api/)
- **Scoring & benchmarking** — [`ros2_ws/src/kit_mp_benchmark/`](ros2_ws/src/kit_mp_benchmark/)
- **GPU track (cuMotion + Isaac Sim)** — [`ros2_ws/src/kit_mp_curobo/`](ros2_ws/src/kit_mp_curobo/), [`ros2_ws/src/kit_mp_isaac/`](ros2_ws/src/kit_mp_isaac/)
- **What to submit** — [`submission/`](submission/)
- **Docs** — [`docs/`](docs/)

## Documentation

1. [Overview & learning goals](docs/00_overview.md)
2. [Install — CORE track](docs/01_install_core.md)
3. [Install — ADVANCED (GPU) track](docs/02_install_gpu.md)
4. [The OMPL playground: planners & hyperparameters](docs/03_ompl_playground.md)
5. [Benchmarking planners](docs/04_benchmarking.md)
6. [The competition](docs/05_competition.md)
7. [Troubleshooting](docs/06_troubleshooting.md)

The exercise sheet itself (with the graded questions) is distributed as a PDF alongside the
lecture. This repository is the software you use to answer it.

## Acknowledgements & licenses

This exercise builds on MoveIt 2, OMPL, `franka_ros2`, NVIDIA Isaac Sim, and cuRobo. See
[ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md). Exercise code is MIT-licensed; vendored third-party
components keep their own licenses.
