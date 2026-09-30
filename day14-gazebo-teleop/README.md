# Day 14 — Gazebo Teleop (`/cmd_vel`)

> **Engineering Question**
>
> **I pressed one keyboard key. How did that make a simulated robot move?**

---

## The story

The key does not move the robot.

`i` becomes a `geometry_msgs/Twist` on `/cmd_vel`. A bridge carries that message from ROS 2 into Gazebo Transport. A differential-drive system turns `linear.x` and `angular.z` into left and right wheel speeds. The simulator integrates those speeds into motion.

---

## Objective

1. Show the Twist for forward (`i`), turn (`j`), and stop (`k`)
2. Show Gazebo does not see that ROS publisher until `ros_gz_bridge` is running
3. Show a forward Twist moves the Harmonic diff-drive model, and `linear.y` does not

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| Simulator | **Gazebo Harmonic** (`gz sim` 8.14.0) |
| Bridge | `ros_gzharmonic_bridge` |
| Teleop bindings | `teleop_twist_keyboard` 2.4.1, speed `0.5`, turn `1.0` |

The Humble Gazebo tutorial targets **Fortress** and `ignition.msgs.Twist`. This machine is Harmonic, so the bridge uses `gz.msgs.Twist`. Same idea, different Gazebo generation.

```bash
cd day14-gazebo-teleop
source ros2_nodes/env.sh
```

---

## Quick start

```bash
cd day14-gazebo-teleop
source ros2_nodes/env.sh

# What the forward key publishes
python3 ros2_nodes/key_twist.py --ros-args -p key:=i -p run_sec:=2.0

# Server-only sim (official Harmonic diff-drive world)
gz sim -s -r /usr/share/gz/gz-sim8/worlds/diff_drive.sdf

# ROS → Gazebo
ros2 run ros_gz_bridge parameter_bridge \
  /model/vehicle_blue/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist
```

Interactive keyboard, once the bridge is up:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args \
  -r /cmd_vel:=/model/vehicle_blue/cmd_vel
```

Evidence:

```bash
./run_smoke.sh
```

`key_twist.py` does not read the keyboard. It publishes the same `moveBindings` the installed teleop node uses, so the smoke does not need a TTY.

---

## Investigations

| ID | What | Headline |
|---|---|---|
| **A** | Key binding → Twist | `i` → `linear.x=0.5` · `j` → `angular.z=1.0` · `k` → zeros |
| **B** | No bridge | ROS publisher exists. Gazebo topic has **no publishers** |
| **C** | Bridge + diff-drive | `x` goes **0 → 1.71 m**. After a stop, `linear.y` leaves `x` and `y` unchanged |

Details: `investigations/`.

---

## Key learnings

- Teleop publishes a **velocity**, not a position and not a joint command.
- Diff-drive uses `linear.x` and `angular.z`. `linear.y` is a strafe the plugin cannot do.
- On Gazebo Sim, ROS and Gazebo Transport are different networks. The bridge is the crossing.
- This repo's sim is Harmonic. Do not paste the Fortress `ignition.msgs` command onto it.

---

## Interview one-liner

**One key becomes a Twist on `/cmd_vel`. The bridge carries it into Gazebo. Diff-drive spends `linear.x` and `angular.z` on the two wheels.**
