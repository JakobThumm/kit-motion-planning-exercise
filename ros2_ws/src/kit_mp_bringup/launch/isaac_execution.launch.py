# ADVANCED track launch: MoveIt move_group configured to EXECUTE on Isaac Sim
# (or the real FR3) instead of the CPU mock controller.
#
# Isaac Sim runs in its own container (docker compose service `isaac`) and provides
# the /joint_states and the fr3_arm_controller/follow_joint_trajectory action over
# DDS. So here we do NOT start ros2_control mock hardware; Isaac is the "hardware".
#
# Prerequisite: the isaac service is up (./docker/run_isaac.sh) and shares
# ROS_DOMAIN_ID with this container.

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
    scene = LaunchConfiguration("scene").perform(context)
    bringup_share = get_package_share_directory("kit_mp_bringup")

    moveit_config = (
        MoveItConfigsBuilder("fr3", package_name="franka_fr3_moveit_config")
        .robot_description(mappings={"robot_ip": "dont-care", "use_fake_hardware": "true"})
        .planning_pipelines(pipelines=["ompl"], default_planning_pipeline="ompl")
        .trajectory_execution(
            file_path=os.path.join(bringup_share, "config", "moveit_controllers.yaml")
        )
        .to_moveit_configs()
    )

    with open(os.path.join(bringup_share, "config", "ompl_planning.yaml")) as f:
        ompl_override = {"ompl": yaml.safe_load(f)}
    with open(os.path.join(bringup_share, "config", "joint_limits.yaml")) as f:
        joint_limits = yaml.safe_load(f)

    # Force the SIMPLE controller manager (FollowJointTrajectory over DDS to Isaac).
    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            ompl_override,
            {"robot_description_planning": joint_limits},
            {"moveit_controller_manager":
             "moveit_simple_controller_manager/MoveItSimpleControllerManager"},
        ],
    )

    rsp_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[moveit_config.robot_description],
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="log",
        arguments=["-d", os.path.join(bringup_share, "rviz", "exercise.rviz")],
        parameters=[
            moveit_config.robot_description,
            moveit_config.robot_description_semantic,
            moveit_config.robot_description_kinematics,
            moveit_config.planning_pipelines,
        ],
    )

    scene_loader = Node(
        package="kit_mp_scenes",
        executable="scene_loader",
        output="screen",
        parameters=[{"scene": scene}],
    )

    nodes = [rsp_node, move_group_node]
    if scene:
        nodes.append(scene_loader)
    if use_rviz.lower() == "true":
        nodes.append(rviz_node)
    return nodes


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("use_rviz", default_value="true"),
        DeclareLaunchArgument("scene", default_value="competition"),
        OpaqueFunction(function=launch_setup),
    ])
