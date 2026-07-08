# =============================================================================
#  YOUR COMPETITION ENTRY  ---  EDIT THIS FILE
# =============================================================================
# Pick the planner and request-level settings for the competition task.
# Tune the per-planner numbers (range, goal_bias, ...) in
#   kit_mp_bringup/config/ompl_planning.yaml
# and select which planner runs here.
#
# Score your entry:  ./scripts/score_local.sh
# Submit:            copy this file + ompl_planning.yaml + results.json into
#                    submission/  (see submission/README.md)
# =============================================================================

from kit_mp_task_api.planner_config import PlannerConfig


def student_config() -> PlannerConfig:
    return PlannerConfig(
        # "ompl" (samplers) | "stomp" (optimizer) | "isaac_ros_cumotion" (GPU)
        pipeline_id="ompl",
        planner_id="RRTConnect",     # try RRTstar / PRMstar / BiTRRT / KPIECE / AITstar

        # More time lets the *-star planners shorten the trajectory. Costs planning
        # time (the tie-break metric), so there is a trade-off.
        allowed_planning_time=5.0,
        num_planning_attempts=1,

        # In [0, 1]. Full speed = fastest execution but least jerk headroom on the
        # real robot. The scorer enforces the FR3 limits and jerk-smooths the result.
        max_velocity_scaling_factor=1.0,
        max_acceleration_scaling_factor=1.0,
    )
