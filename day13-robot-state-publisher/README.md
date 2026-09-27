# Day 13 — Who Publishes the Robot TF Tree

> **Engineering Question**
>
> **Who actually publishes the robot's transform tree?**

---

## The story

A URDF file does not move a robot. A TF tree does.

`robot_state_publisher` is the node that turns the model plus joint angles into that tree:

| Input | Output |
|---|---|
| `robot_description` (URDF) | `/tf_static` — **fixed** joints, once, `TRANSIENT_LOCAL` |
| `/joint_states` | `/tf` — **moving** joints, `VOLATILE` |

`joint_angles` in this demo plays the role of `joint_state_publisher`: it publishes **angles**, not frames. The apt package `joint_state_publisher` is not installed on this machine, so the stand-in is explicit and does not broadcast TF.

`map` and `odom` are not this node's job. Day 12 owns those edges.

---

## Objective

1. **A** — RSP alone: fixed links exist, the revolute chain does not
2. **B** — Joint angles arrive: the hand frame moves
3. **C** — Name the publisher of `/tf`, `/tf_static`, and `/joint_states`

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| RMW | `rmw_fastrtps_cpp` |
| Domains | A=`130` · B=`131`/`132` · C=`133` |

```bash
cd day13-robot-state-publisher
source ros2_nodes/env.sh
```

---

## Quick start

```bash
# A — description only
ros2 launch launch/tree.launch.py use_joint_angles:=false

# B — angles in, frames out
ros2 launch launch/tree.launch.py use_joint_angles:=true shoulder:=0.80 elbow:=1.20

# Evidence
./run_smoke.sh
```

---

## Layout

```text
day13-robot-state-publisher/
├── urdf/arm.urdf                 # fixed wrist + revolute shoulder/elbow
├── ros2_nodes/joint_angles.py    # /joint_states only
├── launch/tree.launch.py         # robot_state_publisher ± angles
└── assets/                       # A/B/C logs + LinkedIn hero
```

---

## Investigations (real results)

| ID | What | Headline |
|---|---|---|
| **A** | No `/joint_states` | `base_link`→`torso` and `forearm`→`hand` exist; `base_link`→`hand` is **NOT_AVAILABLE** |
| **B** | Angles `0,0` then `0.80,1.20` | hand **(0.60, 0, 0.42)** → **(0.18, 0, 0.00)** |
| **C** | Publisher census | `/tf` and `/tf_static`: **robot_state_publisher**. `/joint_states`: **joint_angles** |

Details: `investigations/`.

---

## Key learnings

- URDF is the model. `robot_state_publisher` is the publisher.
- Fixed joints go to `/tf_static` (`TRANSIENT_LOCAL`). Moving joints go to `/tf`.
- Without joint states, the revolute chain is a hole in the tree.
- The angle source is not the frame source.
- RSP does not invent `map` or `odom`.

---

## Interview one-liner

**`robot_state_publisher` publishes the robot TF tree — fixed joints once on `/tf_static`, moving joints on `/tf` — and it only knows the angles because something else publishes `/joint_states`.**
