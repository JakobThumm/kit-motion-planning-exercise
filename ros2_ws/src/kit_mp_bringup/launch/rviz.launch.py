# Standalone RViz with the exercise MotionPlanning config. Use when move_group is
# already running (e.g. started elsewhere) and you only want the GUI.
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


def generate_launch_description():
    bringup_share = get_package_share_directory("kit_mp_bringup")
    moveit_config = (
        MoveItConfigsBuilder("fr3", package_name="franka_fr3_moveit_config")
        .robot_description(mappings={"robot_ip": "dont-care", "use_fake_hardware": "true"})
        .planning_pipelines(pipelines=["ompl"])
        .to_moveit_configs()
    )
    return LaunchDescription([
        Node(
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
    ])
