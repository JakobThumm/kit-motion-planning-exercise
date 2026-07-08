# The competition

## Goal

Produce the **shortest valid trajectory** on the fixed competition task. The three
fastest valid entries run on the **real Franka Research 3**.

## The task (fixed)

- Scene: `competition` (a shelf reach with a pillar and a box to avoid).
- Start: the FR3 "ready" pose. Goal: a fixed joint configuration on the far side.
- Defined in
  [`kit_mp_task_api/tasks/competition_task.yaml`](../ros2_ws/src/kit_mp_task_api/tasks/competition_task.yaml)
  and `kit_mp_scenes/scenes/competition.yaml`. You cannot change these; the scorer
  uses its own authoritative copies.

## The metric

**Score = median trajectory duration** over 10 scored runs (seconds; lower wins).
**Tie-break = best planning time.** An entry counts only if it is **valid**:

1. **Collision-free** at every (densified) waypoint against the competition scene.
2. **Reaches the goal** within tolerance.
3. **Within the FR3 limits** — position, velocity, acceleration, **and jerk**.

Jerk matters because the real robot (libfranka/FCI) rejects jerk-violating
trajectories. The pipeline applies jerk-limited (Ruckig) smoothing and the scorer
enforces the locked FR3 limits, so a valid local score transfers to hardware.

## What you tune

- **Planner + hyperparameters** in `ompl_planning.yaml`.
- **Which planner + scaling** in `student_solution.py`.
- Velocity/acceleration scaling in `[0, 1]` (can only slow you down, so this is a
  genuine path-quality contest, not a limits-raising contest).

You **cannot** win by editing joint limits, the task, or the scene — the scorer
ignores those and re-scores with locked copies.

## Score and submit

```bash
./scripts/score_local.sh myteam        # prints your score, writes results/results.json
```

Then follow [submission/README.md](../submission/README.md): copy your
`student_solution.py`, `ompl_planning.yaml`, `results.json`, and a filled
`submission.yaml` into `submission/<yourteam>/`.

## Instructor: ranking and the real-robot run

```bash
python3 scripts/validate_submission.py submission/<team> --group <team> --reps 20
ros2 run kit_mp_benchmark leaderboard -- --dir submission/
```

Real-FR3 procedure for the top 3 (safety first):

1. Re-score deterministically; confirm **valid** and within limits (jerk included).
2. Re-validate in **Isaac Sim** at reduced velocity scaling.
3. Run on the FR3 via `franka_fr3_moveit_config moveit.launch.py robot_ip:=<IP>
   use_fake_hardware:=false`, executing the validated trajectory, starting at
   reduced velocity scaling, operator on the enabling device, workspace limited.
   Only after a clean reduced-speed pass, run at the submitted scaling for the
   timed result.
