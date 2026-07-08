# Runs the planner-comparison sweep as a MoveItPy node (Exercise 4).
#   ros2 launch kit_mp_benchmark benchmark.launch.py task:=task_01_reach reps:=10
# Then render charts:
#   ros2 run kit_mp_benchmark plot -- --input results/benchmark.json --out results/

import os
import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


def launch_setup(context, *args, **kwargs):
    task = LaunchConfiguration("task").perform(context)
    reps = LaunchConfiguration("reps").perform(context)
    planners = LaunchConfiguration("planners").perform(context)
    output = LaunchConfiguration("output").perform(context)

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

    node = Node(
        name="benchmark",
        package="kit_mp_benchmark",
        executable="benchmark_sweep",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            ompl_override,
            {"robot_description_planning": joint_limits},
        ],
        arguments=["--task", task, "--reps", reps,
                   "--planners", planners, "--output", output],
    )
    return [node]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("task", default_value="task_01_reach"),
        DeclareLaunchArgument("reps", default_value="10"),
        DeclareLaunchArgument(
            "planners",
            default_value="RRTConnect,RRTstar,PRMstar,BiTRRT,KPIECE,AITstar"),
        DeclareLaunchArgument("output", default_value="/root/results/benchmark.json"),
        OpaqueFunction(function=launch_setup),
    ])
