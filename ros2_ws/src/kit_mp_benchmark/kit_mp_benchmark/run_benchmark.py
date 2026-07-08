"""Compare several OMPL planners on the same task and scene (Exercise 4).

Runs each planner N times, records success rate, planning time, and trajectory
duration, and writes a JSON that plot.py turns into comparison charts. Planner-
agnostic (uses the same solve() path as the scorer), so it also works for the
cuMotion pipeline on the advanced track.

Launched via benchmark.launch.py (which supplies the MoveIt parameters):
    ros2 launch kit_mp_benchmark benchmark.launch.py task:=task_01_reach
"""
import argparse
import json
import os
import statistics
import sys

import rclpy

from kit_mp_scenes.scene_io import build_collision_objects, load_scene_dict
from kit_mp_task_api.planner_config import PlannerConfig
from kit_mp_task_api.solve import make_moveit, solve
from kit_mp_task_api.task import load_task

from kit_mp_benchmark import validate

# Each entry is "pipeline:planner". Bare "stomp" means the stomp pipeline (its
# single optimizer). This lets one sweep compare sampling-based OMPL planners
# against the optimization-based STOMP planner head to head.
DEFAULT_SPECS = [
    "ompl:RRTConnect", "ompl:RRTstar", "ompl:PRMstar",
    "ompl:BiTRRT", "ompl:KPIECE", "ompl:AITstar",
    "stomp",
]

_PIPELINES = {"stomp", "chomp", "pilz_industrial_motion_planner", "isaac_ros_cumotion"}


def parse_spec(spec):
    """'ompl:RRTConnect' -> ('ompl', 'RRTConnect'); 'stomp' -> ('stomp', '')."""
    if ":" in spec:
        pipe, planner = spec.split(":", 1)
        return pipe, planner
    if spec in _PIPELINES:
        return spec, ""
    return "ompl", spec


def _apply_scene(moveit, scene_name):
    scene = load_scene_dict(scene_name)
    _, objects = build_collision_objects(scene)
    psm = moveit.get_planning_scene_monitor()
    with psm.read_write() as s:
        for co in objects:
            s.apply_collision_object(co)
        s.current_state.update()


def sweep(task_name, specs, reps, planning_time, output_path):
    task = load_task(task_name)
    limits = validate.load_locked_limits()
    moveit = make_moveit(node_name="benchmark")
    robot_model = moveit.get_robot_model()
    _apply_scene(moveit, task.scene)

    summary = {}
    for spec in specs:
        pipe, planner = parse_spec(spec)
        cfg = PlannerConfig(pipeline_id=pipe, planner_id=planner,
                            allowed_planning_time=planning_time)
        exec_times, plan_times, successes = [], [], 0
        for _ in range(reps):
            res = solve(moveit, task, cfg)
            if not res["success"]:
                continue
            traj = res["trajectory"].get_robot_trajectory_msg()
            goal = validate.check_goal(traj, task, robot_model)
            lim = validate.check_limits(traj, limits)
            psm = moveit.get_planning_scene_monitor()
            with psm.read_only() as s:
                coll_ok, _ = validate.check_collision(
                    traj, s, robot_model, task.group)
            if goal["ok"] and lim["ok"] and coll_ok:
                successes += 1
                exec_times.append(validate.execution_time(traj))
                plan_times.append(res["planning_time"])
        summary[spec] = {
            "pipeline": pipe,
            "planner": planner,
            "success_rate": successes / reps if reps else 0.0,
            "median_exec_time_s":
                statistics.median(exec_times) if exec_times else None,
            "median_plan_time_s":
                statistics.median(plan_times) if plan_times else None,
            "valid_runs": successes,
            "reps": reps,
        }
        m = summary[spec]
        print(f"[bench] {spec:<16} success={m['success_rate']*100:5.1f}%  "
              f"exec={m['median_exec_time_s']}  plan={m['median_plan_time_s']}",
              flush=True)

    out = {"task": task_name, "scene": task.scene, "planners": summary}
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[bench] written to {output_path}", flush=True)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", default="task_01_reach")
    parser.add_argument("--specs", default=",".join(DEFAULT_SPECS),
                        help="comma list of pipeline:planner, e.g. ompl:RRTstar,stomp")
    parser.add_argument("--reps", type=int, default=10)
    parser.add_argument("--planning-time", type=float, default=5.0)
    parser.add_argument("--output", default="/root/results/benchmark.json")
    args, _ = parser.parse_known_args()

    rclpy.init(args=sys.argv)
    try:
        sweep(args.task, args.specs.split(","), args.reps,
              args.planning_time, args.output)
    finally:
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
