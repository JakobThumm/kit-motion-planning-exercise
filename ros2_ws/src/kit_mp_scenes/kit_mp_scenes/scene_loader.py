"""Node that loads a named collision scene into move_group's planning scene.

Usage (started by the launch files with the `scene` parameter)::

    ros2 run kit_mp_scenes scene_loader --ros-args -p scene:=cluttered_table
"""
import rclpy
from moveit_msgs.msg import PlanningScene
from moveit_msgs.srv import ApplyPlanningScene
from rclpy.node import Node

from kit_mp_scenes.scene_io import build_collision_objects, load_scene_dict


class SceneLoader(Node):
    def __init__(self):
        super().__init__("scene_loader")
        self.declare_parameter("scene", "cluttered_table")
        name = self.get_parameter("scene").get_parameter_value().string_value
        self.get_logger().info(f"Loading scene '{name}'")

        scene = load_scene_dict(name)
        _, objects = build_collision_objects(scene)

        msg = PlanningScene()
        msg.is_diff = True
        msg.world.collision_objects = objects

        self.client = self.create_client(ApplyPlanningScene, "/apply_planning_scene")
        if not self.client.wait_for_service(timeout_sec=15.0):
            self.get_logger().error("apply_planning_scene service unavailable; is move_group up?")
            return
        req = ApplyPlanningScene.Request()
        req.scene = msg
        future = self.client.call_async(req)
        future.add_done_callback(
            lambda f: self.get_logger().info(
                f"Scene '{name}' applied: {len(objects)} object(s)."
            )
        )


def main():
    rclpy.init()
    node = SceneLoader()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
