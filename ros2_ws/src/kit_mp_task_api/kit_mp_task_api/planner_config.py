"""PlannerConfig: the choices a group makes for a submission.

Per-planner numeric hyperparameters (range, goal_bias, ...) live in
kit_mp_bringup/config/ompl_planning.yaml. This object selects WHICH planner runs
and the request-level knobs (planning time, velocity/acceleration scaling).
"""
from dataclasses import asdict, dataclass


@dataclass
class PlannerConfig:
    # Pipeline: "ompl" (CORE) or "isaac_ros_cumotion" (ADVANCED, GPU).
    pipeline_id: str = "ompl"
    # Planner name; must exist in ompl_planning.yaml (ignored for cuMotion).
    planner_id: str = "RRTConnect"

    allowed_planning_time: float = 5.0
    num_planning_attempts: int = 1

    # Scaling in [0, 1]. Lower = slower motion. Cannot exceed the FR3 limits.
    max_velocity_scaling_factor: float = 1.0
    max_acceleration_scaling_factor: float = 1.0

    def to_dict(self) -> dict:
        return asdict(self)
