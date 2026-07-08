# Overview & learning goals

## What this exercise is about

You will build intuition for **motion planning in manipulation**: how a robot arm
turns a goal (a pose or a joint configuration) into a collision-free, smooth,
dynamically feasible trajectory. You work with the same tools used in research and
industry: **MoveIt 2**, the **OMPL** sampling-based planners, NVIDIA **cuRobo /
cuMotion**, and **Isaac Sim** on a **Franka Research 3** arm.

## Learning goals

By the end you should be able to:

1. **Explain** the planning pipeline: inverse kinematics → collision checking →
   geometric planning → trajectory optimization (this mirrors the lecture).
2. **Describe** how different algorithms search the configuration space and how
   that shows up in planning time, path length, and trajectory duration.
3. **Judge** which planner and which hyperparameters suit a given scene, using
   evidence from the benchmark harness.
4. **Compose** a competition entry: a planner + hyperparameters that produce the
   fastest *valid* trajectory on a fixed task.

## The two tracks

- **CORE** (everyone, no GPU): OMPL planners in MoveIt 2, visualized in RViz, run
  with a CPU mock controller. All of Exercises 1–4 and the whole competition run
  here.
- **ADVANCED** (optional, needs an NVIDIA GPU): high-fidelity execution in Isaac
  Sim and GPU planning with cuMotion (Exercise 5).

## The competition

The three groups whose entry produces the **shortest valid trajectory duration**
on the fixed competition task get to run it on the **real Franka Research 3**.
See [05_competition.md](05_competition.md).

## Suggested path

1. [Install the CORE track](01_install_core.md) and get a first plan.
2. Work through the exercise sheet (PDF from the lecture) using
   [the OMPL playground guide](03_ompl_playground.md).
3. Compare planners with [the benchmark](04_benchmarking.md).
4. Build and score your [competition entry](05_competition.md).
5. If you have a GPU, try the [advanced track](02_install_gpu.md).
