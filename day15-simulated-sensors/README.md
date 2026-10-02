# Day 15 — Simulated sensors

> **Engineering Question**
>
> **My simulated LiDAR was perfect. Why is that a problem?**

---

## The story

A LiDAR shoots beams and reports how far each one traveled before it hit something.

With no noise, Gazebo is a tape measure. The robot is still, the wall is still, and the next scan is the same number again. A real beam wobbles. Code that only passed on the exact number can chatter on a real robot.

This day puts one stationary sensor in front of one wall and changes a single setting at a time.

---

## What the runs showed

The wall face is **1.90 m** from the sensor. The center beam read **1.9006 m** in every case.

| Case | Setting | What happened |
|---|---|---|
| **A** | No noise, 5 Hz | 15 scans. Largest change between scans: **0.000 m** |
| **B** | Gaussian noise, stddev 0.05 m, still 5 Hz | Same wall. Largest beam change: **0.223 m**. Center stayed near 1.90 m |
| **C** | No noise, 1 Hz | Ranges still identical. Rate fell to **0.99 Hz** |

Before the bridge, Gazebo already had `/lidar`. ROS did not.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| Simulator | Gazebo Harmonic (`gz sim` 8.14.0) |
| Bridge | `ros_gzharmonic_bridge` |
| Domain | `ROS_DOMAIN_ID=150` |

```bash
cd day15-simulated-sensors
source ros2_nodes/env.sh
```

---

## Quick start

```bash
cd day15-simulated-sensors
source ros2_nodes/env.sh

# Terminal 1 — perfect sensor, no window
gz sim -s -r --headless-rendering worlds/wall_perfect.sdf

# Terminal 2 — Gazebo has the scan. ROS does not, until this runs.
ros2 run ros_gz_bridge parameter_bridge \
  /lidar@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan

# Terminal 3
python3 ros2_nodes/measure_scan.py --ros-args -p listen_sec:=3.0
```

Repeat with `worlds/wall_noisy.sdf` and `worlds/wall_slow.sdf`.

All three cases:

```bash
./run_smoke.sh
```

---

## Investigations

| ID | What | Headline |
|---|---|---|
| **A** | No noise | Same scan twice. Bridge is required before ROS sees it |
| **B** | Noise on | The wall does not move. The numbers do |
| **C** | Update rate | 5 Hz → 1 Hz changes how often a scan arrives, not the distance |

Details: `investigations/`.

---

## Key learnings

- A plugin turns the sensor on. It does not make the sensor honest. No `<noise>` block means a repeated scan.
- Noise, update rate, and beam count are different knobs. This day moves the first two. Beam count is fixed at 32 so the comparison stays fair.
- Gaussian noise is a small wobble on each beam. It is not rain, glass, or a missed return.
- The scan lives on Gazebo Transport until `ros_gz_bridge` copies it to `/lidar`.

Day 14 carried a drive command into the simulator. Day 15 carries a measurement out.
