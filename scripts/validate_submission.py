#!/usr/bin/env python3
"""Instructor tool: re-score a submitted entry and gate it for the real FR3.

Takes a submission folder (containing student_solution.py and ompl_planning.yaml),
installs those files into the workspace, re-runs the scorer deterministically in the
core container, and prints a PASS/FAIL with the real-robot safety verdict.

    python3 scripts/validate_submission.py submissions/team_x --group team_x

A submission is cleared for hardware ONLY if it is valid (collision-free, goal
reached, and within FR3 position/velocity/acceleration/JERK limits). Jerk matters:
libfranka aborts jerk-violating trajectories on the real robot.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRINGUP_CFG = os.path.join(REPO, "ros2_ws", "src", "kit_mp_bringup", "config")
TASK_API = os.path.join(REPO, "ros2_ws", "src", "kit_mp_task_api", "kit_mp_task_api")


def install_submission(sub_dir):
    sol = os.path.join(sub_dir, "student_solution.py")
    ompl = os.path.join(sub_dir, "ompl_planning.yaml")
    if not os.path.isfile(sol) or not os.path.isfile(ompl):
        sys.exit(f"submission must contain student_solution.py and ompl_planning.yaml")
    shutil.copy(sol, os.path.join(TASK_API, "student_solution.py"))
    shutil.copy(ompl, os.path.join(BRINGUP_CFG, "ompl_planning.yaml"))
    print(f"installed submission from {sub_dir}")


def rescore(group, reps):
    subprocess.run(
        ["bash", os.path.join(REPO, "scripts", "score_local.sh"), group, str(reps)],
        check=True,
    )
    with open(os.path.join(REPO, "results", "results.json")) as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("submission_dir")
    parser.add_argument("--group", default="submission")
    parser.add_argument("--reps", type=int, default=20)
    args = parser.parse_args()

    install_submission(args.submission_dir)
    result = rescore(args.group, args.reps)

    print("\n" + "=" * 60)
    print(f" Submission: {args.group}")
    print(f" planner    : {result['planner_id']} ({result['pipeline_id']})")
    print(f" valid      : {result['valid']}  ({result['valid_count']}/{result['repetitions']} runs)")
    print(f" exec time  : {result['execution_time_s']:.3f} s")
    print(f" plan time  : {result['planning_time_s']:.3f} s")
    limit_bad = any(r.get("limit_violations") for r in result.get("runs", []))
    hw_ok = result["valid"] and not limit_bad
    print("-" * 60)
    print(f" REAL-FR3 CLEARANCE: {'PASS' if hw_ok else 'FAIL'}")
    if hw_ok:
        print("  -> verify in Isaac Sim, then run on FR3 at reduced velocity first.")
    else:
        print("  -> NOT cleared. Do not run on hardware.")
    print("=" * 60)
    sys.exit(0 if hw_ok else 1)


if __name__ == "__main__":
    main()
