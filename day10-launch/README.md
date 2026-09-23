# Day 10 — Launch (Robot Bringup)

> **Engineering Question**
>
> **How do you bring up an entire robot with one command?**

---

## The story

A robot is not one node. It is a system: camera, LiDAR, IMU, control, …

Day 10 shows how **`ros2 launch`** starts and configures that system from one description — with namespaces, parameters, modular includes, and optional components.

---

## Objective

1. One launch starts multiple stubs (multi-process bringup)
2. Launch args change namespace (`robot1` vs `robot2`)
3. Conditional `use_camera:=false` skips the camera node
4. YAML/params apply without rebuilding nodes

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| RMW | `rmw_fastrtps_cpp` |
| Domain | `ROS_DOMAIN_ID=100` |

```bash
cd day10-launch/ros2_nodes
source ./env.sh
```

---

## Quick start

```bash
cd day10-launch
source ros2_nodes/env.sh

# Default: namespace=robot1, camera on
ros2 launch launch/bringup.launch.py

# Other robot namespace
ros2 launch launch/bringup.launch.py namespace:=robot2

# Skip camera
ros2 launch launch/bringup.launch.py use_camera:=false
```

Smoke + evidence:

```bash
./run_smoke.sh
```

---

## Layout

```text
day10-launch/
├── launch/
│   ├── bringup.launch.py    # top-level include + control
│   └── sensors.launch.py    # camera / lidar / imu (conditional camera)
├── ros2_nodes/
│   ├── sensor_stub.py
│   └── control_stub.py
├── config/robot_params.yaml
└── assets/                  # A/B/C logs + LinkedIn hero
```

---

## Investigations

| ID | What | Evidence |
|---|---|---|
| **A** | Default bringup (`robot1` + camera) | `assets/A.log` |
| **B** | `namespace:=robot2` isolation | `assets/B.log` |
| **C** | `use_camera:=false` | `assets/C.log` |

Details: `investigations/`.

---

## Key learnings

- Launch orchestrates processes; it is not a graph “super-node.”
- Namespaces isolate the same stubs for different robots.
- Includes keep bringup modular.
- Conditions toggle optional hardware/software.
- Process start order ≠ application readiness.

---

## Interview one-liner

**`ros2 launch` brings the robot up with one command — namespaces, params, remaps, and optional pieces all declared in the launch description.**
