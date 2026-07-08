# CORE track launch: FR3 + MoveIt 2 + RViz + mock (CPU-only) controllers.
#
# You do NOT need to edit this file. It wires the FR3 model, the MoveIt move_group,
# and RViz together, and loads YOUR planner settings from config/ompl_planning.yaml.
#
# What it starts:
#   * robot_state_publisher  (FR3 URDF -> TF)
#   * ros2_control_node with mock hardware (fake, no GPU) + joint_state_broadcaster
#   * fr3_arm_controller (joint_trajectory_controller) executes planned trajectories
#   * move_group           (MoveIt, OMPL pipeline with your ompl_planning.yaml)
#   * rviz2                (MotionPlanning panel)
#   * scene_loader         (loads the selected collision scene)

import os
import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from moveit_configs_utils import MoveItConfigsBuilder


def _load_yaml(package, rel_path):
    path = os.path.join(get_package_share_directory(package), rel_path)
    with open(path, "r") as f:
        return yaml.safe_load(f)


def launch_setup(context, *args, **kwargs):
    use_rviz = LaunchConfiguration("use_rviz").perform(context)
    scene = LaunchConfiguration("scene").perform(context)

    bringup_share = get_package_share_directory("kit_mp_bringup")

    # --- Assemble the FR3 MoveIt configuration --------------------------------
    moveit_config = (
        MoveItConfigsBuilder("fr3", package_name="franka_fr3_moveit_config")
        .robot_description(
            mappings={"robot_ip": "dont-care", "use_fake_hardware": "true"}
        )
        .planning_pipelines(pipelines=["ompl"], default_planning_pipeline="ompl")
        .trajectory_execution(
            file_path=os.path.join(bringup_share, "config", "moveit_controllers.yaml")
        )
        .to_moveit_configs()
    )

    # --- Override OMPL with the student-editable file (mounted live) -----------
    # Prefer the host-mounted copy if present, so edits apply without rebuilding.
    mounted = os.environ.get("KIT_MP_SRC", "")
    ompl_path = os.path.join(mounted, "kit_mp_bringup", "config", "ompl_planning.yaml")
    if not (mounted and os.path.isfile(ompl_path)):
        ompl_path = os.path.join(bringup_share, "config", "ompl_planning.yaml")
    with open(ompl_path, "r") as f:
        ompl_override = {"ompl": yaml.safe_load(f)}

    joint_limits = _load_yaml("kit_mp_bringup", "config/joint_limits.yaml")

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            ompl_override,                       # student settings win
            {"robot_description_planning": joint_limits},
            {"publish_robot_description_semantic": True},
        ],
    )

    rsp_node = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[moveit_config.robot_description],
    )

    ros2_controllers_path = os.path.join(
        bringup_share, "config", "ros2_controllers.yaml"
    )
    ros2_control_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[ros2_controllers_path],
        remappings=[("~/robot_description", "/robot_description")],
        output="screen",
    )

    spawners = [
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=[c, "--controller-manager", "/controller_manager"],
            output="screen",
        )
        for c in ["joint_state_broadcaster", "fr3_arm_controller"]
    ]

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
            {"robot_description_planning": joint_limits},
        ],
    )

    scene_loader = Node(
        package="kit_mp_scenes",
        executable="scene_loader",
        output="screen",
        parameters=[{"scene": scene}],
    )

    nodes = [rsp_node, ros2_control_node, *spawners, move_group_node]
    if scene:
        nodes.append(scene_loader)
    if use_rviz.lower() == "true":
        nodes.append(rviz_node)
    return nodes


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("use_rviz", default_value="true"),
            DeclareLaunchArgument(
                "scene",
                default_value="cluttered_table",
                description="Scene name from kit_mp_scenes (empty = none).",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
