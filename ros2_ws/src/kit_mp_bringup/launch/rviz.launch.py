# Standalone RViz with the exercise MotionPlanning config. Use when move_group is
# already running and you only want the GUI.
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

from kit_mp_task_api.moveit_params import moveit_params, fr3_robot_description


def generate_launch_description():
    bringup_share = get_package_share_directory("kit_mp_bringup")
    return LaunchDescription([
        Node(
            package="rviz2",
            executable="rviz2",
            output="log",
            arguments=["-d", os.path.join(bringup_share, "rviz", "exercise.rviz")],
            parameters=[fr3_robot_description()] + moveit_params(),
        )
    ])
