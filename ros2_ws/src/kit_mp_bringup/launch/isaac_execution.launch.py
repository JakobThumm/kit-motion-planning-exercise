# ADVANCED track launch: MoveIt move_group configured to EXECUTE on Isaac Sim
# (or the real FR3). Isaac runs in its own container and provides /joint_states
# and the fr3_arm_controller/follow_joint_trajectory action over DDS, so here we
# enable the simple controller manager (no ros2_control mock).
#
# Prerequisite: the isaac service is up (./docker/run_isaac.sh) with the same
# ROS_DOMAIN_ID.

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
    scene = LaunchConfiguration("scene").perform(context)
    bringup_share = get_package_share_directory("kit_mp_bringup")

    controllers = _yaml(os.path.join(bringup_share, "config",
                                     "moveit_controllers.yaml"))
    # Enable execution via the simple controller manager (Isaac provides the action).
    params = moveit_params() + [
        {"moveit_manage_controllers": True},
        {"moveit_simple_controller_manager":
            controllers.get("moveit_simple_controller_manager", {})},
        {"moveit_controller_manager":
            "moveit_simple_controller_manager/MoveItSimpleControllerManager"},
    ]
    robot_description = fr3_robot_description()

    move_group_node = Node(
        package="moveit_ros_move_group", executable="move_group",
        output="screen", parameters=params,
    )
    rsp_node = Node(
        package="robot_state_publisher", executable="robot_state_publisher",
        output="screen", parameters=[robot_description],
    )
    rviz_node = Node(
        package="rviz2", executable="rviz2", output="log",
        arguments=["-d", os.path.join(bringup_share, "rviz", "exercise.rviz")],
        parameters=[robot_description] + moveit_params(),
    )
    scene_loader = Node(
        package="kit_mp_scenes", executable="scene_loader",
        output="screen", parameters=[{"scene": scene}],
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
