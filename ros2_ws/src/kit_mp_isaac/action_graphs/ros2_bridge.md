# Isaac Sim ↔ ROS 2 bridge (OmniGraph)

`run_isaac_fr3.py` builds this graph programmatically. If you prefer the GUI
(Window → Visual Scripting → Action Graph), wire the same nodes:

| Node | Extension type | Purpose |
|---|---|---|
| On Playback Tick | `omni.graph.action.OnPlaybackTick` | drives the graph each sim step |
| ROS2 Context | `isaacsim.ros2.bridge.ROS2Context` | shared DDS context (set `domain_id` to match `ROS_DOMAIN_ID`) |
| Isaac Read Sim Time | `isaacsim.core.nodes.IsaacReadSimulationTime` | timestamps |
| Publish Clock | `isaacsim.ros2.bridge.ROS2PublishClock` | `/clock` |
| Publish Joint State | `isaacsim.ros2.bridge.ROS2PublishJointState` | `/joint_states` (targetPrim `/World/fr3`) |
| Subscribe Joint State | `isaacsim.ros2.bridge.ROS2SubscribeJointState` | receive `/joint_command` |
| Articulation Controller | `isaacsim.core.nodes.IsaacArticulationController` | apply commands to the FR3 |

## Connecting MoveIt

MoveIt executes trajectories through a `FollowJointTrajectory` action. Two options:

1. **Position streaming (simplest):** run `isaac_ros_cumotion_controllers` or a small
   bridge that turns MoveIt's `fr3_arm_controller/follow_joint_trajectory` goals into
   `/joint_command` position streams. Then launch MoveIt with
   `isaac_execution.launch.py` (simple controller manager).
2. **Native FollowJointTrajectory:** add the
   `isaacsim.ros2.bridge.ROS2SubscribeJointState`-based controller graph provided by
   the Isaac Sim MoveIt tutorial and expose the action directly.

Keep `ROS_DOMAIN_ID` identical across the `isaac`, `core`, and `curobo` containers
so DDS discovery works. Verify with `ros2 topic echo /joint_states` from the core
container while Isaac is playing.
