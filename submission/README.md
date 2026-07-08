# Submitting your competition entry

Your goal: the **shortest valid trajectory duration** on the fixed competition task
(tie-break: planning time). Valid = collision-free, reaches the goal, and within the
FR3 position/velocity/acceleration/jerk limits. **The top 3 groups run on the real
Franka Research 3.**

## What to submit

Copy the `TEMPLATE/` folder, rename it to your group name, and fill it in:

```
submission/<your_group>/
├── submission.yaml        # group name + your chosen planner and settings
├── student_solution.py    # your edited kit_mp_task_api/student_solution.py
├── ompl_planning.yaml     # your edited kit_mp_bringup/config/ompl_planning.yaml
└── results.json           # produced by ./scripts/score_local.sh
```

## Steps

1. Tune `ompl_planning.yaml` (per-planner hyperparameters) and `student_solution.py`
   (which planner + scaling).
2. Score it: `./scripts/score_local.sh <your_group>` → writes `results/results.json`.
3. Copy the two edited files + `results/results.json` + a filled `submission.yaml`
   into `submission/<your_group>/`.
4. Commit / hand in as instructed.

## Rules

- You may **not** edit the competition task, scene, or `joint_limits` — the scorer
  uses its own locked copies, so tampering only makes your local number lie.
- `max_velocity_scaling_factor` / `max_acceleration_scaling_factor` must be in `[0, 1]`.
- The instructor re-scores your submission deterministically with
  `scripts/validate_submission.py`; only a **valid** entry is eligible.
