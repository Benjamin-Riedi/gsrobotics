# ROS1 Noetic RGB Integration (Standalone, catkin kept separate)

This file adds a **new-file-only** path for RGB publishing from GelSight Mini on Ubuntu 20.04.
No existing files are modified.

## What was added

- `/home/runner/work/gsrobotics/gsrobotics/rgb_compat/gelsight_rgb_compat.py`
- `/home/runner/work/gsrobotics/gsrobotics/ros1_rgb_publisher.py`
- `/home/runner/work/gsrobotics/gsrobotics/requirements-rgb-noetic.txt`
- `/home/runner/work/gsrobotics/gsrobotics/examples/rgb_ros1_noetic_config.json`
- `/home/runner/work/gsrobotics/gsrobotics/examples/run_ros1_rgb_publisher.sh`

## Option A (recommended): Python 3.8/3.9 compatible RGB path

1. Create and activate a Python env (3.8/3.9 on Ubuntu 20.04).
2. Install RGB-only deps:
   ```bash
   pip install -r /home/runner/work/gsrobotics/gsrobotics/requirements-rgb-noetic.txt
   ```
3. Install ROS Noetic Python dependencies (system packages):
   ```bash
   sudo apt update
   sudo apt install -y ros-noetic-rospy ros-noetic-sensor-msgs ros-noetic-cv-bridge
   ```
4. Run publisher:
   ```bash
   /home/runner/work/gsrobotics/gsrobotics/examples/run_ros1_rgb_publisher.sh
   ```

## Option B: Keep capture in Python 3.12, bridge to ROS1 3.8

- Keep capture process separate in a Python 3.12 env.
- Send frames via local IPC/TCP/UDP/JPEG stream to a ROS1 Python 3.8 publisher process.
- Use this if you need to preserve upstream runtime assumptions without backporting.

## Option C: Ways to access Python 3.12 on Ubuntu 20.04

- `pyenv`
- `deadsnakes`
- `micromamba` / `conda`
- containerized runtime with USB passthrough

## Catkin note

Catkin integration is intentionally not implemented here. Use the standalone publisher first,
then reference or mirror it in your existing catkin workspace later.
