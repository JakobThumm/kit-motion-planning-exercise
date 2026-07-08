"""Competition scorer.

Plans the fixed competition task with the group's PlannerConfig, validates every
run, and reports the MEDIAN valid trajectory duration (the score) plus the best
planning time (tie-break). Writes results.json.

Launched via competition.launch.py, which supplies the MoveIt parameters. The task,
scene and locked limits are authoritative here: a student's PlannerConfig chooses
the planner and scaling, but cannot change the task, scene, or joint limits.

    ros2 launch kit_mp_benchmark competition.launch.py output:=/root/results/results.json
"""
import argparse
import json
import os
import statistics
import sys

import rclpy

from kit_mp_scenes.scene_io import build_collision_objects, load_scene_dict
from kit_mp_task_api.solve import make_moveit, solve
from kit_mp_task_api.task import load_task
from kit_mp_task_api.student_solution import student_config

from kit_mp_benchmark import validate


TASK_NAME = "competition_task"     # authoritative; not student-editable


def _apply_scene(moveit, scene_name):
    scene = load_scene_dict(scene_name)
    _, objects = build_collision_objects(scene)
    psm = moveit.get_planning_scene_monitor()
    with psm.read_write() as s:
        for co in objects:
            s.apply_collision_object(co)
        s.current_state.update()
    return len(objects)


def score(output_path, reps, group_name):
    task = load_task(TASK_NAME)
    cfg = student_config()
    limits = validate.load_locked_limits()

    moveit = make_moveit(node_name="scorer")
    robot_model = moveit.get_robot_model()
    n_obj = _apply_scene(moveit, task.scene)
    print(f"[scorer] scene '{task.scene}' loaded with {n_obj} objects", flush=True)

    runs = []
    for i in range(reps):
        res = solve(moveit, task, cfg)
        if not res["success"]:
            runs.append({"run": i, "valid": False, "reason": "planning_failed"})
            print(f"[scorer] run {i}: planning FAILED", flush=True)
            continue

        traj_msg = res["trajectory"].get_robot_trajectory_msg()
        exec_t = validate.execution_time(traj_msg)

        goal = validate.check_goal(traj_msg, task, robot_model)
        lim = validate.check_limits(traj_msg, limits)
        psm = moveit.get_planning_scene_monitor()
        with psm.read_only() as s:
            coll_ok, coll_idx = validate.check_collision(
                traj_msg, s, robot_model, task.group)

        valid = goal["ok"] and lim["ok"] and coll_ok
        runs.append({
            "run": i,
            "valid": valid,
            "execution_time_s": exec_t,
            "planning_time_s": res["planning_time"],
            "collision_free": coll_ok,
            "collision_index": coll_idx,
            "goal_reached": goal["ok"],
            "goal_detail": goal,
            "limits_ok": lim["ok"],
            "limit_violations": lim["violations"],
            "num_waypoints": len(traj_msg.joint_trajectory.points),
        })
        print(f"[scorer] run {i}: valid={valid} exec={exec_t:.3f}s "
              f"plan={res['planning_time']:.3f}s coll_free={coll_ok} "
              f"goal={goal['ok']} limits={lim['ok']}", flush=True)

    valid_runs = [r for r in runs if r.get("valid")]
    if valid_runs:
        median_exec = statistics.median(r["execution_time_s"] for r in valid_runs)
        best_plan = min(r["planning_time_s"] for r in valid_runs)
        overall_valid = True
    else:
        median_exec = float("inf")
        best_plan = float("inf")
        overall_valid = False

    result = {
        "group": group_name,
        "task": TASK_NAME,
        "scene": task.scene,
        "pipeline_id": cfg.pipeline_id,
        "planner_id": cfg.planner_id,
        "hyperparameters": cfg.to_dict(),
        "valid": overall_valid,
        "execution_time_s": median_exec,      # <-- PRIMARY SCORE (lower is better)
        "planning_time_s": best_plan,          # <-- tie-break
        "repetitions": reps,
        "valid_count": len(valid_runs),
        "runs": runs,
        "note": "per-planner hyperparameters are in ompl_planning.yaml (submit it too)",
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    print("\n" + "=" * 60, flush=True)
    if overall_valid:
        print(f"  SCORE: {median_exec:.3f} s  (tie-break plan {best_plan:.3f} s)", flush=True)
        print(f"  {len(valid_runs)}/{reps} runs valid  |  planner {cfg.planner_id}", flush=True)
    else:
        print("  INVALID: no valid trajectory (see runs in results.json)", flush=True)
    print(f"  written to {output_path}", flush=True)
    print("=" * 60, flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="/root/results/results.json")
    parser.add_argument("--reps", type=int, default=10)
    parser.add_argument("--group", default=os.environ.get("KIT_MP_GROUP", "local"))
    args, _ = parser.parse_known_args()

    rclpy.init(args=sys.argv)
    try:
        score(args.output, args.reps, args.group)
    finally:
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
