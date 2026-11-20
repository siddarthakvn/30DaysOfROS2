# Day 30 — One graph, three bodies

> **Engineering Question**
>
> **What breaks when you scale one ROS 2 robot to three?**

---

## The story

On one robot, `/cmd_vel`, `/odom`, and `base_link` feel like names for the truth. Launch three copies of that stack on the same domain, and DDS connects all of them together.

Scaling from one robot to three requires **two separate boundaries**:

1. **Isolation (private body wires).** Putting a node inside `--ros-args -r __ns:=/r1` only namespaces **relative** names (`cmd_vel` → `/r1/cmd_vel`, `odom` → `/r1/odom`). Any hardcoded leading slash (`"/cmd_vel"`, `"/odom"`) or unprefixed TF frame (`"base_link"`) bypasses the namespace and merges all three robots onto one bus.
2. **Allocation (shared fleet wire).** Even after namespaces isolate `/r1/*`, `/r2/*`, and `/r3/*`, having all three robots listen directly to one mission topic sends three physical bodies into the same doorway. A `fleet_coordinator` sits between the shared `/fleet/target` and the private `/rN/goal` topics so one target dispatches one robot.

Three bays in `map`: `r1` at `(1.00, 3.00)`, `r2` at `(1.00, 1.00)`, `r3` at `(5.00, 1.00)`. One rescue target arrives at `(2.50, 3.00)` (`1.500 m` from `r1`, `2.500 m` from `r2`, `3.202 m` from `r3`).

---

## What the runs showed

Domain `224`. Goal tolerance `0.04 m`. Control window `3.5 s` at `20 Hz`. Launched via `ros2 launch launch/fleet.launch.py mode:=<mode>`.

| Case | Topic & TF wiring | `/cmd_vel` endpoints | Moved | Reached `(2.50, 3.00)` | Fleet travel | Min pair separation |
|---|---|---|---|---|---|---|
| **A** `collision` | Leading slashes `"/cmd_vel"`, `"/odom"`, `"base_link"` | **3 pub / 3 sub** on `/cmd_vel` | **3** | **0** (`err` `3.88–5.97 m`) | **14.840 m** | `4.431 m` |
| **B** `uncoordinated` | Relative `cmd_vel`, `odom`, `rN/base_link`; shared `/fleet/target` | **1 pub / 1 sub** per `/rN/cmd_vel` | **3** | **3** (`err` `0.036–0.037 m`) | **7.091 m** | **0.033 m** (pile-up) |
| **C** `coordinated` | Namespaced robots + `fleet_coordinator` → `/r1/goal` | **1 pub / 1 sub** per `/rN/cmd_vel` | **1** (`r1`) | **1** (`r1`, `err` `0.036 m`) | **1.464 m** | **2.479 m** |

- **In A (`collision`),** `/r1/*`, `/r2/*`, and `/r3/*` were passed as node namespaces, so `ros2 node list` showed `/r1/base`, `/r1/controller`, `/r2/base`, `/r2/controller`, `/r3/base`, `/r3/controller`. Yet `ros2 topic list` had no `/rN/cmd_vel` at all: leading slashes collapsed all three controllers and all three bases onto `/cmd_vel` (`Publisher count: 3`, `Subscription count: 3`) and `/odom` (`Publisher count: 3`, `Subscription count: 3`). Every base received **213** conflicting `Twist` messages, wandered **4.90–4.97 m**, and **0 of 3** robots reached the target.
- **In B (`uncoordinated`),** switching to relative topic names (`cmd_vel`, `odom`) and TF prefixes (`r1/base_link`, `r2/base_link`, `r3/base_link`) gave each robot clean `1 pub / 1 sub` control of its own wheels. Without task allocation, all three chased `/fleet/target` at once, burning **7.091 m** of total travel and converging to **0.033 m** (`3.3 cm`) center-to-center — a three-robot collision at the goal.
- **In C (`coordinated`),** `fleet_coordinator` read `/r1/odom`, `/r2/odom`, and `/r3/odom`, scored distances (`r1: 1.500 m`, `r2: 2.500 m`, `r3: 3.202 m`), published `winner=r1` on `/fleet/assignment`, and routed the goal exclusively to `/r1/goal`. `r1` drove **1.464 m** (`35` commands) to `(2.464, 3.000)` (`tf2_echo map r1/base_link` → `[2.464, 3.000, 0.000]`), while `r2` and `r3` stayed parked at `0.000 m` travel and `0` commands.

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble |
| Domain | `ROS_DOMAIN_ID=224` |
| Launch | `ros2 launch` (`launch/fleet.launch.py`) with `-r __ns:=/r1`, `/r2`, `/r3` |
| Interfaces | `geometry_msgs/Twist`, `geometry_msgs/PoseStamped`, `nav_msgs/Odometry`, `tf2_ros` |

