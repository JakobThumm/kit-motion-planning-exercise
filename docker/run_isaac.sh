#!/usr/bin/env bash
# Launches Isaac Sim with the FR3 exercise scene and the ROS 2 bridge action graph.
# Runs inside the isaac container (Dockerfile.isaac). Talks to move_group over DDS.
set -e

# Headless by default; set ISAAC_GUI=1 for the GUI (needs X11).
SCRIPT=/root/kit_mp_isaac/scripts/run_isaac_fr3.py

if [ "${ISAAC_GUI:-0}" = "1" ]; then
    /isaac-sim/python.sh "${SCRIPT}"
else
    /isaac-sim/python.sh "${SCRIPT}" --headless
fi
