# Day 21 — After the Nav2 goal

> **Engineering Question**
>
> **What actually happens after I send a Nav2 goal?**

---

## The story

The pin on the map is a pose. It is not a wheel speed.

This day sends one real `NavigateToPose` goal three times. A wall stands between the start and the pin, so a straight command would hit it. Each run turns on one more stage.

- **Goal only.** The action arrives. Nothing plans. Nothing drives.
- **Planner only.** A path is drawn around the wall. The robot stays put.
- **Full.** The controller turns that path into `Twist`. The pose arrives.

The production stack is `bt_navigator`, `planner_server`, and `controller_server`. Here those three jobs are small enough to count, and the goal message is the real Nav2 action.

---

## What the runs showed

Start **(0.6, 0.6)**. Goal **(5.2, 0.6)**. Straight-line distance **4.60 m**. The wall occupies x = 2.3 to 3.5 m and y = 0 to 2.35 m. `S` is the start, `G` is the pin, `R` is where the robot finished, `.` is the path.

| Case | Order of events | Action result | Path | Final error | Wheel commands |
|---|---|---|---|---|---|
| **A** | `goal` | ABORTED | 0 poses | **4.600 m** | 0 |
| **B** | `goal > path` | ABORTED | **27 poses, 6.69 m**, crest y = **2.50 m** | **4.600 m** | 0 |
| **C** | `goal > path > cmd_vel` | **SUCCEEDED** | same 6.69 m path | **0.130 m** | **279**, peak 0.45 m/s |

The path is longer than the straight line because it climbs over the wall. In B that line exists and the robot has not moved. In C the same line becomes speed, and the robot does not enter the wall.

`ros2 action send_goal /navigate_to_pose` is the client. The server node is `navigator`. `/plan` is a latched `nav_msgs/Path`.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| Domain | `ROS_DOMAIN_ID=210` |

```bash
cd day21-nav2-architecture
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=210
```

---

## Quick start

```bash
cd day21-nav2-architecture
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=210

# Terminal 1
python3 ros2_nodes/navigate.py --ros-args -p mode:=full

# Terminal 2
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 5.2, y: 0.6, z: 0.0}, orientation: {w: 1.0}}}}"
```

`mode` is `goal_only`, `planner_only`, or `full`.

All three:

```bash
./run_smoke.sh
```

---

## Investigations

| ID | What | Headline |
|---|---|---|
| **A** | Goal only | The pin arrives. The robot stays 4.60 m away |
| **B** | Planner only | A 6.69 m path goes over the wall. The pose does not |
| **C** | Planner and controller | 279 speed commands. The action succeeds |

Details: `investigations/`.

---

## Key learnings

- `NavigateToPose` carries a pose. It does not carry `linear.x`.
- The planner's output is `nav_msgs/Path`. Around this wall the path is 6.69 m, not the 4.60 m straight line.
- The controller's output is `geometry_msgs/Twist` on `/cmd_vel`. Without that publisher the path is a drawing.
- The action succeeds only after the pose is within 0.15 m of the pin. A goal with no driver is aborted, on purpose.
- Nav2's behavior tree is the checklist that calls the planner, then the controller, then checks again. This day runs that order once, with no recovery branch.

Day 20 found the robot on the map. Day 21 sends it to a pin on that map.
