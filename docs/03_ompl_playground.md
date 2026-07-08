# The OMPL playground: planners & hyperparameters

Everything here is tuned in
[`kit_mp_bringup/config/ompl_planning.yaml`](../ros2_ws/src/kit_mp_bringup/config/ompl_planning.yaml).
Edit, relaunch (or re-score), observe.

## The planners

| Planner | Family | Character |
|---|---|---|
| `RRTConnect` | bidirectional RRT | fast, finds *a* path; not optimized. Great default. |
| `RRT` | single-tree RRT | simpler, usually slower than RRTConnect. |
| `RRTstar` | optimal RRT | keeps shortening the path with more time. |
| `PRM` / `PRMstar` | roadmap | builds a reusable graph; `*` is asymptotically optimal. |
| `LazyPRMstar` | lazy roadmap | defers collision checks; fast in cheap-to-check scenes. |
| `BiTRRT` | cost-aware RRT | good in clutter; balances exploration vs cost. |
| `EST` / `SBL` | expansive/lazy | alternative exploration strategies. |
| `KPIECE` | cell-based | discretizes the space; strong in high-DoF. |
| `AITstar` / `ABITstar` | anytime optimal | near-optimal quickly; strong "fast trajectory" picks. |

Switch the active planner by editing `default_planner_config` under `fr3_arm`, or
pick it from the RViz **OMPL** dropdown.

## The hyperparameters that matter

- **`range`** — the maximum length of one tree extension (rad in C-space).
  - *Too small*: fine control, but slow and many nodes.
  - *Too large*: fast, but can tunnel through thin obstacles or fail in clutter.
  - `0.0` lets OMPL auto-pick; a good first experiment is to set it explicitly.
- **`goal_bias`** — probability (0–1) of sampling the goal directly.
  - High in open space → reaches the goal fast.
  - High in mazes / `narrow_passage` → gets stuck; lower it.
- **`allowed_planning_time`** (set per request via the task API) — for the
  `*`-optimal planners (RRTstar, PRMstar, AITstar) more time buys a **shorter
  trajectory**. This is the key lever for the competition, traded against planning
  time (the tie-break metric).
- **`longest_valid_segment_fraction`** — how finely the motion between two states
  is collision-checked. Smaller = safer but slower. If "valid" plans clip
  obstacles, lower it.
- **`max_velocity_scaling_factor` / `max_acceleration_scaling_factor`** (task API,
  0–1) — scale the timing. Lower = slower motion = longer duration. You cannot
  exceed the FR3 limits; the scorer enforces them.

## Experiments to try (Exercises 2–3)

1. Same task, swap `RRTConnect → RRTstar → PRMstar → BiTRRT → AITstar`. Record
   planning time, trajectory duration. Which is fastest to plan? Which gives the
   shortest motion?
2. Fix `RRTstar`, sweep `allowed_planning_time` = 1, 3, 5, 10 s. Plot duration vs
   time. Where are the diminishing returns?
3. In `narrow_passage`, compare a high vs low `goal_bias`. Explain the difference.
4. Across the three scenes (`cluttered_table`, `shelf`, `narrow_passage`), argue
   which planner you would pick for each and why.

Then quantify it: [benchmarking](04_benchmarking.md).
