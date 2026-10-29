# Day 24 — A box on the path

> **Engineering Question**
>
> **What happens when an obstacle suddenly appears on the planned path?**

---

## The story

The global plan is drawn first, on an empty floor. Start **(3.0, 1.0)**. Goal **(3.0, 7.0)**. The line is **6.00 m** and it runs through the middle of the room.

Then a box appears, once the robot has passed y = 2.20 m. The old line still goes through the box. Three controllers meet that fact.

- **Blind.** Follow the old line. Stop when the next step would enter the box.
- **Local.** Keep publishing the old line. A short-range steer may step up to 1.05 m off the line. The small box leaves a bypass inside that reach, so the body goes around and the plan does not change.
- **Replan.** The box is 4.00 m wide. No bypass fits inside 1.05 m. The steer reports no passage. One global search draws a new line around the box, and the controller follows that line.

The body radius is 0.22 m, the Humble `nav2_bringup` robot radius. This is the controller-then-replan order from Nav2's `navigate_to_pose_w_replanning_and_recovery.xml`, small enough to count. It is not the DWB critic stack.

---

## What the runs showed

`S` is the start, `G` is the goal, `#` is the box, `.` is the global path, `r` is where the body drove.

| Case | Plan after the box | Body | Goal |
|---|---|---|---|
| **A** blind | still the **6.00 m** line, through the box | stops on the line, **3.680 m** short | not reached, 117 commands |
| **B** local | still the **6.00 m** line, through the box | drives **1.05 m** off the line, stays **0.315 m** clear | reached, error **0.181 m**, 369 commands, **0** replans |
| **C** replan | a new **6.70 m** line, **1.75 m** off center, not through the box | follows it, **1.77 m** off the old line | reached, error **0.195 m**, 371 commands, **1** replan |

In B the published path is still illegal. The wheels are not. In C the local reach cannot see a way past, so the global planner runs again.

`/plan` is a latched `nav_msgs/Path`. `/cmd_vel` is a `geometry_msgs/Twist`. The node is `avoidance`.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| Domain | `ROS_DOMAIN_ID=231` |

```bash
cd day24-dynamic-obstacles
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=231
```

---

## Quick start

```bash
cd day24-dynamic-obstacles
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=231

python3 ros2_nodes/drive.py --ros-args -p mode:=replan
```

`mode` is `blind`, `local`, or `replan`.

All three:

```bash
./run_smoke.sh
```

---

## Investigations

| ID | What | Headline |
|---|---|---|
| **A** | Follow the old line | Stopped 3.680 m short of the goal |
| **B** | Local steer, same plan | 1.05 m off the line, plan still 6.00 m |
| **C** | One replan | New path 6.70 m, goal reached |

Details: `investigations/`.

---

## Key learnings

- A new obstacle does not delete the global path. In A and B, `/plan` is still the 6.00 m line through the box.
- The local controller is the stage that can bend the body around a box the plan still contains. Here the body went 1.05 m off the line and stayed 0.315 m clear, with zero replans.
- That steer has a reach. The wide box has no bypass inside 1.05 m, so the local policy stops and asks for a new line.
- The new line is 6.70 m, 0.70 m longer than the straight plan, and it does not enter the box. The body then follows it to within 0.195 m of the goal.
- In Nav2 this split is `FollowPath` against the local costmap, then `ComputePathToPose` again when that action fails. This day runs that handoff once.

Day 23 drew the line. Day 24 is what happens when the floor changes after the line exists.