```bash
cd day30-multi-robot
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=224
```

---

## Quick start

Launch one mode directly:

```bash
cd day30-multi-robot
source ros2_nodes/env.sh
export ROS_DOMAIN_ID=224

ros2 launch launch/fleet.launch.py mode:=coordinated
```

`mode` is `collision`, `uncoordinated`, or `coordinated`.

Run all three investigations end-to-end and capture CLI transcripts:

```bash
./run_smoke.sh
```

---

## Investigations

| ID | What | Headline |
|---|---|---|
| **A** | Leading slashes inside `/r1`, `/r2`, `/r3` | 3 pub / 3 sub on `/cmd_vel`, 213 cmds each, 0 robots reach target |
| **B** | Relative topics + TF prefixes, no coordinator | Isolated wheels, but all 3 pile onto `(2.50, 3.00)` (`0.033 m` apart) |
| **C** | Namespaces + `fleet_coordinator` allocator | `r1` wins (`1.500 m`), drives `1.464 m`; `r2` and `r3` hold (`0` cmds) |

Details: `investigations/`.

---

## Key learnings

- A namespace does not rewrite a leading slash. Launching under `-r __ns:=/r1` turns `"cmd_vel"` into `"/r1/cmd_vel"`, while `"/cmd_vel"` stays global `"/cmd_vel"`. Single-robot code written with leading slashes breaks the moment Robot 2 boots.
- TF frames are strings inside message payloads, not ROS topic names. Even when `/tf` is shared across the fleet, `child_frame_id` must be distinct per robot (`r1/base_link`, `r2/base_link`, `r3/base_link`), or every robot overwrites the same `map → base_link` transform.
- Topic isolation and task allocation solve two different failures. Isolation (A → B) stops robots from driving each other's wheels (`14.840 m` of cross-talk down to clean trajectories). Allocation (B → C) stops three isolated robots from piling onto the same target (`min_pair_sep_m` from `0.033 m` up to `2.479 m`, fleet travel from `7.091 m` down to `1.464 m`).
- Honest scope: these robots use a 2D kinematic integrator and Euclidean distance bidding without inter-robot local obstacle avoidance or dynamic task preemption. On physical Nav2 fleets, each `/rN` namespace also isolates costmaps, action servers (`/rN/navigate_to_pose`), and lifecycle managers (or per-robot `/rN/tf` remaps).

---

## 30-Day Capstone Arc

- **Days 01–10 (Core Graph):** DDS discovery without a master, modular nodes, backpressure, topics/services/actions, QoS, executors, parameters, and `ros2 launch`.
- **Days 11–18 (Body & Estimation):** URDF/Xacro, TF2 frames, `robot_state_publisher`, Gazebo teleop, noisy sensors, wheel odometry, PID control, and EKF fusion.
- **Days 19–26 (Autonomy & Mission):** LiDAR SLAM, AMCL localization, Nav2 pipeline, costmaps, Dijkstra vs A*, dynamic obstacles, Behavior Trees, and mission FSMs.
- **Days 27–30 (Perception, Edge & Fleet):** YOLOv8 perception topics, camera-pixel-to-map TF projection, micro-ROS serial bridging, and multi-robot namespace + coordinator scaling.
