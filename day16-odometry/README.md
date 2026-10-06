# Day 16 — Wheel rotation to position

> **Engineering Question**
>
> **How does wheel rotation become robot position?**

---

## The story

The wheels do not report where the robot is. They report how fast each wheel is turning.

A differential-drive robot can roll forward and it can spin. It cannot slide sideways. Two wheel speeds become one forward speed and one yaw rate. Adding that motion up, a small step at a time, becomes `x`, `y`, and yaw. That running total is odometry.

---

## What the runs showed

Wheel radius 0.10 m. Track width 0.40 m. Pose is published on `/odom` in frame `odom`, with the body speed in `base_link`.

| Case | Wheels | Result |
|---|---|---|
| **A** | Both spin at 5 rad/s for 2 s | `x = 1.000 m`, `y = 0`, yaw `0°`. Body sideways speed `0` |
| **B** | Opposite spins, 2 rad/s, for a quarter turn | Center stays at `0, 0`. Yaw `90.01°` |
| **C** | Same drive as A, but already facing 90° | `x` stays `0`. `y = 1.000 m`. Body still has no sideways speed |
| **D** | Same wheel spin as A, but the radius used in the sum is 0.11 m | Reported `x = 1.100 m` |

The command did not change between A and D. The wheel size in the formula did.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| Domain | `ROS_DOMAIN_ID=160` |
| Message | `nav_msgs/Odometry` |

```bash
cd day16-odometry
source ros2_nodes/env.sh
```

---

## Quick start

```bash
cd day16-odometry
source ros2_nodes/env.sh
./run_smoke.sh
```

One case by hand:

```bash
python3 ros2_nodes/wheel_odom.py --ros-args \
  -p omega_left:=5.0 -p omega_right:=5.0 \
  -p radius:=0.1 -p track_width:=0.4 -p seconds:=2.0
```

---

## Investigations

| ID | What | Headline |
|---|---|---|
| **A** | Both wheels the same way | 2 s at 0.5 m/s becomes 1.000 m straight |
| **B** | Wheels opposite ways | The center does not move. The heading does |
| **C** | Drive after a turn | World `y` changes. Body sideways speed stays 0 |
| **D** | Wrong wheel radius | Same spin, 1.100 m instead of 1.000 m |

Details: `investigations/`.

---

## Key learnings

- Contact speed of a wheel is spin rate times radius.
- Forward speed is the average of the two contact speeds. Yaw rate is their difference divided by the track width.
- The pose is that motion added up. It is a guess from the wheels, not a map.
- A short, perfect run can land on a round number. That does not mean a real wheel will. Slip and a wrong radius accumulate. Day 18 is where another sensor is asked to help.

Day 14 turned a command into wheel motion. Day 12 named the `odom` frame. This day fills that frame with the wheel sum.
