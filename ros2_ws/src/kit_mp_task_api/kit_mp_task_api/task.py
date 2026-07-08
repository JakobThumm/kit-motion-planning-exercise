"""Task definition: a planning problem (scene + start + goal + tolerances)."""
import os
from dataclasses import dataclass, field
from typing import List, Optional

import yaml
from ament_index_python.packages import get_package_share_directory


@dataclass
class Task:
    name: str
    group: str = "fr3_arm"
    scene: str = "empty"                       # kit_mp_scenes scene name
    tip_link: str = "fr3_hand_tcp"

    # Start: either a named configuration or explicit joint values (None = current).
    start_joints: Optional[List[float]] = None

    # Goal: give EITHER a pose (position + quaternion in `frame`) OR joint values.
    goal_pose: Optional[List[float]] = None    # [x, y, z, qx, qy, qz, qw]
    goal_joints: Optional[List[float]] = None
    frame: str = "base"

    # Tolerances for the goal-reached validity check.
    position_tolerance: float = 0.01           # metres
    orientation_tolerance: float = 0.05        # radians
    joint_tolerance: float = 0.01              # radians

    joint_names: List[str] = field(default_factory=lambda: [
        "fr3_joint1", "fr3_joint2", "fr3_joint3", "fr3_joint4",
        "fr3_joint5", "fr3_joint6", "fr3_joint7",
    ])

    @property
    def is_pose_goal(self) -> bool:
        return self.goal_pose is not None


def tasks_dir() -> str:
    return os.path.join(get_package_share_directory("kit_mp_task_api"), "tasks")


def load_task(name: str) -> Task:
    """Load a task by file stem, e.g. load_task('competition_task')."""
    path = name if os.path.isfile(name) else os.path.join(tasks_dir(), f"{name}.yaml")
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return Task(**data)
