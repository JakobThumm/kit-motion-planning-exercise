# Runs the planner-comparison sweep as a MoveItPy node (Exercise 5). No controllers.
#   ros2 launch kit_mp_benchmark benchmark.launch.py task:=task_01_reach reps:=10
# Then render charts:
#   ros2 run kit_mp_benchmark plot -- --input results/benchmark.json --out results/

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

from kit_mp_task_api.moveit_params import moveit_params


def launch_setup(context, *args, **kwargs):
    task = LaunchConfiguration("task").perform(context)
    reps = LaunchConfiguration("reps").perform(context)
    specs = LaunchConfiguration("specs").perform(context)
    output = LaunchConfiguration("output").perform(context)

    node = Node(
        name="benchmark",
        package="kit_mp_benchmark",
        executable="benchmark_sweep",
        output="screen",
        parameters=moveit_params(moveit_cpp=True),
        arguments=["--task", task, "--reps", reps,
                   "--specs", specs, "--output", output],
    )
    return [node]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("task", default_value="task_01_reach"),
        DeclareLaunchArgument("reps", default_value="10"),
        DeclareLaunchArgument(
            "specs",
            default_value=("ompl:RRTConnect,ompl:RRTstar,ompl:PRMstar,"
                           "ompl:BiTRRT,ompl:KPIECE,ompl:AITstar,stomp")),
        DeclareLaunchArgument("output", default_value="/root/results/benchmark.json"),
        OpaqueFunction(function=launch_setup),
    ])
