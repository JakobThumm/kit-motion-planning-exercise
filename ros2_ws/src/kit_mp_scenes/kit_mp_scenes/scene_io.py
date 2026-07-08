"""Shared scene parsing: YAML scene files -> moveit_msgs CollisionObjects.

Reused by scene_loader (to populate move_group's planning scene) and by the scorer
(to validate a trajectory against the same geometry). One parser, one source of truth.

Scene YAML format::

    frame_id: base
    objects:
      - id: table
        type: box            # box | cylinder | sphere
        dims: [1.2, 0.8, 0.04]   # box: x,y,z | cylinder: height,radius | sphere: radius
        pose: {xyz: [0.5, 0.0, 0.2], rpy: [0.0, 0.0, 0.0]}
"""
import math
import os

import yaml
from ament_index_python.packages import get_package_share_directory
from geometry_msgs.msg import Pose
from moveit_msgs.msg import CollisionObject
from shape_msgs.msg import SolidPrimitive


def scenes_dir():
    return os.path.join(get_package_share_directory("kit_mp_scenes"), "scenes")


def scene_path(name):
    return os.path.join(scenes_dir(), f"{name}.yaml")


def load_scene_dict(name):
    with open(scene_path(name), "r") as f:
        return yaml.safe_load(f)


def _rpy_to_quat(roll, pitch, yaw):
    cy, sy = math.cos(yaw * 0.5), math.sin(yaw * 0.5)
    cp, sp = math.cos(pitch * 0.5), math.sin(pitch * 0.5)
    cr, sr = math.cos(roll * 0.5), math.sin(roll * 0.5)
    return (
        sr * cp * cy - cr * sp * sy,   # x
        cr * sp * cy + sr * cp * sy,   # y
        cr * cp * sy - sr * sp * cy,   # z
        cr * cp * cy + sr * sp * sy,   # w
    )


_PRIMITIVE = {
    "box": (SolidPrimitive.BOX, 3),
    "cylinder": (SolidPrimitive.CYLINDER, 2),
    "sphere": (SolidPrimitive.SPHERE, 1),
}


def build_collision_objects(scene, default_frame="base"):
    """Return (frame_id, [CollisionObject]) for a parsed scene dict."""
    frame_id = scene.get("frame_id", default_frame)
    objects = []
    for spec in scene.get("objects", []):
        ptype, ndims = _PRIMITIVE[spec["type"]]
        prim = SolidPrimitive()
        prim.type = ptype
        prim.dimensions = [float(d) for d in spec["dims"][:ndims]]

        pose = Pose()
        xyz = spec.get("pose", {}).get("xyz", [0.0, 0.0, 0.0])
        rpy = spec.get("pose", {}).get("rpy", [0.0, 0.0, 0.0])
        pose.position.x, pose.position.y, pose.position.z = (float(v) for v in xyz)
        qx, qy, qz, qw = _rpy_to_quat(*[float(v) for v in rpy])
        pose.orientation.x, pose.orientation.y = qx, qy
        pose.orientation.z, pose.orientation.w = qz, qw

        obj = CollisionObject()
        obj.header.frame_id = frame_id
        obj.id = spec["id"]
        obj.primitives = [prim]
        obj.primitive_poses = [pose]
        obj.operation = CollisionObject.ADD
        objects.append(obj)
    return frame_id, objects
