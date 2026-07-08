# Benchmarking planners (Exercise 4)

Comparing planners by eye in RViz is not enough. Run them many times and look at
the statistics.

## The built-in sweep (recommended)

Runs every curated planner N times on one task/scene, validates each result, and
records success rate, median planning time, and median trajectory duration.

```bash
# CPU core track
./run_core.sh ros2 launch kit_mp_benchmark benchmark.launch.py \
    task:=task_01_reach reps:=10

# Render the comparison charts
./run_core.sh ros2 run kit_mp_benchmark plot -- \
    --input /root/results/benchmark.json --out /root/results/
```

You get `results/planner_comparison.png` (and `.pdf`): trajectory duration and
planning time per planner, annotated with success rate.

Change the planner set or scene:

```bash
ros2 launch kit_mp_benchmark benchmark.launch.py \
    task:=task_02_shelf_pick reps:=20 \
    planners:=RRTConnect,RRTstar,AITstar
```

The sweep uses the same planning path as the scorer, so it also works for cuMotion
(`--pipeline isaac_ros_cumotion`) on the advanced track — this is how you compare
OMPL vs the GPU planner head to head.

## The official OMPL Planner Arena (optional, deeper stats)

MoveIt ships `moveit_ros_benchmarks`, which produces the rich OMPL Planner Arena
database (path length, smoothness, clearance, solve-time distributions).

```bash
ros2 run moveit_ros_benchmarks moveit_run_benchmark --ros-args \
    --params-file $(ros2 pkg prefix kit_mp_benchmark)/share/kit_mp_benchmark/config/benchmark.yaml
# logs land in /tmp/moveit_benchmarks/
ros2 run moveit_ros_benchmarks moveit_benchmark_statistics.py /tmp/moveit_benchmarks/<log>
```

Upload the resulting database to <https://plannerarena.org> for interactive plots.
Note: the official executor is OMPL-oriented and needs a warehouse of scenes/queries;
use it for the OMPL comparison, and the built-in sweep for OMPL-vs-cuMotion.

## What to report

- A ranked table / chart of planners by median trajectory duration on the
  competition scene.
- The planning-time cost of each.
- A one-paragraph recommendation: which planner + settings you will submit, and why.
