# Runs the competition scorer as a MoveItPy node. The node NAME must be "scorer"
# so MoveItPy(node_name="scorer") picks up the MoveIt parameters set here.
#
#   ros2 launch kit_mp_benchmark competition.launch.py output:=/root/results/results.json group:=team_x

import os
import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


def launch_setup(context, *args, **kwargs):
    output = LaunchConfiguration("output").perform(context)
    group = LaunchConfiguration("group").perform(context)
    reps = LaunchConfiguration("reps").perform(context)

    bringup_share = get_package_share_directory("kit_mp_bringup")

    moveit_config = (
        MoveItConfigsBuilder("fr3", package_name="franka_fr3_moveit_config")
        .robot_description(mappings={"robot_ip": "dont-care", "use_fake_hardware": "true"})
        .planning_pipelines(pipelines=["ompl"], default_planning_pipeline="ompl")
        .to_moveit_configs()
    )

    with open(os.path.join(bringup_share, "config", "ompl_planning.yaml")) as f:
        ompl_override = {"ompl": yaml.safe_load(f)}
    with open(os.path.join(bringup_share, "config", "joint_limits.yaml")) as f:
        joint_limits = yaml.safe_load(f)

    scorer = Node(
        name="scorer",
        package="kit_mp_benchmark",
        executable="scorer",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            ompl_override,
            {"robot_description_planning": joint_limits},
        ],
        arguments=["--output", output, "--group", group, "--reps", reps],
    )
    return [scorer]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("output", default_value="/root/results/results.json"),
        DeclareLaunchArgument("group", default_value="local"),
        DeclareLaunchArgument("reps", default_value="10"),
        OpaqueFunction(function=launch_setup),
    ])
