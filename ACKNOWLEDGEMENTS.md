# Acknowledgements

This exercise stands on excellent open-source robotics software. We thank the maintainers and
communities of:

- **MoveIt 2** — robotic manipulation platform for ROS 2. https://moveit.ai — BSD-3-Clause.
- **OMPL** (Open Motion Planning Library) — the sampling-based planners you experiment with.
  https://ompl.kavrakilab.org — BSD-3-Clause.
- **franka_ros2 / franka_description** (Franka Robotics) — FR3 model, MoveIt config, hardware
  interface. https://github.com/frankarobotics/franka_ros2 — Apache-2.0.
- **NVIDIA Isaac Sim** — high-fidelity simulation used on the advanced track.
  https://developer.nvidia.com/isaac-sim — NVIDIA license / EULA (requires accepting terms).
- **cuRobo** and **isaac_ros_cumotion** (NVIDIA) — CUDA-accelerated motion generation and the
  MoveIt planning-pipeline plugin. https://curobo.org ·
  https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_cumotion — NVIDIA / Apache-2.0 (per package).

Pinned versions used by this exercise (July 2026):

| Component | Version / tag |
|---|---|
| ROS 2 | Jazzy Jalisco (Ubuntu 24.04) |
| MoveIt 2 | `moveit/moveit2:jazzy-release` |
| franka_ros2 | v3.4.1 |
| Isaac Sim | 4.5.0 (`nvcr.io/nvidia/isaac-sim:4.5.0`) |
| isaac_ros_cumotion | 4.5 |

Exercise design and this repository: Jakob Thumm, Karlsruhe Institute of Technology (KIT).
