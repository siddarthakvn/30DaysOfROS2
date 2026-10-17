# Day 20 — Where am I on the map?

> **Engineering Question**
>
> **A robot has a map — but how does it know where it is on that map?**

---

## The story

The floor plan is already drawn. The robot wakes up in the kitchen and is not told that.

Guesses are poses dropped on the open floor. The wheels move every guess by the step the robot just took. The laser scores each guess by how well that place would have seen the same walls. The guesses that fit are copied. The others are dropped.

The house is a kitchen on the left, a hall in the middle, and a bedroom at the top right. A plain square looks the same from four directions, so this house does not.

---

## What the runs showed

The robot walks inside the kitchen and finishes at **(1.9 m, 3.0 m)**. `T` on the ASCII map is the truth. `E` is the pose the mode reports. `.` is a guess.

| Case | How the guesses are handled | Final error | Cloud width | Guesses still in the kitchen |
|---|---|---|---|---|
| **A** | One guess, dropped in the bedroom | **5.316 m** | 0.000 m | 0.000 |
| **B** | 400 guesses, wheels only | **2.201 m** | **3.304 m** | 0.345 |
| **C** | 400 guesses, laser scores them | **0.030 m** | 0.221 m | **1.000** |

The first laser scan in case C does not finish the job. After that scan, **98.8%** of the guesses are already in the kitchen, and the reported place is still **2.605 m** off. A long kitchen wall looks alike from both ends. The later steps break that tie. Four scans while the robot stands still pull the cluster onto the body. The leftover cloud is **22 cm** wide because each copy is nudged a little, so a later scan can still move it.

`/map` is a latched `nav_msgs/OccupancyGrid`. `/particle_cloud` is a `geometry_msgs/PoseArray`. One publisher: `localizer`.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| Domain | `ROS_DOMAIN_ID=200` |

```bash
cd day20-amcl
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=200
```

---

## Quick start

```bash
cd day20-amcl
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=200

python3 ros2_nodes/localize.py --ros-args -p mode:=laser_vote
```

`mode` is `one_guess`, `wheels_only`, or `laser_vote`. The node prints a `SUMMARY` line and an ASCII house, and keeps publishing `/map` and `/particle_cloud`.

All three cases:

```bash
./run_smoke.sh
```

---

## Investigations

| ID | What | Headline |
|---|---|---|
| **A** | One bedroom guess | It copies the steps and stays 5.3 m away |
| **B** | Wheels only | The cloud covers the house |
| **C** | Laser vote | The cloud collapses onto the kitchen pose |

Details: `investigations/`.

---

## Key learnings

- The first cloud is an input. With no hint, the dots are scattered on the free cells of the map. With one hint, you only get the guesses you placed.
- Wheels move the guesses. They do not choose among them. After the walk, 34.5% of the wheel-only guesses are still in the kitchen, which is about where a random scatter starts.
- The laser is a test against the frozen map. A guess survives when the walls it expects are the walls the robot measured.
- The first test picked the room. It took the rest of the walk to pick the spot inside the room.
- This is the loop `nav2_amcl` runs. Here the house, the 400 guesses, and the steps are small enough to count.

Day 19 drew the map. Day 20 holds that drawing still and asks which guess belongs on it.
