# Install — ADVANCED (GPU) track

Adds Isaac Sim (high-fidelity execution) and cuRobo / cuMotion (GPU planning).
Everything on the CORE track still works without any of this.

## Prerequisites

- NVIDIA GPU, **driver 580+**, CUDA 13 capable (Ubuntu 24.04 host recommended).
- `nvidia-container-toolkit` configured for Docker.
- An NGC account to pull the Isaac Sim image.

Check readiness:

```bash
./scripts/verify_gpu.sh
```

## nvidia-container-toolkit

```bash
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```

## Pull Isaac Sim (NGC)

```bash
docker login nvcr.io      # username: $oauthtoken ; password: your NGC API key
```

## Build & run

```bash
cd docker
docker compose build curobo          # cuMotion planner (FROM the core image)
docker compose build isaac           # Isaac Sim (large, ~20-30 GB)

# Terminal 1: Isaac Sim + ROS 2 bridge
ISAAC_GUI=1 docker compose run --rm isaac

# Terminal 2: MoveIt with OMPL + cuMotion pipelines
./run_gpu.sh ros2 launch kit_mp_curobo cumotion_planner.launch.py
```

Now you can plan with cuMotion by setting `pipeline_id="isaac_ros_cumotion"` in
`student_solution.py`, and execute in Isaac Sim.

## Older GPUs — Humble + cuMotion 3.2 fallback

If `verify_gpu.sh` reports a driver **< 580**, use the frozen-but-compatible line
(Turing / RTX 2080+):

1. `docker/Dockerfile.core`: base image → `moveit/moveit2:humble-release`.
2. `docker/isaac_ros.repos`: versions → `release-3.2`.
3. `docker/Dockerfile.gpu`: apt prefix `ros-humble-*`; Isaac Sim tag per the 3.2
   compatibility matrix.
4. In `ompl_planning.yaml`, use the Humble singular keys (`planning_plugin` /
   `response_adapters`) — a Humble variant is documented inline.

The CORE track is unaffected by this switch.

## Known integration notes

- Isaac Sim 4.5's in-container ROS bridge is unreliable when co-located with a
  separate ROS 2, so Isaac runs in its **own** container and talks over DDS. Keep
  `ROS_DOMAIN_ID` identical across services.
- The shipped cuMotion XRDF is for Panda; we provide an FR3 XRDF
  ([`kit_mp_curobo/config/fr3.xrdf`](../ros2_ws/src/kit_mp_curobo/config/fr3.xrdf)) —
  verify its collision spheres before trusting cuMotion collision avoidance.
