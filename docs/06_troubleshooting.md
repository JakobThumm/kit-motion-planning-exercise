# Troubleshooting

## RViz shows no window / "cannot connect to display"
```bash
xhost +local:docker
echo $DISPLAY          # should be set (e.g. :0); pass it into the container via .env
```
On Wayland, ensure XWayland is running. On a remote machine, use X forwarding or a
VNC/NoMachine session.

## `franka_fr3_moveit_config` not found during build
The FR3 sources are vendored by `vcs import` from `docker/franka.repos`. Rebuild:
```bash
cd docker && docker compose build --no-cache core
```
Or on a native install run `scripts/setup_workspace.sh`.

## `MoveItPy` import error / no motion plan
`ros-jazzy-moveit-py` must be installed (it is in `Dockerfile.core`). The scorer and
sweep must be launched via their launch files (`competition.launch.py`,
`benchmark.launch.py`) so MoveItPy receives the MoveIt parameters — running the
python entry points bare will fail to find the robot description.

## Planning always fails / trajectory invalid
- Increase `allowed_planning_time` in `student_solution.py`.
- Lower `goal_bias` in `narrow_passage`-type scenes.
- If "collision" but it looks fine, lower `longest_valid_segment_fraction`.
- Check the goal is reachable and in the joint limits (see the run log in
  `results/results.json` → `runs`).

## Scene doesn't appear
The `scene_loader` calls `/apply_planning_scene`, which needs `move_group` running
first. It waits up to 15 s. If it times out, confirm `move_group` started (look for
it in the launch log).

## GPU / advanced track
- `./scripts/verify_gpu.sh` diagnoses driver, toolkit, and passthrough.
- Driver < 580 → use the Humble + cuMotion 3.2 fallback (see
  [02_install_gpu.md](02_install_gpu.md)).
- Isaac Sim can't reach ROS 2: confirm the `isaac`, `core`, `curobo` services share
  the same `ROS_DOMAIN_ID`; test with `ros2 topic echo /joint_states` from the core
  container while Isaac plays.
- `nvcr.io` pull denied: `docker login nvcr.io` with `$oauthtoken` + your NGC key.

## DDS discovery issues across containers
All services use `network_mode: host` and a shared `ROS_DOMAIN_ID`. If discovery is
flaky on your host, set a fixed `RMW_IMPLEMENTATION=rmw_fastrtps_cpp` (already in the
compose env) and check no firewall blocks multicast on `lo`.
