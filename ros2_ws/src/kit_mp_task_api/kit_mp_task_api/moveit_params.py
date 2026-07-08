"""Assemble the FR3 MoveIt parameters in ONE place.

franka splits the robot across packages (URDF + SRDF in franka_description,
configs in franka_fr3_moveit_config), so MoveItConfigsBuilder's auto-inference
does not work. We build the parameters manually, mirroring franka's own
moveit.launch.py, and every launch file imports this single helper.

For PLANNING and SCORING no controllers / ros2_control are needed: move_group and
MoveItPy only need the robot description, semantic, kinematics, joint limits, and
the planning-pipeline configs. Execution controllers are a separate concern
(Isaac / real FR3 / an optional mock block for interactive RViz).
"""
import os

import xacro
import yaml
from ament_index_python.packages import get_package_share_directory


def _xacro(path, mappings):
    return xacro.process_file(path, mappings=mappings).toxml()


def _yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def _bringup_cfg(filename):
    """Load a kit_mp_bringup config, preferring the live host-mounted copy."""
    mounted = os.environ.get("KIT_MP_SRC", "")
    path = os.path.join(mounted, "kit_mp_bringup", "config", filename)
    if not (mounted and os.path.isfile(path)):
        path = os.path.join(
            get_package_share_directory("kit_mp_bringup"), "config", filename)
    return _yaml(path)


def fr3_robot_description(hand: str = "true", ee_id: str = "franka_hand") -> dict:
    desc = get_package_share_directory("franka_description")
    urdf = _xacro(
        os.path.join(desc, "robots", "fr3", "fr3.urdf.xacro"),
        {"hand": hand, "ee_id": ee_id},
    )
    return {"robot_description": urdf}


def fr3_robot_description_semantic(hand: str = "true",
                                   ee_id: str = "franka_hand") -> dict:
    desc = get_package_share_directory("franka_description")
    srdf = _xacro(
        os.path.join(desc, "robots", "fr3", "fr3.srdf.xacro"),
        {"hand": hand, "ee_id": ee_id},
    )
    return {"robot_description_semantic": srdf}


def moveit_params(pipelines=("ompl", "stomp"),
                  default_pipeline="ompl",
                  extra_pipelines=None,
                  moveit_cpp=False):
    """Full parameter list for a move_group / MoveItPy node.

    extra_pipelines: optional {name: config_dict} to register additional pipelines
    (e.g. {"isaac_ros_cumotion": {...}} on the GPU track).
    moveit_cpp: set True for MoveItPy/MoveItCpp consumers (the scorer, the
    benchmark sweep). MoveItCpp reads the pipeline list from
    `planning_pipelines.pipeline_names`, whereas the move_group executable reads a
    flat `planning_pipelines` list. Same configs, different key layout.
    Returns a list of dicts suitable for a launch_ros Node `parameters=`.
    """
    mcfg = get_package_share_directory("franka_fr3_moveit_config")

    params = [
        fr3_robot_description(),
        fr3_robot_description_semantic(),
        {"robot_description_kinematics":
         _yaml(os.path.join(mcfg, "config", "kinematics.yaml"))},
        {"robot_description_planning": _bringup_cfg("joint_limits.yaml")},
    ]

    pipeline_names = list(pipelines)
    pipeline_cfgs = {
        "ompl": _bringup_cfg("ompl_planning.yaml"),
        "stomp": _bringup_cfg("stomp_planning.yaml"),
    }
    if extra_pipelines:
        for name, cfg in extra_pipelines.items():
            pipeline_cfgs[name] = cfg
            if name not in pipeline_names:
                pipeline_names.append(name)

    # MoveItCpp/MoveItPy reads default PlanRequestParameters from
    # `<pipeline>.plan_request_params.*`; provide them to avoid a wall of
    # "parameter not found, using default" warnings. solve.py overrides per plan.
    for name in pipeline_names:
        cfg = pipeline_cfgs.setdefault(name, {})
        cfg.setdefault("plan_request_params", {
            "planning_pipeline": name,
            "planner_id": "RRTConnect" if name == "ompl" else "",
            "planning_time": 5.0,
            "planning_attempts": 1,
            "max_velocity_scaling_factor": 1.0,
            "max_acceleration_scaling_factor": 1.0,
        })

    if moveit_cpp:
        params.append({"planning_pipelines": {
            "pipeline_names": pipeline_names,
            "default_planning_pipeline": default_pipeline,
        }})
    else:
        params.append({"planning_pipelines": pipeline_names,
                       "default_planning_pipeline": default_pipeline})
    for name in pipeline_names:
        if name in pipeline_cfgs:
            params.append({name: pipeline_cfgs[name]})

    # Planning-only: don't require a controller manager (no execution here).
    params.append({
        "moveit_manage_controllers": False,
        "trajectory_execution.allowed_start_tolerance": 0.01,
        "publish_planning_scene": True,
        "publish_geometry_updates": True,
        "publish_state_updates": True,
        "publish_transforms_updates": True,
        "publish_robot_description_semantic": True,
    })
    return params
