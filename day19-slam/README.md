# Day 19 — Building a map

> **Engineering Question**
>
> **What actually happens when a robot "builds a map"?**

---

## The story

A LiDAR does not hand over a floor plan. It hands over a fan of distances. The map is what you get after those distances are lined up and painted into a grid.

This day drives a robot through a 4 m square room and paints the same 16 scans three ways.

- **Truth.** Each scan is painted at the real pose.
- **Drift.** Each scan is painted where the wheels think the robot is. The wheels add 3 cm of extra forward motion every step.
- **Match.** The wheels still drift, but each new scan is slid until its hits sit on the walls already drawn. Then it is painted.

---

## What the runs showed

The room walls are at 0 m and 4 m. The robot drives from x = 1.00 m to x = 1.90 m along y = 1.50 m. Sixteen scans. Cell size 5 cm.

| Case | Pose used to paint | Final pose error | Hits vs real walls | East-wall spread | Occupied cells |
|---|---|---|---|---|---|
| **A** | Real pose | **0.000 m** | **0.000 m** | 0.017 m | 322 |
| **B** | Wheel pose | **0.450 m** | 0.111 m | **0.131 m** | **553** |
| **C** | Scan matched to the grid | **0.036 m** | 0.024 m | 0.017 m | 317 |

`/map` is a latched `nav_msgs/OccupancyGrid`. One publisher: `map_builder`.

A correct pose draws one clean square. Drift draws the same walls again in the wrong place, so the square grows a second edge. Matching pulls the pose back before the paint goes down, and the square stays single.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| Domain | `ROS_DOMAIN_ID=190` |

```bash
cd day19-slam
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=190
```

---

## Quick start

```bash
cd day19-slam
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=190

python3 ros2_nodes/build_map.py --ros-args -p mode:=truth
```

`mode` is `truth`, `drift`, or `match`. The node prints a `SUMMARY` line and an ASCII map, and keeps publishing `/map`.

All three cases:

```bash
./run_smoke.sh
```

---

## Investigations

| ID | What | Headline |
|---|---|---|
| **A** | Paint at the real pose | The walls land on the walls |
| **B** | Paint at the wheel pose | 45 cm of drift, and the wall is drawn twice |
| **C** | Slide the scan onto the grid first | Pose error stays near one cell |

Details: `investigations/`.

---

## Key learnings

- Building a map is two steps. Line the new scan up. Then mark open floor along each beam and a surface where the beam stops.
- Wheel odometry is only the first guess. Paint with that guess alone and the same wall is stored in more than one place.
- Scan matching here searches a few centimeters in x and y until the new hits sit on cells that are already occupied.
- The leftover 3.6 cm is about one grid cell. It does not grow the way the wheel error does.
- This is the same loop `slam_toolbox` runs on a real scan. This day uses a scripted square room and a small search, so the numbers stay easy to read.

Day 15 carried a laser scan out of the simulator. Day 19 turns a sequence of those scans into a grid.
