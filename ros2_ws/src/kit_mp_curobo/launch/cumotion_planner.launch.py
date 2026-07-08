# ADVANCED / GPU track: start move_group with BOTH the OMPL and cuMotion pipelines,
# plus the cuMotion planner node that the cuMotion MoveIt plugin forwards to.
#
# After this is up you can request either planner per plan:
#   PlannerConfig(pipeline_id="ompl", ...)                 # CPU planners
#   PlannerConfig(pipeline_id="isaac_ros_cumotion", ...)   # GPU cuMotion
#
# Requires the GPU image (docker compose service `curobo`).

import os
import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


def launch_setup(context, *args, **kwargs):
    use_rviz = LaunchConfiguration("use_rviz").perform(context)
    bringup_share = get_package_share_directory("kit_mp_bringup")
    curobo_share = get_package_share_directory("kit_mp_curobo")

    # Both pipelines registered on the same move_group.
    moveit_config = (
        MoveItConfigsBuilder("fr3", package_name="franka_fr3_moveit_config")
        .robot_description(mappings={"robot_ip": "dont-care", "use_fake_hardware": "true"})
        .planning_pipelines(
            pipelines=["ompl", "isaac_ros_cumotion"],
            default_planning_pipeline="ompl",
        )
        .trajectory_execution(
            file_path=os.path.join(bringup_share, "config", "moveit_controllers.yaml")
        )
        .to_moveit_configs()
    )

    with open(os.path.join(bringup_share, "config", "ompl_planning.yaml")) as f:
        ompl_override = {"ompl": yaml.safe_load(f)}
    with open(os.path.join(bringup_share, "config", "cumotion_planning.yaml")) as f:
        cumotion_override = {"isaac_ros_cumotion": yaml.safe_load(f)}
    with open(os.path.join(bringup_share, "config", "joint_limits.yaml")) as f:
        joint_limits = yaml.safe_load(f)

    fr3_xrdf = os.path.join(curobo_share, "config", "fr3.xrdf")

    move_group = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            ompl_override,
            cumotion_override,
            {"robot_description_planning": joint_limits},
        ],
    )

    # The cuMotion planner node the MoveIt plugin talks to.
    cumotion_node = Node(
        package="isaac_ros_cumotion",
        executable="cumotion_planner_node",
        name="cumotion_planner",
        output="screen",
        parameters=[
            {"robot": fr3_xrdf},
            {"urdf_path": moveit_config.robot_description},
            {"time_dilation_factor": 1.0},
        ],
    )

    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[moveit_config.robot_description],
    )

    nodes = [rsp, move_group, cumotion_node]
    if use_rviz.lower() == "true":
        nodes.append(Node(
            package="rviz2", executable="rviz2", output="log",
            arguments=["-d", os.path.join(bringup_share, "rviz", "exercise.rviz")],
            parameters=[
                moveit_config.robot_description,
                moveit_config.robot_description_semantic,
                moveit_config.robot_description_kinematics,
                moveit_config.planning_pipelines,
            ],
        ))
    return nodes


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("use_rviz", default_value="true"),
        OpaqueFunction(function=launch_setup),
    ])
