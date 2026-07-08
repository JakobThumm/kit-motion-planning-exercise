#!/usr/bin/env bash
# Reproduce the ROS 2 workspace build (what Dockerfile.core does). Run INSIDE the
# container, or on a native ROS 2 Jazzy install. Idempotent.
set -euo pipefail

ROS_DISTRO="${ROS_DISTRO:-jazzy}"
WS="${WS:-$(cd "$(dirname "$0")/../ros2_ws" && pwd)}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

source "/opt/ros/${ROS_DISTRO}/setup.bash"
cd "${WS}"

# 1. Vendor pinned FR3 sources, then prune franka_ros2 to just the MoveIt config
#    (the rest is real-hardware / Gazebo only; see docker/franka.repos).
mkdir -p src
vcs import src < "${REPO_ROOT}/docker/franka.repos"
find src/franka_ros2 -mindepth 1 -maxdepth 1 -type d \
    ! -name franka_fr3_moveit_config -exec rm -rf {} +

# 2. (advanced) Vendor cuMotion sources if building the GPU track.
if [ "${WITH_GPU:-0}" = "1" ]; then
    vcs import src < "${REPO_ROOT}/docker/isaac_ros.repos"
fi

# 3. Resolve dependencies.
rosdep update
rosdep install --from-paths src --ignore-src -r -y

# 4. Build.
colcon build --symlink-install --mixin release
echo "Done. Source it:  source ${WS}/install/setup.bash"
