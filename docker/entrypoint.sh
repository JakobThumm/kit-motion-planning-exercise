#!/usr/bin/env bash
# Sources ROS 2 + the exercise workspace, then runs whatever command was passed.
set -e

source /opt/ros/${ROS_DISTRO:-jazzy}/setup.bash
if [ -f "${WS:-/root/ros2_ws}/install/setup.bash" ]; then
    source "${WS:-/root/ros2_ws}/install/setup.bash"
fi

# If the host mounted an editable copy of the sources, prefer it for config files.
if [ -d "/root/ros2_ws/src_mounted" ]; then
    export KIT_MP_SRC=/root/ros2_ws/src_mounted
else
    export KIT_MP_SRC=/root/ros2_ws/src
fi

exec "$@"
