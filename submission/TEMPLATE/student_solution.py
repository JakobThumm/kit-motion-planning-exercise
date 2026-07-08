# Paste your edited kit_mp_task_api/student_solution.py here (the version you scored).
from kit_mp_task_api.planner_config import PlannerConfig


def student_config() -> PlannerConfig:
    return PlannerConfig(
        pipeline_id="ompl",
        planner_id="RRTConnect",
        allowed_planning_time=5.0,
        num_planning_attempts=1,
        max_velocity_scaling_factor=1.0,
        max_acceleration_scaling_factor=1.0,
    )
