# ADVANCED / GPU track: move_group with OMPL + STOMP + cuMotion pipelines, plus
# the cuMotion planner node that the cuMotion MoveIt plugin forwards to.
#
# Request a planner per plan via PlannerConfig(pipeline_id=...):
#   "ompl" / "stomp" (CPU) or "isaac_ros_cumotion" (GPU).
# Requires the GPU image (docker compose service `curobo`).

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from kit_mp_task_api.moveit_params import moveit_params, fr3_robot_description


def _yaml(path):
    import yaml
    with open(path) as f:
        return yaml.safe_load(f)


def launch_setup(context, *args, **kwargs):
    use_rviz = LaunchConfiguration("use_rviz").perform(context)
    bringup_share = get_package_share_directory("kit_mp_bringup")
    curobo_share = get_package_share_directory("kit_mp_curobo")

    cumotion_cfg = _yaml(os.path.join(bringup_share, "config",
                                      "cumotion_planning.yaml"))
    params = moveit_params(extra_pipelines={"isaac_ros_cumotion": cumotion_cfg})
    robot_description = fr3_robot_description()
    fr3_xrdf = os.path.join(curobo_share, "config", "fr3.xrdf")

    move_group = Node(
        package="moveit_ros_move_group", executable="move_group",
        output="screen", parameters=params,
    )
    # cuMotion planner node the MoveIt plugin talks to.
    cumotion_node = Node(
        package="isaac_ros_cumotion", executable="cumotion_planner_node",
        name="cumotion_planner", output="screen",
        parameters=[robot_description,
                    {"robot": fr3_xrdf, "time_dilation_factor": 1.0}],
    )
    rsp = Node(
        package="robot_state_publisher", executable="robot_state_publisher",
        output="screen", parameters=[robot_description],
    )
    nodes = [rsp, move_group, cumotion_node]
    if use_rviz.lower() == "true":
        nodes.append(Node(
            package="rviz2", executable="rviz2", output="log",
            arguments=["-d", os.path.join(bringup_share, "rviz", "exercise.rviz")],
            parameters=[robot_description] + moveit_params(),
        ))
    return nodes


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("use_rviz", default_value="true"),
        OpaqueFunction(function=launch_setup),
    ])
