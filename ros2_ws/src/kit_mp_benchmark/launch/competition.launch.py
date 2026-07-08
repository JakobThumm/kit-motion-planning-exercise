# Runs the competition scorer as a MoveItPy node. Node NAME must be "scorer" so
# MoveItPy(node_name="scorer") picks up these MoveIt parameters. No controllers:
# the scorer plans in-process and scores the planned trajectory's duration.
#
#   ros2 launch kit_mp_benchmark competition.launch.py output:=/root/results/results.json group:=team_x

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from kit_mp_task_api.moveit_params import moveit_params


def launch_setup(context, *args, **kwargs):
    output = LaunchConfiguration("output").perform(context)
    group = LaunchConfiguration("group").perform(context)
    reps = LaunchConfiguration("reps").perform(context)

    scorer = Node(
        name="scorer",
        package="kit_mp_benchmark",
        executable="scorer",
        output="screen",
        parameters=moveit_params(),
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
