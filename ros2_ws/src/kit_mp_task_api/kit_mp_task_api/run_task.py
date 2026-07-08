"""Plan a named task on the RUNNING move_group so it shows up in RViz.

Run core.launch.py in one terminal (RViz + move_group), then in another:

    ros2 run kit_mp_task_api run_task task_01_reach --planner RRTConnect

It applies the task's scene, sends the start/goal to move_group via the MoveGroup
action with plan_only=True (no controller needed), and prints the planned
trajectory duration. RViz draws the planned path automatically.
"""
import argparse
import os
import sys

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from geometry_msgs.msg import Pose
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import (
    BoundingVolume,
    Constraints,
    JointConstraint,
    MotionPlanRequest,
    OrientationConstraint,
    PlanningScene,
    PositionConstraint,
)
from moveit_msgs.srv import ApplyPlanningScene
from shape_msgs.msg import SolidPrimitive

from kit_mp_scenes.scene_io import build_collision_objects, load_scene_dict
from kit_mp_task_api.planner_config import PlannerConfig
from kit_mp_task_api.student_solution import student_config
from kit_mp_task_api.task import load_task


def _goal_constraints(task):
    c = Constraints()
    if task.is_pose_goal:
        x, y, z, qx, qy, qz, qw = task.goal_pose
        pc = PositionConstraint()
        pc.header.frame_id = task.frame
        pc.link_name = task.tip_link
        sphere = SolidPrimitive(type=SolidPrimitive.SPHERE,
                                dimensions=[task.position_tolerance])
        region = BoundingVolume()
        region.primitives.append(sphere)
        pose = Pose()
        pose.position.x, pose.position.y, pose.position.z = x, y, z
        pose.orientation.w = 1.0
        region.primitive_poses.append(pose)
        pc.constraint_region = region
        pc.weight = 1.0

        oc = OrientationConstraint()
        oc.header.frame_id = task.frame
        oc.link_name = task.tip_link
        oc.orientation.x, oc.orientation.y = qx, qy
        oc.orientation.z, oc.orientation.w = qz, qw
        oc.absolute_x_axis_tolerance = task.orientation_tolerance
        oc.absolute_y_axis_tolerance = task.orientation_tolerance
        oc.absolute_z_axis_tolerance = task.orientation_tolerance
        oc.weight = 1.0
        c.position_constraints.append(pc)
        c.orientation_constraints.append(oc)
    else:
        for name, pos in zip(task.joint_names, task.goal_joints):
            jc = JointConstraint()
            jc.joint_name = name
            jc.position = float(pos)
            jc.tolerance_above = task.joint_tolerance
            jc.tolerance_below = task.joint_tolerance
            jc.weight = 1.0
            c.joint_constraints.append(jc)
    return c


class RunTask(Node):
    def __init__(self, task, cfg):
        super().__init__("run_task")
        self.task = task
        self.cfg = cfg

    def apply_scene(self):
        client = self.create_client(ApplyPlanningScene, "/apply_planning_scene")
        if not client.wait_for_service(timeout_sec=10.0):
            self.get_logger().warn("apply_planning_scene unavailable; keeping current scene")
            return
        _, objects = build_collision_objects(load_scene_dict(self.task.scene))
        scene = PlanningScene(is_diff=True)
        scene.world.collision_objects = objects
        req = ApplyPlanningScene.Request(scene=scene)
        fut = client.call_async(req)
        rclpy.spin_until_future_complete(self, fut, timeout_sec=10.0)
        self.get_logger().info(f"scene '{self.task.scene}': {len(objects)} object(s)")

    def plan(self):
        ac = ActionClient(self, MoveGroup, "/move_action")
        if not ac.wait_for_server(timeout_sec=15.0):
            self.get_logger().error("move_action server not found; is move_group running?")
            return False

        req = MotionPlanRequest()
        req.group_name = self.task.group
        req.pipeline_id = self.cfg.pipeline_id
        req.planner_id = self.cfg.planner_id
        req.num_planning_attempts = self.cfg.num_planning_attempts
        req.allowed_planning_time = self.cfg.allowed_planning_time
        req.max_velocity_scaling_factor = self.cfg.max_velocity_scaling_factor
        req.max_acceleration_scaling_factor = self.cfg.max_acceleration_scaling_factor
        if self.task.start_joints is not None:
            req.start_state.joint_state.name = self.task.joint_names
            req.start_state.joint_state.position = [float(p) for p in self.task.start_joints]
        else:
            req.start_state.is_diff = True
        req.goal_constraints.append(_goal_constraints(self.task))

        goal = MoveGroup.Goal()
        goal.request = req
        goal.planning_options.plan_only = True   # plan + display, do not execute
        goal.planning_options.planning_scene_diff.is_diff = True
        goal.planning_options.planning_scene_diff.robot_state.is_diff = True

        self.get_logger().info(
            f"planning '{self.task.name}' with {self.cfg.pipeline_id}/{self.cfg.planner_id}")
        send = ac.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, send, timeout_sec=20.0)
        handle = send.result()
        if handle is None or not handle.accepted:
            self.get_logger().error("goal not accepted (is move_group in this container?)")
            return False
        res_fut = handle.get_result_async()
        rclpy.spin_until_future_complete(
            self, res_fut, timeout_sec=self.cfg.allowed_planning_time + 30.0)
        if res_fut.result() is None:
            self.get_logger().error("no planning result (timed out)")
            return False
        result = res_fut.result().result

        if result.error_code.val != 1:  # SUCCESS
            self.get_logger().error(f"planning failed (error code {result.error_code.val})")
            return False
        pts = result.planned_trajectory.joint_trajectory.points
        dur = pts[-1].time_from_start.sec + pts[-1].time_from_start.nanosec * 1e-9 if pts else 0.0
        log = self.get_logger()
        log.info("=" * 50)
        log.info(f"  Planned '{self.task.name}'  |  {self.cfg.planner_id}")
        log.info(f"  trajectory duration: {dur:.3f} s   ({len(pts)} waypoints)")
        log.info("  (shown in RViz on the Planned Path display)")
        log.info("=" * 50)
        return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task", help="task name, e.g. task_01_reach")
    parser.add_argument("--planner", default=None, help="override OMPL planner id")
    parser.add_argument("--pipeline", default=None, help="ompl | stomp | isaac_ros_cumotion")
    args, _ = parser.parse_known_args()

    task = load_task(args.task)
    cfg = student_config()
    if args.planner or args.pipeline:
        cfg = PlannerConfig(
            pipeline_id=args.pipeline or cfg.pipeline_id,
            planner_id=args.planner or cfg.planner_id,
            allowed_planning_time=cfg.allowed_planning_time,
            num_planning_attempts=cfg.num_planning_attempts,
            max_velocity_scaling_factor=cfg.max_velocity_scaling_factor,
            max_acceleration_scaling_factor=cfg.max_acceleration_scaling_factor,
        )

    rclpy.init(args=sys.argv)
    node = RunTask(task, cfg)
    ok = False
    try:
        node.apply_scene()
        ok = node.plan()
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
    # Force exit: the action client can leave non-daemon threads that would
    # otherwise keep the process (and the docker exec) alive.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0 if ok else 1)


if __name__ == "__main__":
    main()
