# Day 23 — Choosing a path from A to B

> **Engineering Question**
>
> **How does a robot choose a path from A to B?**

---

## The story

The straight line is 7.00 m. Ten samples of it sit on a wall, so that line is not a path.

The planner reads the grid and returns a shortest route that stays on free cells. This day asks the same grid twice.

- **Line.** Draw A to B. Count the wall hits. Publish an empty path.
- **Dijkstra.** Spread by travel cost alone, the way NavFn does when `use_astar` is false.
- **A\*.** Add the straight-line distance still left. Open the cell that looks cheapest once that guess is included.

The guess never exceeds the real distance left, so A\* still owes a shortest path. It just stops wandering.

---

## What the runs showed

A is **(1.0, 1.2)**. B is **(7.0, 4.8)**. The grid is 8 m by 6 m at 0.1 m. **4284** cells are free. Two vertical bars block the diagonal. `A` and `B` are the ends, `#` is a wall, `.` is the path, `+` is a cell the search opened.

| Case | Reached B | Cells opened | Path |
|---|---|---|---|
| **A** line | no | 0 | empty. **10** samples of the 7.00 m line sit on a wall |
| **B** Dijkstra | yes | **3989** of 4284 | **61 poses, 7.49 m** |
| **C** A\* | yes | **832** of 4284 | **61 poses, 7.49 m** |

Both searches return a shortest length. A grid can hold more than one route of that length, so the drawn cells are not the same list. The length is. Dijkstra opened almost the whole room. A\* opened about a fifth of it and followed the corridor toward B.

`/plan` is a latched `nav_msgs/Path`. The node is `global_planner`. In the line run the topic still has a publisher, and the path has 0 poses.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| Domain | `ROS_DOMAIN_ID=230` |

```bash
cd day23-global-planning
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=230
```

---

## Quick start

```bash
cd day23-global-planning
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=230

python3 ros2_nodes/planner.py --ros-args -p mode:=astar
```

`mode` is `line`, `dijkstra`, or `astar`.

All three:

```bash
./run_smoke.sh
```

---

## Investigations

| ID | What | Headline |
|---|---|---|
| **A** | The straight line | 7.00 m, and 10 samples land on a wall |
| **B** | Dijkstra | 3989 cells opened, path 7.49 m |
| **C** | A\* | 832 cells opened, path still 7.49 m |

Details: `investigations/`.

---

## Key learnings

- A global planner chooses a path on the costmap. The straight line is only a candidate, and here it is illegal.
- Dijkstra orders cells by the cost to arrive. It opened 3989 of 4284 free cells before B was the cheapest cell it had finished.
- A\* adds the straight-line distance still left. That guess stays admissible, so the path length stays 7.49 m, and the search opens 832 cells.
- Equal length is the promise. On this grid more than one 7.49 m route exists, so the pose list can differ.
- NavFn's Humble default is `use_astar: false`. Turning that flag on is this same choice: same costmap, a search that looks toward the goal.

Day 22 built the costmap. Day 23 is the search that draws a line on it.
