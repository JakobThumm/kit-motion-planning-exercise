"""Plot planner-comparison charts from a benchmark.json (produced by run_benchmark).

    ros2 run kit_mp_benchmark plot -- --input results/benchmark.json --out results/

Renders two bar charts: median trajectory duration and median planning time, plus
a success-rate annotation. No ROS needed. Uses a non-interactive backend so it
works headless in the container.
"""
import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def plot(data, out_dir):
    planners = list(data["planners"].keys())
    exec_t = [data["planners"][p]["median_exec_time_s"] or 0.0 for p in planners]
    plan_t = [data["planners"][p]["median_plan_time_s"] or 0.0 for p in planners]
    succ = [data["planners"][p]["success_rate"] * 100 for p in planners]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    b1 = ax1.bar(planners, exec_t, color="#4c72b0")
    ax1.set_title(f"Trajectory duration (score) — {data['scene']}")
    ax1.set_ylabel("median execution time [s]")
    ax1.tick_params(axis="x", rotation=30)
    for bar, s in zip(b1, succ):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                 f"{s:.0f}%", ha="center", va="bottom", fontsize=8)

    ax2.bar(planners, plan_t, color="#dd8452")
    ax2.set_title("Planning (compute) time")
    ax2.set_ylabel("median planning time [s]")
    ax2.tick_params(axis="x", rotation=30)

    fig.suptitle(f"Planner comparison (sampling vs optimization) — "
                 f"task '{data['task']}'  (% = success rate)")
    fig.tight_layout()

    os.makedirs(out_dir, exist_ok=True)
    png = os.path.join(out_dir, "planner_comparison.png")
    pdf = os.path.join(out_dir, "planner_comparison.pdf")
    fig.savefig(png, dpi=150)
    fig.savefig(pdf)
    print(f"wrote {png}\nwrote {pdf}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="results/benchmark.json")
    parser.add_argument("--out", default="results")
    args, _ = parser.parse_known_args()
    with open(args.input) as f:
        data = json.load(f)
    plot(data, args.out)


if __name__ == "__main__":
    main()
