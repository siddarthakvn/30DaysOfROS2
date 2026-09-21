# Day 08 — Executors and Blocking Callbacks

> **Engineering Question**
>
> **What happens to an entire ROS 2 node when one callback takes too long?**
>
> *(Concrete: Your LiDAR callback takes 500 ms. Your IMU needs 10 ms. Does the IMU still run?)*

---

## The story

Day 07 showed matched discovery is not enough — QoS can silence a topic.

Day 08 asks the next trap:

> Publisher and subscriber match. Messages arrive. Middleware is healthy.
> Then **one callback sleeps for 500 ms**.
> Does the rest of the node keep living?

On a robot that usually means:

| Callback | Need |
|---|---|
| IMU | every **10 ms** |
| Control timer | every **20 ms** |
| LiDAR | occasionally **500 ms** of work |
| Camera | 30 FPS (same fate if it shares the executor/group) |

The failure mode is not “DDS broke.”
It is **callback starvation**: ready work waits while one callback owns the executor thread and/or a mutually exclusive callback group.

---

## Objective

Prove three engineering facts:

1. **SingleThreadedExecutor** — a long callback delays other callbacks on that executor
2. **MultiThreadedExecutor alone is not enough** — a shared MutuallyExclusive group still serializes
3. **Separate callback groups + MultiThreaded** — unrelated callbacks can run during the slow one

---

## Environment

| | |
|---|---|
| OS | Ubuntu 22.04 LTS |
| ROS 2 | Humble Hawksbill |
| RMW (pinned) | `rmw_fastrtps_cpp` (Fast DDS) |
| Domain | `ROS_DOMAIN_ID=80` |
| Scope | One host (localhost) |

### Pin middleware (every terminal)

```bash
cd day08-executors/ros2_nodes
source ./env.sh
ros2 daemon stop
```

---

## Hypotheses

| ID | Prediction |
|---|---|
| **H1** | SingleThreaded + long LiDAR callback → IMU/control `during_lidar ≈ 0`, large `max_gap_ms` |
| **H2/H3** | MultiThreaded + **shared** MutEx group → still serialized (`during_lidar ≈ 0`) |
| **H4** | MultiThreaded + **separate** MutEx groups → IMU/control run during LiDAR (`during_lidar >> 0`) |
| **H5** | LiDAR callback duration stays ≈ 500 ms in all modes (threads do not shrink the work) |
| **H6** | Starvation happens with matched QoS / healthy topics (processing capacity failure) |

---

## Investigations

| ID | Title | File |
|---|---|---|
| **A** | SingleThreaded starvation | [investigations/A-single-threaded-starvation.md](investigations/A-single-threaded-starvation.md) |
| **B** | MultiThreaded + shared MutEx | [investigations/B-multithreaded-shared-group.md](investigations/B-multithreaded-shared-group.md) |
| **C** | MultiThreaded + separate groups (hero) | [investigations/C-separate-callback-groups.md](investigations/C-separate-callback-groups.md) |

Automated evidence: `./run_smoke.sh` → `assets/A.log`, `B.log`, `C.log`, `comparison.txt`.

---

## Nodes

| Node | Role |
|---|---|
| `lidar_pub.py` | Publishes scan ids on `/day08/lidar` after warmup |
| `busy_robot_node.py` | IMU timer (10 ms), control timer (20 ms), LiDAR sub that `sleep`s `lidar_block_ms` |

### Parameters (`busy_robot_node.py`)

| Param | Meaning |
|---|---|
| `executor` | `single` or `multi` |
| `num_threads` | MultiThreaded pool size |
| `group_mode` | `default` / `shared_mutex` / `separate_mutex` / `reentrant` |
| `lidar_block_ms` | Artificial LiDAR work (default 500) |
| `run_sec` | Experiment duration |

`SUMMARY` reports IMU/control gaps, `during_lidar` counts, and `max_active_callbacks`.

---

## Reproduction (quick start — Investigation C hero)

```bash
cd day08-executors/ros2_nodes
source ./env.sh
ros2 daemon stop

# Terminal 1
python3 lidar_pub.py --ros-args -p period_sec:=1.5 -p warmup_sec:=1.0 -p count:=4

# Terminal 2
python3 busy_robot_node.py --ros-args \
  -p executor:=multi -p num_threads:=4 -p group_mode:=separate_mutex \
  -p lidar_block_ms:=500 -p run_sec:=8.0
```

Or run all three:

```bash
cd day08-executors
./run_smoke.sh
```

---

## Key learnings

- The **executor** invokes callbacks — not the node.
- Messages wait in **middleware** until a callback takes them (Day 03/07 history still applies).
- **SingleThreaded** → one slow callback can freeze the whole executor’s responsiveness.
- **MultiThreaded** without group design often changes nothing (default group is MutuallyExclusive).
- **Callback groups** decide who may overlap; threads only supply capacity.
- Multi-threading does **not** make a callback non-blocking.

---

## Bridge to other days

| Day | Link |
|---|---|
| **02** | Node ≠ process; shared executor = shared scheduling fate |
| **03** | Pub faster than process → backlog/staleness |
| **07** | QoS mismatch → silence |
| **08** | Matched QoS + blocked callback → starvation |

---

## Interview one-liner

**DDS can deliver the message. The executor decides whether anyone is free to handle it — and callback groups decide who may run at the same time.**

---

## Tomorrow

Can I tune a robot without restarting its ROS 2 nodes? (Parameters)
