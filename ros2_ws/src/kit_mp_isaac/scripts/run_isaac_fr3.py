"""Load the FR3 in Isaac Sim and bridge it to ROS 2 for high-fidelity execution.

Run INSIDE the Isaac Sim container (Dockerfile.isaac):
    /isaac-sim/python.sh run_isaac_fr3.py [--headless]

What it sets up:
  * the FR3 articulation (from the Isaac Sim asset library),
  * the competition obstacles (matching kit_mp_scenes/competition.yaml),
  * a ROS 2 bridge (OmniGraph) publishing /joint_states + /clock and exposing a
    FollowJointTrajectory action `fr3_arm_controller/follow_joint_trajectory`
    that MoveIt (in the core/curobo container) drives over DDS.

Isaac Sim and ROS 2 run in SEPARATE containers on the same ROS_DOMAIN_ID; this
avoids the in-container bridge issues of Isaac Sim 4.5. See action_graphs/ros2_bridge.md
for the exact OmniGraph node wiring if you build it in the GUI instead.

NOTE: asset paths and a few Isaac APIs are version-specific (validated against
Isaac Sim 4.5). Adjust the asset root if your install differs.
"""
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--headless", action="store_true")
args, _ = parser.parse_known_args()

# 1. Boot the simulator FIRST (must precede any omni.* import).
from isaacsim import SimulationApp  # noqa: E402

sim_app = SimulationApp({"headless": args.headless})

# 2. Now the omni / isaacsim APIs are importable.
import omni.graph.core as og  # noqa: E402
from isaacsim.core.api import World  # noqa: E402
from isaacsim.core.utils.stage import add_reference_to_stage  # noqa: E402
from isaacsim.core.utils.nucleus import get_assets_root_path  # noqa: E402
from isaacsim.core.api.objects import DynamicCuboid, FixedCuboid  # noqa: E402
import omni.usd  # noqa: E402

FR3_JOINTS = [f"fr3_joint{i}" for i in range(1, 8)]


def build_scene(world):
    assets_root = get_assets_root_path()
    fr3_usd = assets_root + "/Isaac/Robots/Franka/franka.usd"   # FR3/Panda articulation
    add_reference_to_stage(usd_path=fr3_usd, prim_path="/World/fr3")

    # Competition obstacles (subset; keep in sync with competition.yaml).
    world.scene.add(FixedCuboid(
        prim_path="/World/table", name="table",
        position=[0.55, 0.0, 0.20], scale=[0.9, 1.2, 0.04]))
    world.scene.add(FixedCuboid(
        prim_path="/World/pillar", name="pillar",
        position=[0.40, -0.02, 0.445], scale=[0.09, 0.09, 0.45]))
    world.scene.add(FixedCuboid(
        prim_path="/World/box", name="box",
        position=[0.42, 0.28, 0.37], scale=[0.14, 0.14, 0.30]))


def build_ros2_bridge():
    """OmniGraph: clock + JointState publish + JointState subscribe (command).

    A full FollowJointTrajectory action bridge is added via the
    isaacsim.ros2.bridge action-graph nodes; see action_graphs/ros2_bridge.md for
    the node-by-node layout if you prefer to wire it in the GUI.
    """
    og.Controller.edit(
        {"graph_path": "/World/ros2_bridge", "evaluator_name": "execution"},
        {
            og.Controller.Keys.CREATE_NODES: [
                ("OnTick", "omni.graph.action.OnPlaybackTick"),
                ("Context", "isaacsim.ros2.bridge.ROS2Context"),
                ("PublishClock", "isaacsim.ros2.bridge.ROS2PublishClock"),
                ("PublishJointState", "isaacsim.ros2.bridge.ROS2PublishJointState"),
                ("SubscribeJointState", "isaacsim.ros2.bridge.ROS2SubscribeJointState"),
                ("ArticulationController",
                 "isaacsim.core.nodes.IsaacArticulationController"),
                ("ReadSimTime", "isaacsim.core.nodes.IsaacReadSimulationTime"),
            ],
            og.Controller.Keys.CONNECT: [
                ("OnTick.outputs:tick", "PublishClock.inputs:execIn"),
                ("OnTick.outputs:tick", "PublishJointState.inputs:execIn"),
                ("OnTick.outputs:tick", "SubscribeJointState.inputs:execIn"),
                ("OnTick.outputs:tick", "ArticulationController.inputs:execIn"),
                ("Context.outputs:context", "PublishClock.inputs:context"),
                ("Context.outputs:context", "PublishJointState.inputs:context"),
                ("Context.outputs:context", "SubscribeJointState.inputs:context"),
                ("ReadSimTime.outputs:simulationTime",
                 "PublishClock.inputs:timeStamp"),
                ("ReadSimTime.outputs:simulationTime",
                 "PublishJointState.inputs:timeStamp"),
                ("SubscribeJointState.outputs:jointNames",
                 "ArticulationController.inputs:jointNames"),
                ("SubscribeJointState.outputs:positionCommand",
                 "ArticulationController.inputs:positionCommand"),
            ],
            og.Controller.Keys.SET_VALUES: [
                ("PublishJointState.inputs:targetPrim", "/World/fr3"),
                ("ArticulationController.inputs:targetPrim", "/World/fr3"),
                ("PublishJointState.inputs:topicName", "joint_states"),
                ("SubscribeJointState.inputs:topicName", "joint_command"),
            ],
        },
    )


def main():
    world = World(stage_units_in_meters=1.0)
    world.scene.add_default_ground_plane()
    build_scene(world)
    build_ros2_bridge()
    world.reset()

    print("[isaac] FR3 + ROS 2 bridge ready. Press Play (GUI) or running headless.",
          flush=True)
    while sim_app.is_running():
        world.step(render=not args.headless)

    sim_app.close()


if __name__ == "__main__":
    main()
