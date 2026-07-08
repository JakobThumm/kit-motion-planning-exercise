# CORE track launch: FR3 + MoveIt 2 + RViz (CPU only, no GPU).
#
# You do NOT need to edit this file. It loads the FR3 model and the MoveIt
# move_group with YOUR planner settings from config/ompl_planning.yaml and
# config/stomp_planning.yaml (mounted live from the host).
#
# This is a PLANNING setup: move_group + RViz. RViz "Plan" shows the trajectory.
# (Full "Plan & Execute" on a controller is handled on the Isaac / real-FR3 track;
#  the competition is scored on the planned trajectory, so no controller is needed.)

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from kit_mp_task_api.moveit_params import moveit_params, fr3_robot_description


def launch_setup(context, *args, **kwargs):
    use_rviz = LaunchConfiguration("use_rviz").perform(context)
    scene = LaunchConfiguration("scene").perform(context)
    bringup_share = get_package_share_directory("kit_mp_bringup")

    params = moveit_params()
    robot_description = fr3_robot_description()

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=params,
    )

    rsp_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description],
    )

    # Publishes a (valid, default) joint state so move_group knows the start state
    # for interactive planning in RViz. The scorer sets the start state explicitly
    # and does not rely on this.
    jsp_node = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        output="log",
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        output="log",
        arguments=["-d", os.path.join(bringup_share, "rviz", "exercise.rviz")],
        parameters=[robot_description] + moveit_params(),
    )

    scene_loader = Node(
        package="kit_mp_scenes",
        executable="scene_loader",
        output="screen",
        parameters=[{"scene": scene}],
    )

    nodes = [rsp_node, jsp_node, move_group_node]
    if scene:
        nodes.append(scene_loader)
    if use_rviz.lower() == "true":
        nodes.append(rviz_node)
    return nodes


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("use_rviz", default_value="true"),
        DeclareLaunchArgument(
            "scene",
            default_value="empty",
            description="Scene from kit_mp_scenes. run_task also loads its task's scene.",
        ),
        OpaqueFunction(function=launch_setup),
    ])
