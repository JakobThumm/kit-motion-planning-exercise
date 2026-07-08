"""Plan a Task with a PlannerConfig via MoveItPy.

This is the single planning entry point used by both the interactive demo and the
competition scorer. It is planner-agnostic: it just runs whatever pipeline/planner
the PlannerConfig names and times the call.
"""
import time

from geometry_msgs.msg import PoseStamped
from moveit.core.robot_state import RobotState
from moveit.planning import MoveItPy, PlanRequestParameters

from kit_mp_task_api.planner_config import PlannerConfig
from kit_mp_task_api.task import Task


def make_moveit(node_name: str = "kit_mp_solver", config_dict: dict = None) -> MoveItPy:
    """Create a MoveItPy instance (spins its own move_group internally)."""
    if config_dict is None:
        return MoveItPy(node_name=node_name)
    return MoveItPy(node_name=node_name, config_dict=config_dict)


def _apply_start(arm, robot_model, task: Task):
    if task.start_joints is not None:
        rs = RobotState(robot_model)
        rs.set_joint_group_positions(task.group, task.start_joints)
        rs.update()
        arm.set_start_state(robot_state=rs)
    else:
        arm.set_start_state_to_current_state()


def _apply_goal(arm, robot_model, task: Task):
    if task.is_pose_goal:
        ps = PoseStamped()
        ps.header.frame_id = task.frame
        x, y, z, qx, qy, qz, qw = task.goal_pose
        ps.pose.position.x, ps.pose.position.y, ps.pose.position.z = x, y, z
        ps.pose.orientation.x, ps.pose.orientation.y = qx, qy
        ps.pose.orientation.z, ps.pose.orientation.w = qz, qw
        arm.set_goal_state(pose_stamped_msg=ps, pose_link=task.tip_link)
    else:
        rs = RobotState(robot_model)
        rs.set_joint_group_positions(task.group, task.goal_joints)
        rs.update()
        arm.set_goal_state(robot_state=rs)


def solve(moveit: MoveItPy, task: Task, cfg: PlannerConfig) -> dict:
    """Plan the task. Returns dict with success, trajectory, planning_time."""
    arm = moveit.get_planning_component(task.group)
    robot_model = moveit.get_robot_model()

    _apply_start(arm, robot_model, task)
    _apply_goal(arm, robot_model, task)

    params = PlanRequestParameters(moveit, cfg.pipeline_id)
    params.planning_pipeline = cfg.pipeline_id
    params.planner_id = cfg.planner_id
    params.planning_time = cfg.allowed_planning_time
    params.planning_attempts = cfg.num_planning_attempts
    params.max_velocity_scaling_factor = cfg.max_velocity_scaling_factor
    params.max_acceleration_scaling_factor = cfg.max_acceleration_scaling_factor

    t0 = time.perf_counter()
    result = arm.plan(single_plan_parameters=params)
    planning_time = time.perf_counter() - t0

    trajectory = getattr(result, "trajectory", None)
    success = trajectory is not None
    return {
        "success": success,
        "trajectory": trajectory,       # moveit RobotTrajectory (or None)
        "planning_time": planning_time,
        "planning_component": arm,
    }


def execute(moveit: MoveItPy, trajectory) -> bool:
    """Send a planned trajectory to the active controller (RViz mock / Isaac / FR3)."""
    return moveit.execute(trajectory, controllers=[])
