# Day 22 — The cushion that stayed in the costmap

> **Engineering Question**
>
> **Why was my robot avoiding obstacles that didn't exist?**

---

## The story

The simulator room is empty. Walls, floor, a robot, a goal. Nothing else.

The planner does not read that room. It reads a costmap. This day builds the same empty room three ways.

- **Live.** The obstacle layer is only the scan from where the robot stands now. The old cell is free.
- **Stale.** An earlier scan marked one cell, while a cushion was still there. The robot has since backed up. The clearing ray no longer reaches that cell, so it stays lethal. Inflation is off.
- **Inflated.** The same leftover cell, plus the inflation layer from the Humble Nav2 defaults.

The local costmap is a 3 m window around the robot. The leftover cell sits outside that window the whole time. The path is planned on the global costmap.

The production plugins are `nav2_costmap_2d`'s static layer, obstacle layer, and inflation layer. Here those three jobs are small enough to count. The published messages are the real `nav2_msgs/Costmap` and `nav_msgs/Path`. The radii and ranges are the Humble `nav2_bringup` defaults.

---

## What the runs showed

Start **(0.80, 2.00)**. Goal **(5.20, 2.00)**. Straight line **4.40 m**. The old return is the cell at **(4.025, 2.025)**.

It was marked from **(1.70, 2.00)**, **2.325 m** away, inside `obstacle_max_range` **2.5 m**. From the start it is **3.225 m** away, past `raytrace_max_range` **3.0 m**, so the second scan does not clear it.

`S` is the start, `G` is the goal, `C` is that cell, `.` is the path, `#` is lethal, `O` is inscribed (253), `+` is the inflation gradient.

| Case | Global cell | Local cell | Path | Closest the center comes |
|---|---|---|---|---|
| **A** live | cost **0** | outside the window | **4.40 m**, through the cell | **0.000 m** |
| **B** stale, no inflation | cost **254**, 1 lethal cell | outside the window | **4.44 m**, one cell aside | **0.050 m** |
| **C** inflated | cost **254**, **60** inscribed, **316** gradient | outside the window | **4.90 m**, bends **0.57 m** off the line | **0.552 m** |

In A the path is the straight line. In B the center misses a 5 cm cell and would still drive the 0.22 m body through it. In C the inflation layer has grown that cell to the 0.55 m inflation radius, and the path stays just outside it. The floor inside that disk is empty in the simulator.

`/global_costmap/costmap` and `/local_costmap/costmap` are latched `nav2_msgs/Costmap`. `/plan` is a latched `nav_msgs/Path`. The node is `costmap_demo`.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| Domain | `ROS_DOMAIN_ID=220` |

```bash
cd day22-costmaps
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=220
```

---

## Quick start

```bash
cd day22-costmaps
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=220

python3 ros2_nodes/costmaps.py --ros-args -p mode:=inflated
```

`mode` is `live`, `stale`, or `inflated`.

All three:

```bash
./run_smoke.sh
```

---

## Investigations

| ID | What | Headline |
|---|---|---|
| **A** | Live scan | The cell is free. The path is the 4.40 m line |
| **B** | Obstacle layer memory | One lethal cell. The center passes 5 cm away |
| **C** | Obstacle layer plus inflation | 4.90 m path, 0.552 m clear of an empty disk |

Details: `investigations/`.

---

## Key learnings

- The planner reads the global costmap. An empty simulator frame does not clear a cell the current rays never touch.
- `raytrace_max_range` is 3.0 m in the Humble bringup file. A cell marked from 2.325 m away is still lethal from 3.225 m away.
- A lethal cell is cost 254. Without inflation the planner treats the robot as a point, and the center comes within 0.050 m. The configured robot radius is 0.22 m.
- The inflation layer writes 253 out to that radius, then a falling cost out to 0.55 m. This run grew 60 inscribed cells and 316 gradient cells from one phantom, and the path stayed 0.552 m away.
- The local costmap is a rolling 3 m window filled from the current scan. The phantom was outside it, and the path still bent.

Day 21 sent the robot to a pin. Day 22 is the map that pin is planned on.
