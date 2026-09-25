# Day 11 — URDF / Xacro (Robot Description)

> **Engineering Question**
>
> **How does ROS 2 know what a robot physically looks like?**

---

## The story

ROS 2 cannot see aluminum, motors, or a humanoid’s hands.

It loads a **description**: a kinematic tree of **links** and **joints**.

That description is **URDF** (often authored with **Xacro** macros). Launch puts it in `robot_description`. `robot_state_publisher` turns it into TF frames the rest of the stack can share.

Day 11 owns the blueprint. Day 12 deepens TF. Day 13 deepens who publishes the tree.

---

## Objective

1. Validate a fixed humanoid URDF (`check_urdf`) and load it via `robot_description`
2. Show revolute joints + joint states move the hand frame in TF
3. Expand a Xacro macro into left/right arms without copy-paste

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| RMW | `rmw_fastrtps_cpp` |
| Tools | `check_urdf`, `xacro`, `robot_state_publisher` |

```bash
cd day11-urdf-xacro
source ros2_nodes/env.sh
```

Smoke uses isolated `ROS_DOMAIN_ID`s (110–113) so `/tf_static` from one investigation cannot mask another.

---

## Quick start

```bash
cd day11-urdf-xacro
source ros2_nodes/env.sh

# A — fixed humanoid
ros2 launch launch/display.launch.py model:=urdf/humanoid_fixed.urdf

# B — movable arm + joint states
ros2 launch launch/display.launch.py \
  model:=urdf/humanoid_movable.urdf use_joint_demo:=true \
  joint_mode:=pose joints:=r_shoulder,r_elbow positions:=0.80,1.20

# C — Xacro L/R arms
ros2 launch launch/display.launch.py \
  model:=xacro/humanoid.urdf.xacro use_joint_demo:=true \
  joint_mode:=zero \
  joints:=r_shoulder,r_elbow,l_shoulder,l_elbow
```

Evidence:

```bash
./run_smoke.sh
```

Optional RViz: add **RobotModel** + **TF**, fixed frame `base_link`.

---

## Layout

```text
day11-urdf-xacro/
├── urdf/
│   ├── humanoid_fixed.urdf      # Investigation A
│   └── humanoid_movable.urdf    # Investigation B
├── xacro/
│   ├── arm_macro.xacro          # reusable L/R arm
│   └── humanoid.urdf.xacro      # Investigation C
├── launch/display.launch.py
├── ros2_nodes/joint_demo.py     # publishes JointState
└── assets/                      # A/B/C logs + LinkedIn hero
```

---

## Investigations

| ID | What | Evidence |
|---|---|---|
| **A** | Fixed URDF tree → `robot_description` + TF | `assets/A.log` |
| **B** | Revolute shoulder/elbow → hand pose changes | `assets/B.log` |
| **C** | Xacro expands to mirrored L/R arms | `assets/C.log` |

Details: `investigations/`.

---

## Key learnings

- URDF is a **file/string**, not a ROS node.
- **Links** are rigid bodies; **joints** + **origins** place them in a tree.
- Xacro is authoring sugar; runtime is still URDF.
- Movable joints need **joint states** before the full TF chain animates.
- `robot_description` is how the graph carries the blueprint (Day 09/10 plumbing).

---

## Interview one-liner

**ROS 2 doesn’t see the metal — it loads a URDF link/joint tree into `robot_description`, then publishes frames so every tool shares one idea of the robot.**
