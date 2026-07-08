"""Aggregate results.json files into a ranked leaderboard.

    ros2 run kit_mp_benchmark leaderboard -- --dir submission_results/

Ranks valid entries by execution_time_s (lower is better), tie-break planning_time_s.
Invalid entries are listed at the bottom. No ROS needed.
"""
import argparse
import glob
import json
import os


def collect(directory):
    entries = []
    for path in glob.glob(os.path.join(directory, "**", "results.json"), recursive=True):
        try:
            with open(path) as f:
                entries.append(json.load(f))
        except (json.JSONDecodeError, OSError):
            print(f"  skipping unreadable {path}")
    return entries


def rank(entries):
    valid = [e for e in entries if e.get("valid")]
    invalid = [e for e in entries if not e.get("valid")]
    valid.sort(key=lambda e: (e.get("execution_time_s", float("inf")),
                              e.get("planning_time_s", float("inf"))))
    return valid, invalid


def render(valid, invalid):
    print("\n" + "=" * 74)
    print(" KIT MOTION-PLANNING COMPETITION LEADERBOARD")
    print("=" * 74)
    print(f" {'#':>2}  {'group':<20} {'planner':<14} {'exec [s]':>9} {'plan [s]':>9}")
    print("-" * 74)
    for i, e in enumerate(valid, 1):
        marker = " *" if i <= 3 else "  "
        print(f"{marker}{i:>2}  {e.get('group','?'):<20} {e.get('planner_id','?'):<14} "
              f"{e.get('execution_time_s', float('inf')):>9.3f} "
              f"{e.get('planning_time_s', float('inf')):>9.3f}")
    if invalid:
        print("-" * 74)
        print(" INVALID (not eligible):")
        for e in invalid:
            print(f"     {e.get('group','?'):<20} {e.get('planner_id','?'):<14}  "
                  "(no valid trajectory)")
    print("=" * 74)
    print(" * = top 3 -> real Franka Research 3 run\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="results")
    parser.add_argument("--out", default="")
    args, _ = parser.parse_known_args()

    entries = collect(args.dir)
    valid, invalid = rank(entries)
    render(valid, invalid)
    if args.out:
        with open(args.out, "w") as f:
            json.dump({"ranking": valid, "invalid": invalid}, f, indent=2)
        print(f" written to {args.out}")


if __name__ == "__main__":
    main()
