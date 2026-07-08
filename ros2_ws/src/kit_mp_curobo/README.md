# kit_mp_curobo — GPU planning with cuRobo / cuMotion

Adds NVIDIA cuMotion as a **second MoveIt planning pipeline** so you can compare a
GPU optimizer against the OMPL sampling-based planners in the *same* framework.

## How it plugs in

- `config/cumotion_planning.yaml` (in `kit_mp_bringup`) sets the pipeline's
  `planning_plugins` to `isaac_ros_cumotion_moveit/CumotionPlanner`.
- `launch/cumotion_planner.launch.py` starts `move_group` with **both** pipelines
  (`ompl` and `isaac_ros_cumotion`) and the `cumotion_planner_node` that the plugin
  forwards planning requests to.
- `config/fr3.xrdf` is the FR3 robot description cuRobo needs (collision spheres,
  cspace, jerk/acceleration limits, tool frame).

## Use it

```bash
./docker/run_gpu.sh ros2 launch kit_mp_curobo cumotion_planner.launch.py
```

Then request cuMotion per plan:

```python
PlannerConfig(pipeline_id="isaac_ros_cumotion")
```

Score a cuMotion entry:

```bash
# edit student_solution.py -> pipeline_id="isaac_ros_cumotion", then
./scripts/score_local.sh          # inside the curobo container
```

## The FR3 XRDF caveat

The stock `isaac_ros_cumotion` ships a **Panda** XRDF. `config/fr3.xrdf` adapts it
for FR3, but the collision spheres are an approximation. Verify and tune them with
the [XRDF tutorial](https://nvidia-isaac-ros.github.io/) before relying on cuMotion
collision avoidance on hardware — this is part of the advanced task.
