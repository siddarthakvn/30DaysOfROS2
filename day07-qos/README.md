# Day 07 — QoS Compatibility (Silent Failure)

> **Engineering Question**
>
> **Can the wrong QoS policy silently break a robotic system?**
>
> *(Alternate: Why can two ROS 2 nodes be connected, yet messages still never arrive?)*

---

## The story

Day 01 showed nodes can **find** each other without a Master.
Day 03 showed a **matched** topic can still bury you in stale data.

Day 07 asks the gate in between:

> After discovery, under what conditions are endpoints **allowed** to exchange data?

Publisher alive. Subscriber alive. Topic in the graph. Publishing continues.
And the callback stays quiet — because **QoS did not match**.

This is not “connect then drop packets.”
It is usually **no data path at all**.

---

## Objective

Prove QoS is a **communication contract**:

1. Compatible offer/request → messages flow
2. Reliability mismatch → endpoints can be visible, receives stay at **0**
3. Durability controls late-join behavior (and can also block matching)

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble Hawksbill |
| RMW (pinned) | `rmw_fastrtps_cpp` (Fast DDS) |
| Domain | `ROS_DOMAIN_ID=70` |
| Scope | One host (localhost) |

### Pin middleware (every terminal)

```bash
cd day07-qos/ros2_nodes
source ./env.sh
ros2 daemon stop
```

---

## Hypotheses

| ID | Prediction |
|---|---|
| **H1** | Compatible RELIABLE + VOLATILE both sides → `recv_total` increases. |
| **H2** | BEST_EFFORT pub + RELIABLE sub → topic/endpoints visible, `recv_total` stays 0. |
| **H3** | Changing only the subscriber reliability to BEST_EFFORT restores flow. |
| **H4** | VOLATILE pub + TRANSIENT_LOCAL sub → no communication. |
| **H5** | Dual TRANSIENT_LOCAL can deliver retained samples to a late joiner (within depth). |

---

## Investigations

| ID | Title | File |
|---|---|---|
| **A** | Compatible baseline | [investigations/A-compatible-flow.md](investigations/A-compatible-flow.md) |
| **B** | Reliability mismatch (hero) | [investigations/B-reliability-mismatch.md](investigations/B-reliability-mismatch.md) |
| **C** | Durability + late join | [investigations/C-durability-late-join.md](investigations/C-durability-late-join.md) |

Scripts: `ros2_nodes/run_A.sh`, `run_B.sh`, `run_C.sh`.

---

## Nodes

| Node | Role |
|---|---|
| `qos_pub.py` | Publishes `std_msgs/Int32` seq on `/qos_demo/stream` |
| `qos_sub.py` | Counts receives; reports `recv_total` / `last_seq` |
| `qos_utils.py` | Builds KEEP_LAST + reliability + durability |

---

## Reproduction (quick start — Investigation B hero)

```bash
cd day07-qos/ros2_nodes
source ./env.sh
ros2 daemon stop

# Terminal 1 — sensor-style publisher
python3 qos_pub.py --ros-args \
  -p reliability:=best_effort -p durability:=volatile

# Terminal 2 — default-ish reliable subscriber (MISMATCH)
python3 qos_sub.py --ros-args \
  -p reliability:=reliable -p durability:=volatile

# Terminal 3
ros2 topic info /qos_demo/stream --verbose
```

Watch for: PUB `seq` climbing, SUB `recv_total=0`, verbose QoS showing the bad pair.

Then fix Terminal 2:

```bash
python3 qos_sub.py --ros-args \
  -p reliability:=best_effort -p durability:=volatile
```

---

## Key learnings

- Discovery ≠ delivery. QoS matching sits between them.
- Incompatible reliability/durability → **no connection**, not a lossy connection.
- `ros2 topic list` is not proof of communication; use `ros2 topic info --verbose`.
- Choose QoS from **data meaning** (fresh sensor stream vs command/state), not “always RELIABLE.”

---

## Bridge to other days

| Day | Link |
|---|---|
| **01** | Nodes find each other |
| **03** | Matched QoS + overload → staleness |
| **07** | Mismatched QoS → silence |
| **08** | Even with matched QoS, a blocked callback can freeze the node |

---

## Interview one-liner

**Discovery finds the nodes. QoS decides whether they are allowed to exchange data.**
